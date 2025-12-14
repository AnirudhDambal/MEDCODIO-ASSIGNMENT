"""
Utility functions for Clinical NLP Assignment
"""
import re
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any
import json

def clean_text(text: str) -> str:
    """Clean and preprocess clinical text"""
    if not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation for clinical terms
    text = text.strip()
    return text

def extract_sections(text: str) -> Dict[str, str]:
    """Extract common sections from clinical reports"""
    sections = {
        'chief_complaint': '',
        'history_of_present_illness': '',
        'review_of_systems': '',
        'physical_examination': '',
        'assessment_and_plan': '',
        'procedures': '',
        'diagnoses': ''
    }
    
    text_lower = text.lower()
    
    # Common section headers
    patterns = {
        'chief_complaint': r'(?:chief complaint|cc):?\s*(.+?)(?=\n\n|\nhistory|$)',
        'history_of_present_illness': r'(?:history of present illness|hpi):?\s*(.+?)(?=\n\n|\nreview|$)',
        'review_of_systems': r'(?:review of systems|ros):?\s*(.+?)(?=\n\n|\nphysical|$)',
        'physical_examination': r'(?:physical examination|pe|exam):?\s*(.+?)(?=\n\n|\nassessment|$)',
        'assessment_and_plan': r'(?:assessment and plan|a&p|assessment):?\s*(.+?)(?=\n\n|\nprocedure|$)',
        'procedures': r'(?:procedure[s]?|procedures performed):?\s*(.+?)(?=\n\n|\ndiagnosis|$)',
        'diagnoses': r'(?:diagnosis|diagnoses|final diagnosis):?\s*(.+?)(?=\n\n|$)'
    }
    
    for section, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sections[section] = clean_text(match.group(1))
    
    return sections

def extract_clinical_entities(text: str) -> Dict[str, List[str]]:
    """Extract clinical entities like diagnoses, procedures, medications"""
    entities = {
        'diagnoses': [],
        'procedures': [],
        'medications': [],
        'body_parts': []
    }
    
    # Common diagnosis patterns
    diagnosis_patterns = [
        r'(?:diagnosis|diagnoses|dx):\s*([^.\n]+)',
        r'(?:icd[-\s]?10[:\s]+)([A-Z]\d{2}(?:\.\d+)?)',
        r'([A-Z]\d{2}(?:\.\d+)?)',  # ICD-10 format codes in text
    ]
    
    # Common procedure patterns
    procedure_patterns = [
        r'(?:procedure|procedure code|cpt):\s*([^.\n]+)',
        r'(?:cpt[-\s]?code[:\s]+)(\d{5})',
        r'(\d{5})',  # 5-digit CPT codes
    ]
    
    for pattern in diagnosis_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities['diagnoses'].extend([clean_text(m) for m in matches])
    
    for pattern in procedure_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities['procedures'].extend([clean_text(m) for m in matches])
    
    # Remove duplicates while preserving order
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))
    
    return entities

def load_excel_data(file_path: str) -> pd.DataFrame:
    """Load data from Excel file"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

def save_json(data: Dict[str, Any], file_path: str):
    """Save data to JSON file with proper formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(file_path: str) -> Dict[str, Any]:
    """Load data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

