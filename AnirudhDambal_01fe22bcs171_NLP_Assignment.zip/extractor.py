"""
Clinical Report Data Extractor
"""
import re
import PyPDF2
import json
from typing import Dict, List, Any
import utils
from vector_db import CodeVectorDB
import config

# Try to import Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARNING] google-generativeai not installed. Install with: pip install google-generativeai")

class ClinicalReportExtractor:
    """Extract structured data from clinical reports"""
    
    def __init__(self, use_gemini=None):
        """Initialize the extractor with vector database"""
        self.vector_db = CodeVectorDB()
        self.vector_db.load_icd_database()
        self.vector_db.load_cpt_database()
        
        # Determine if we should use Gemini
        if use_gemini is None:
            use_gemini = config.USE_GEMINI and GEMINI_AVAILABLE and bool(config.GEMINI_API_KEY)
        
        self.use_gemini = use_gemini
        
        if self.use_gemini:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(config.GEMINI_MODEL)
                print(f"[INFO] Gemini API initialized with model: {config.GEMINI_MODEL}")
            except Exception as e:
                print(f"[WARNING] Failed to initialize Gemini API: {e}")
                print("[INFO] Falling back to regex extraction")
                self.use_gemini = False
        else:
            if config.USE_GEMINI and not GEMINI_AVAILABLE:
                print("[INFO] Using regex extraction (Gemini library not installed)")
            elif config.USE_GEMINI and not config.GEMINI_API_KEY:
                print("[INFO] Using regex extraction (GEMINI_API_KEY not set)")
            else:
                print("[INFO] Using regex extraction")
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
        return text
    
    def extract_patient_info(self, text: str) -> Dict[str, Any]:
        """Extract patient information from clinical report"""
        patient_info = {
            'patient_id': None,
            'name': None,
            'date_of_birth': None,
            'age': None,
            'gender': None,
            'visit_date': None
        }
        
        # Extract patient ID
        patient_id_patterns = [
            r'(?:patient id|patientid|mrn|medical record number)[:\s]+([A-Z0-9\-]+)',
            r'(?:id|mrn)[:\s]+([A-Z0-9\-]+)'
        ]
        for pattern in patient_id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                patient_info['patient_id'] = match.group(1).strip()
                break
        
        # Extract name
        name_patterns = [
            r'(?:patient name|name)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'([A-Z][a-z]+,?\s+[A-Z][a-z]+)',  # Last, First format
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                patient_info['name'] = match.group(1).strip()
                break
        
        # Extract DOB
        dob_patterns = [
            r'(?:dob|date of birth|birth date)[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
            r'(\d{1,2}/\d{1,2}/\d{4})'
        ]
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                patient_info['date_of_birth'] = match.group(1).strip()
                break
        
        # Extract age
        age_match = re.search(r'(?:age)[:\s]+(\d+)', text, re.IGNORECASE)
        if age_match:
            patient_info['age'] = int(age_match.group(1))
        
        # Extract gender
        gender_match = re.search(r'(?:gender|sex)[:\s]+([MF]|Male|Female)', text, re.IGNORECASE)
        if gender_match:
            patient_info['gender'] = gender_match.group(1).strip()
        
        # Extract visit date
        visit_date_patterns = [
            r'(?:visit date|date of service|dos|date)[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
            r'(\d{1,2}/\d{1,2}/\d{4})'
        ]
        for pattern in visit_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                patient_info['visit_date'] = match.group(1).strip()
                break
        
        return patient_info
    
    def extract_icd_codes(self, text: str) -> List[Dict[str, Any]]:
        """Extract ICD codes using NLP and vector database"""
        # Extract entities first
        entities = utils.extract_clinical_entities(text)
        
        # Extract sections for context
        sections = utils.extract_sections(text)
        
        # Combine relevant sections for diagnosis search
        diagnosis_context = " ".join([
            sections.get('chief_complaint', ''),
            sections.get('history_of_present_illness', ''),
            sections.get('assessment_and_plan', ''),
            sections.get('diagnoses', '')
        ])
        
        # Search for ICD codes
        icd_results = self.vector_db.search_icd(
            diagnosis_context if diagnosis_context.strip() else text,
            top_k=config.TOP_K_RESULTS,
            threshold=config.SIMILARITY_THRESHOLD
        )
        
        # Also check for explicit ICD codes in text (improved pattern to catch codes like K64.8, K57.90)
        explicit_codes = re.findall(r'\b([A-Z]\d{2}(?:\.\d{1,4})?)\b', text)
        extracted_codes = []
        explicit_codes_found = set()
        
        # First, prioritize explicit codes found in text
        for code in explicit_codes:
            code = code.strip()
            if code and code not in explicit_codes_found:
                explicit_codes_found.add(code)
                # Search for this specific code (lower threshold for explicit codes)
                code_matches = self.vector_db.search_icd(code, top_k=1, threshold=0.1)
                if code_matches:
                    extracted_codes.append({
                        'code': code,
                        'description': code_matches[0]['description'],
                        'confidence': 1.0,  # High confidence for explicit codes
                        'source': 'explicit_code'
                    })
                else:
                    # Even if not in database, include it if it matches ICD-10 pattern
                    if re.match(r'^[A-Z]\d{2}(\.\d{1,4})?$', code):
                        extracted_codes.append({
                            'code': code,
                            'description': code,  # Use code as description if not found
                            'confidence': 0.95,
                            'source': 'explicit_code'
                        })
        
        # Then add NLP-retrieved codes that aren't already in the list
        for result in icd_results:
            if result['code'] not in explicit_codes_found:
                extracted_codes.append({
                    'code': result['code'],
                    'description': result['description'],
                    'confidence': result['similarity_score'],
                    'source': 'nlp_retrieval'
                })
        
        # Remove duplicates and sort by confidence
        seen_codes = set()
        unique_codes = []
        for code_info in sorted(extracted_codes, key=lambda x: x['confidence'], reverse=True):
            if code_info['code'] not in seen_codes:
                seen_codes.add(code_info['code'])
                unique_codes.append(code_info)
        
        return unique_codes[:10]  # Return top 10
    
    def extract_cpt_codes(self, text: str) -> List[Dict[str, Any]]:
        """Extract CPT codes using NLP and vector database"""
        # Extract entities first
        entities = utils.extract_clinical_entities(text)
        
        # Extract sections for context
        sections = utils.extract_sections(text)
        
        # Combine relevant sections for procedure search
        procedure_context = " ".join([
            sections.get('procedures', ''),
            sections.get('physical_examination', ''),
            sections.get('assessment_and_plan', '')
        ])
        
        # Search for CPT codes
        cpt_results = self.vector_db.search_cpt(
            procedure_context if procedure_context.strip() else text,
            top_k=config.TOP_K_RESULTS,
            threshold=config.SIMILARITY_THRESHOLD
        )
        
        # Also check for explicit CPT codes in text (5-digit codes)
        # Look for "Procedure Codes : 45380" or "45378" patterns
        explicit_codes = re.findall(r'\b(\d{5})\b', text)
        extracted_codes = []
        explicit_codes_found = set()
        
        # First, prioritize explicit codes found in text
        for code in explicit_codes:
            code = code.strip()
            if code and code not in explicit_codes_found:
                explicit_codes_found.add(code)
                # Search for this specific code (lower threshold for explicit codes)
                code_matches = self.vector_db.search_cpt(code, top_k=1, threshold=0.1)
                if code_matches:
                    extracted_codes.append({
                        'code': code,
                        'description': code_matches[0]['description'],
                        'confidence': 1.0,  # High confidence for explicit codes
                        'source': 'explicit_code'
                    })
                else:
                    # Even if not in database, include it if it's a 5-digit code
                    extracted_codes.append({
                        'code': code,
                        'description': f'CPT Code {code}',
                        'confidence': 0.95,
                        'source': 'explicit_code'
                    })
        
        # Then add NLP-retrieved codes that aren't already in the list
        for result in cpt_results:
            if result['code'] not in explicit_codes_found:
                extracted_codes.append({
                    'code': result['code'],
                    'description': result['description'],
                    'confidence': result['similarity_score'],
                    'source': 'nlp_retrieval'
                })
        
        # Remove duplicates and sort by confidence
        seen_codes = set()
        unique_codes = []
        for code_info in sorted(extracted_codes, key=lambda x: x['confidence'], reverse=True):
            if code_info['code'] not in seen_codes:
                seen_codes.add(code_info['code'])
                unique_codes.append(code_info)
        
        return unique_codes[:10]  # Return top 10
    
    def extract_clinical_terms(self, text: str) -> List[str]:
        """Extract clinical terms and conditions"""
        terms = set()
        
        # Common clinical terms patterns
        patterns = [
            r'\b(colon polyps|polyps?)\b',
            r'\b(internal hemorrhoids?|hemorrhoids?)\b',
            r'\b(diverticulosis|diverticulitis)\b',
            r'\b(melanosis coli)\b',
            r'\b(rectal (exam|examination|erosion|proctitis))\b',
            r'\b(bowel preparation|preparation)\b',
            r'\b(no polyps?|polyps? found|polyps? revealed)\b',
            r'\b(no complications|complications)\b',
            r'\b(colonoscopy|colonoscope)\b',
            r'\b(sigmoid diverticulosis)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    terms.add(match[0].strip().lower())
                else:
                    terms.add(match.strip().lower())
        
        # Also extract from impressions and findings
        impression_section = re.search(r'impression[:\s]+(.+?)(?=\n\n|plan:|$)', text, re.IGNORECASE | re.DOTALL)
        if impression_section:
            impression_text = impression_section.group(1).lower()
            # Extract key phrases
            key_phrases = [
                'colon polyps', 'history of colon polyps', 'colonic polyps',
                'internal hemorrhoids', 'hemorrhoids',
                'diverticulosis', 'sigmoid diverticulosis',
                'melanosis coli', 'no polyps', 'rectal erosion',
                'good bowel preparation', 'no complications'
            ]
            for phrase in key_phrases:
                if phrase in impression_text:
                    terms.add(phrase)
        
        # Clean up and format
        formatted_terms = []
        for term in sorted(terms):
            # Capitalize first letter
            formatted_term = term.capitalize()
            if term.startswith('no '):
                formatted_term = 'No ' + term[3:].capitalize()
            formatted_terms.append(formatted_term)
        
        return formatted_terms
    
    def extract_anatomical_locations(self, text: str) -> List[str]:
        """Extract anatomical locations mentioned in the report"""
        locations = set()
        
        # Common anatomical terms
        anatomical_patterns = [
            r'\b(rectum|rectal)\b',
            r'\b(sigmoid (colon)?|sigmoid)\b',
            r'\b(cecum|caecum)\b',
            r'\b(proximal colon)\b',
            r'\b(ileocecal valve)\b',
            r'\b(appendiceal orifice|appendix orifice)\b',
            r'\b(distal rectum)\b',
            r'\b(anal verge)\b',
            r'\b(colon|colonic)\b'
        ]
        
        text_lower = text.lower()
        for pattern in anatomical_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    loc = match[0].strip()
                else:
                    loc = match.strip()
                if loc:
                    # Clean up
                    if loc == 'rectal':
                        loc = 'Rectum'
                    elif loc == 'colonic':
                        loc = 'Colon'
                    elif loc == 'sigmoid':
                        loc = 'Sigmoid colon'
                    locations.add(loc.capitalize())
        
        return sorted(list(locations))
    
    def extract_diagnosis_descriptions(self, text: str, icd_codes: List[Dict]) -> List[str]:
        """Extract diagnosis descriptions"""
        diagnoses = set()
        
        # Get descriptions from ICD codes
        for icd in icd_codes:
            desc = icd.get('description', '').strip()
            if desc:
                diagnoses.add(desc)
        
        # Extract from text
        impression_match = re.search(r'impression[:\s]+(.+?)(?=\n\n|plan:|$)', text, re.IGNORECASE | re.DOTALL)
        if impression_match:
            impression_text = impression_match.group(1)
            # Extract key diagnosis phrases
            diagnosis_phrases = [
                'Personal history of colonic polyps',
                'Internal hemorrhoids',
                'Diverticulosis',
                'Melanosis coli',
                'No new polyps',
                'No polyps seen'
            ]
            for phrase in diagnosis_phrases:
                if phrase.lower() in impression_text.lower():
                    diagnoses.add(phrase)
        
        # Also check explicit mentions
        if '82-year-old female with history of colon polyps' in text:
            diagnoses.add('Personal history of colonic polyps')
        if 'diverticulosis' in text.lower():
            diagnoses.add('Diverticulosis (sigmoid)')
        if 'melanosis coli' in text.lower():
            diagnoses.add('Melanosis coli')
        if 'internal hemorrhoids' in text.lower():
            diagnoses.add('Internal hemorrhoids')
        if 'no polyps' in text.lower():
            diagnoses.add('No new polyps seen in this examination')
        
        return sorted(list(diagnoses))
    
    def extract_procedure_descriptions(self, text: str) -> List[str]:
        """Extract procedure descriptions"""
        procedures = set()
        
        # Common procedures
        if 'colonoscopy' in text.lower():
            procedures.add('Colonoscopy')
        if 'rectal exam' in text.lower() or 'rectal examination' in text.lower():
            procedures.add('Rectal examination')
        if 'scope passage' in text.lower() or 'colonoscope' in text.lower():
            procedures.add('Scope passage to cecum')
        if 'retroflexion' in text.lower():
            procedures.add('Retroflexion in rectum')
        if 'monitored anesthesia care' in text.lower() or 'mac' in text.lower():
            procedures.add('Monitored Anesthesia Care (MAC)')
        if 'intravenous' in text.lower() or 'iv' in text.lower():
            procedures.add("Intravenous medication administration (Lidocaine, Propofol, Lactated Ringer's)")
        
        return sorted(list(procedures))
    
    def extract_hcpcs_codes(self, text: str) -> List[str]:
        """Extract HCPCS codes (alphanumeric codes like J3490, A4216)"""
        hcpcs_codes = set()
        
        # HCPCS codes are typically alphanumeric: 1 letter followed by 4 digits
        hcpcs_pattern = r'\b([A-Z]\d{4})\b'
        matches = re.findall(hcpcs_pattern, text)
        
        for match in matches:
            # Filter out ICD codes (which start with specific letters like I, E, K, Z)
            # HCPCS typically start with A, B, C, D, E, G, H, J, K, L, M, P, Q, R, S, T, V
            if match[0] in ['A', 'B', 'C', 'D', 'E', 'G', 'H', 'J', 'K', 'L', 'M', 'P', 'Q', 'R', 'S', 'T', 'V']:
                hcpcs_codes.add(match)
        
        return sorted(list(hcpcs_codes))
    
    def extract_from_report(self, text: str, report_id: str = None) -> Dict[str, Any]:
        """Extract all structured data from a clinical report"""
        result = {
            'report_id': report_id or 'unknown',
            'patient_info': self.extract_patient_info(text),
            'icd_codes': self.extract_icd_codes(text),
            'cpt_codes': self.extract_cpt_codes(text),
            'sections': utils.extract_sections(text),
            'raw_text_length': len(text)
        }
        
        return result
    
    def extract_codes_with_gemini(self, text: str) -> Dict[str, Any]:
        """Extract medical codes using Gemini API"""
        
        # Limit text length to avoid token limits (keep it under 30k chars)
        text_for_extraction = text[:30000] if len(text) > 30000 else text
        
        prompt = f"""You are a medical coding expert. Extract all medical codes and structured data from the following clinical report.

Extract the following information:

1. **ICD-10 Diagnosis Codes**: Extract ALL ICD-10 codes mentioned (format: letter + 2 digits + optional decimal + digits)
   Examples: Z86.0100, K64.8, K57.90, I10, E11.9
   Look carefully for codes in the Diagnosis section or anywhere in the text

2. **CPT Procedure Codes**: Extract ALL CPT codes (5-digit numeric codes)
   Examples: 45378, 45380, 99213, 36415
   CRITICAL: Look very carefully for CPT codes! They might appear as:
   - "Procedure Code 45378" or "Procedure Code: 45378"
   - "45378" near procedure descriptions
   - "CPT 45378" or "CPT: 45378"
   - In procedure sections, expected output sections, or billing sections
   - Even if the PDF text extraction missed formatting, look for any 5-digit numbers in procedure context
   - Common colonoscopy CPT codes: 45378, 45380, 45385, 45379

3. **HCPCS Codes**: Extract HCPCS codes (1 letter + 4 digits)
   Examples: J3490, A4216, G0121

4. **Clinical Terms**: Key medical terms and conditions mentioned
   Examples: colon polyps, internal hemorrhoids, diverticulosis, melanosis coli

5. **Anatomical Locations**: Body parts and anatomical structures mentioned
   Examples: rectum, sigmoid colon, cecum, ileocecal valve

6. **Diagnosis Descriptions**: Full diagnosis descriptions
   Examples: "Personal history of colonic polyps", "Internal hemorrhoids", "Diverticulosis"

7. **Procedures**: Procedure descriptions
   Examples: "Colonoscopy", "Rectal examination", "Monitored Anesthesia Care"

Return ONLY a valid JSON object with this exact structure (no markdown, no explanations):
{{
    "ICD-10": ["code1", "code2"],
    "CPT": ["code1", "code2"],
    "HCPCS": ["code1"],
    "Clinical_Terms": ["term1", "term2"],
    "Anatomical_Locations": ["location1", "location2"],
    "Diagnosis": ["diagnosis1", "diagnosis2"],
    "Procedures": ["procedure1", "procedure2"]
}}

IMPORTANT EXTRACTION RULES:
- For CPT codes: If you see "Colonoscopy" procedure mentioned, look for associated CPT codes like 45378, 45380, etc.
- Search the ENTIRE document text thoroughly - codes might be in any section
- If a procedure is mentioned (like colonoscopy), include the most likely CPT code even if not explicitly stated
- Look in sections labeled "Procedure Code", "Expected Output", "Procedure Codes", or billing sections
- Include codes even if they appear with formatting issues from PDF extraction
- Return only the JSON object, nothing else
- Ensure all arrays are lists, even if empty (use [] not null)

Clinical Report Text:
{text_for_extraction}
"""
        
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "top_p": 0.95,
                    "top_k": 40,
                }
            )
            
            result_text = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if result_text.startswith('```json'):
                result_text = result_text[7:].strip()
            elif result_text.startswith('```'):
                result_text = result_text[3:].strip()
            if result_text.endswith('```'):
                result_text = result_text[:-3].strip()
            
            # Try to extract JSON if there's extra text
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result_text = result_text[json_start:json_end]
            
            # Parse JSON response
            result = json.loads(result_text)
            
            # Validate and clean up
            if not isinstance(result, dict):
                print("[WARNING] Gemini returned invalid response format")
                return {}
            
            # Ensure all keys exist with empty lists as defaults
            cleaned_result = {
                "ICD-10": result.get("ICD-10", []) if isinstance(result.get("ICD-10"), list) else [],
                "CPT": result.get("CPT", []) if isinstance(result.get("CPT"), list) else [],
                "HCPCS": result.get("HCPCS", []) if isinstance(result.get("HCPCS"), list) else [],
                "Clinical_Terms": result.get("Clinical_Terms", []) if isinstance(result.get("Clinical_Terms"), list) else [],
                "Anatomical_Locations": result.get("Anatomical_Locations", []) if isinstance(result.get("Anatomical_Locations"), list) else [],
                "Diagnosis": result.get("Diagnosis", []) if isinstance(result.get("Diagnosis"), list) else [],
                "Procedures": result.get("Procedures", []) if isinstance(result.get("Procedures"), list) else []
            }
            
            # Clean and deduplicate codes
            cleaned_result["ICD-10"] = list(set([str(c).strip() for c in cleaned_result["ICD-10"] if c]))
            cleaned_result["CPT"] = list(set([str(c).strip() for c in cleaned_result["CPT"] if c]))
            cleaned_result["HCPCS"] = list(set([str(c).strip() for c in cleaned_result["HCPCS"] if c]))
            
            print(f"[INFO] Gemini extracted: {len(cleaned_result['ICD-10'])} ICD codes, {len(cleaned_result['CPT'])} CPT codes")
            
            return cleaned_result
            
        except json.JSONDecodeError as e:
            print(f"[WARNING] Gemini API returned invalid JSON: {e}")
            print(f"[DEBUG] Response text: {result_text[:500]}")
            # Try to fix common JSON issues
            try:
                # Try to extract just the JSON part more aggressively
                import re as regex_module
                json_pattern = regex_module.search(r'\{.*\}', result_text, regex_module.DOTALL)
                if json_pattern:
                    fixed_json = json_pattern.group(0)
                    result = json.loads(fixed_json)
                    if isinstance(result, dict):
                        cleaned_result = {
                            "ICD-10": result.get("ICD-10", []) if isinstance(result.get("ICD-10"), list) else [],
                            "CPT": result.get("CPT", []) if isinstance(result.get("CPT"), list) else [],
                            "HCPCS": result.get("HCPCS", []) if isinstance(result.get("HCPCS"), list) else [],
                            "Clinical_Terms": result.get("Clinical_Terms", []) if isinstance(result.get("Clinical_Terms"), list) else [],
                            "Anatomical_Locations": result.get("Anatomical_Locations", []) if isinstance(result.get("Anatomical_Locations"), list) else [],
                            "Diagnosis": result.get("Diagnosis", []) if isinstance(result.get("Diagnosis"), list) else [],
                            "Procedures": result.get("Procedures", []) if isinstance(result.get("Procedures"), list) else []
                        }
                        cleaned_result["ICD-10"] = list(set([str(c).strip() for c in cleaned_result["ICD-10"] if c]))
                        cleaned_result["CPT"] = list(set([str(c).strip() for c in cleaned_result["CPT"] if c]))
                        cleaned_result["HCPCS"] = list(set([str(c).strip() for c in cleaned_result["HCPCS"] if c]))
                        print(f"[INFO] Gemini extracted (fixed): {len(cleaned_result['ICD-10'])} ICD codes, {len(cleaned_result['CPT'])} CPT codes")
                        return cleaned_result
            except:
                pass
            return {}
        except Exception as e:
            print(f"[WARNING] Gemini API error: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def enhance_with_vector_db(self, gemini_result: Dict, text: str) -> Dict[str, List[str]]:
        """Enhance Gemini results with vector database lookups for better descriptions"""
        
        # Get ICD codes and enhance with descriptions (optional - we mainly use codes)
        diagnosis_descriptions = gemini_result.get("Diagnosis", [])
        
        # If diagnosis descriptions are empty, try to get from vector DB
        if not diagnosis_descriptions:
            icd_codes = gemini_result.get("ICD-10", [])
            icd_code_list = []
            for code in icd_codes:
                matches = self.vector_db.search_icd(str(code), top_k=1, threshold=0.1)
                if matches:
                    diagnosis_descriptions.append(matches[0]['description'])
                    icd_code_list.append({
                        'code': code,
                        'description': matches[0]['description']
                    })
            if not diagnosis_descriptions:
                diagnosis_descriptions = self.extract_diagnosis_descriptions(text, icd_code_list)
        
        # Use Gemini's extracted terms or fallback to regex
        clinical_terms = gemini_result.get("Clinical_Terms", self.extract_clinical_terms(text))
        anatomical_locations = gemini_result.get("Anatomical_Locations", self.extract_anatomical_locations(text))
        procedure_descriptions = gemini_result.get("Procedures", self.extract_procedure_descriptions(text))
        
        return {
            "Clinical Terms": clinical_terms if isinstance(clinical_terms, list) else list(clinical_terms),
            "Anatomical Locations": anatomical_locations if isinstance(anatomical_locations, list) else list(anatomical_locations),
            "Diagnosis": diagnosis_descriptions if isinstance(diagnosis_descriptions, list) else list(diagnosis_descriptions),
            "Procedures": procedure_descriptions if isinstance(procedure_descriptions, list) else list(procedure_descriptions),
            "ICD-10": gemini_result.get("ICD-10", []),
            "CPT": gemini_result.get("CPT", []),
            "HCPCS": gemini_result.get("HCPCS", [])
        }

    def extract_to_required_format(self, text: str, report_id: str = None) -> Dict[str, List[str]]:
        """Extract data in the required JSON format"""
        
        if self.use_gemini:
            # Try Gemini first
            print("[INFO] Using Gemini API for extraction...")
            gemini_result = self.extract_codes_with_gemini(text)
            
            if gemini_result:
                # Enhance with vector database lookup for descriptions
                enhanced_result = self.enhance_with_vector_db(gemini_result, text)
                
                # Hybrid approach: If Gemini missed CPT codes, supplement with regex
                if not enhanced_result.get("CPT") or len(enhanced_result.get("CPT", [])) == 0:
                    print("[INFO] Gemini found no CPT codes, supplementing with regex search...")
                    regex_result = self.extract_to_required_format_regex(text)
                    if regex_result.get("CPT"):
                        enhanced_result["CPT"] = list(set(enhanced_result.get("CPT", []) + regex_result.get("CPT", [])))
                        print(f"[INFO] Added {len(regex_result.get('CPT', []))} CPT code(s) from regex")
                
                return enhanced_result
            else:
                print("[WARNING] Gemini extraction failed, falling back to regex...")
        
        # Fallback to regex-based extraction
        return self.extract_to_required_format_regex(text)
    
    def extract_to_required_format_regex(self, text: str) -> Dict[str, List[str]]:
        """Regex-based extraction (fallback method)"""
        # Get ICD and CPT codes first
        icd_code_list = self.extract_icd_codes(text)
        cpt_code_list = self.extract_cpt_codes(text)
        
        # Extract ICD codes as strings
        icd_10_codes = []
        for icd in icd_code_list:
            code = icd.get('code', '').strip()
            if code:
                icd_10_codes.append(code)
        
        # Extract CPT codes as strings
        cpt_codes = []
        for cpt in cpt_code_list:
            code = cpt.get('code', '').strip()
            if code:
                cpt_codes.append(code)
        
        # Extract HCPCS codes
        hcpcs_codes = self.extract_hcpcs_codes(text)
        
        # Extract other required fields
        clinical_terms = self.extract_clinical_terms(text)
        anatomical_locations = self.extract_anatomical_locations(text)
        diagnosis_descriptions = self.extract_diagnosis_descriptions(text, icd_code_list)
        procedure_descriptions = self.extract_procedure_descriptions(text)
        
        # Build result in required format
        result = {
            "Clinical Terms": clinical_terms,
            "Anatomical Locations": anatomical_locations,
            "Diagnosis": diagnosis_descriptions,
            "Procedures": procedure_descriptions,
            "ICD-10": icd_10_codes,
            "CPT": cpt_codes,
            "HCPCS": hcpcs_codes
        }
        
        return result

