"""
Main script for Clinical NLP Assignment - Medical Code Extraction

Usage:
    python main.py [--pdf_path <path_to_pdf>]
    
Example:
    python main.py --pdf_path "../Input data for Assignment.pdf"
    python main.py  # Uses default path from config.py
"""
import sys
import os
import argparse
import json

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from vector_db import CodeVectorDB
from extractor import ClinicalReportExtractor
import config
import utils


def build_vector_databases(vector_db):
    """Build or load vector databases for ICD and CPT codes"""
    icd_db_path = os.path.join(config.VECTOR_DB_DIR, 'icd_vector_db.pkl')
    cpt_db_path = os.path.join(config.VECTOR_DB_DIR, 'cpt_vector_db.pkl')
    
    if not os.path.exists(icd_db_path):
        print("[INFO] Building ICD vector database (this may take a few minutes)...")
        icd_count = vector_db.build_icd_database()
        print(f"[SUCCESS] Processed {icd_count} ICD codes\n")
    else:
        print("[INFO] Loading existing ICD database...")
        vector_db.load_icd_database()
        print(f"[SUCCESS] Loaded {len(vector_db.icd_codes)} ICD codes\n")
    
    if not os.path.exists(cpt_db_path):
        print("[INFO] Building CPT vector database (this may take a few minutes)...")
        cpt_count = vector_db.build_cpt_database()
        print(f"[SUCCESS] Processed {cpt_count} CPT codes\n")
    else:
        print("[INFO] Loading existing CPT database...")
        vector_db.load_cpt_database()
        print(f"[SUCCESS] Loaded {len(vector_db.cpt_codes)} CPT codes\n")


def split_reports(text):
    """Split text into individual clinical reports"""
    import re
    # Split on multiple blank lines
    reports = re.split(r'\n\n\n+', text)
    # Filter out very short segments (likely not reports)
    reports = [r.strip() for r in reports if len(r.strip()) > 200]
    return reports


def main(pdf_path=None):
    """Main extraction function"""
    print("="*80)
    print("Clinical NLP Assignment - Medical Code Extraction")
    print("="*80)
    
    # Check for Gemini API key
    if config.USE_GEMINI:
        if not config.GEMINI_API_KEY:
            print("\n[WARNING] GEMINI_API_KEY not set. Using regex extraction only.")
            print("[INFO] Set environment variable:")
            print("       Windows PowerShell: $env:GEMINI_API_KEY='your-api-key'")
            print("       Windows CMD: set GEMINI_API_KEY=your-api-key")
            print("       Or set it in config.py directly")
            print()
        else:
            print(f"\n[INFO] Gemini API enabled (Model: {config.GEMINI_MODEL})")
    
    # Use provided path or default from config
    if pdf_path:
        input_pdf = pdf_path
    else:
        input_pdf = config.INPUT_DATA_PDF
    
    # Validate PDF path
    if not os.path.exists(input_pdf):
        print(f"\n[ERROR] PDF file not found at: {input_pdf}")
        print(f"[INFO] Please provide a valid PDF path using --pdf_path argument")
        return
    
    print(f"\n[INFO] Input PDF: {input_pdf}")
    
    # Step 1: Build/Load Vector Databases
    print("\n[STEP 1] Building/Loading Vector Databases...")
    vector_db = CodeVectorDB()
    build_vector_databases(vector_db)
    
    # Step 2: Initialize Extractor
    print("[STEP 2] Initializing Clinical Report Extractor...")
    extractor = ClinicalReportExtractor()
    
    # Step 3: Extract text from PDF
    print(f"\n[STEP 3] Reading PDF...")
    clinical_text = extractor.extract_from_pdf(input_pdf)
    print(f"[SUCCESS] Extracted {len(clinical_text)} characters from PDF")
    
    # Step 4: Split Reports
    print("\n[STEP 4] Processing Reports...")
    reports = split_reports(clinical_text)
    
    if len(reports) == 0:
        reports = [clinical_text]
        print("[INFO] Processing as single report")
    else:
        print(f"[INFO] Found {len(reports)} report(s)")
    
    # Step 5: Extract Data
    print("\n[STEP 5] Extracting Structured Data...")
    extracted_data = []
    
    for i, report_text in enumerate(reports[:4], 1):  # Process up to 4 reports
        print(f"  Processing Report {i}...", end=" ")
        try:
            # Extract in required format
            formatted_data = extractor.extract_to_required_format(report_text, report_id=f"report_{i}")
            extracted_data.append(formatted_data)
            print(f"[OK] (ICD: {len(formatted_data['ICD-10'])}, CPT: {len(formatted_data['CPT'])})")
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
    
    # Step 6: Save Results
    print(f"\n[STEP 6] Saving Results...")
    output_file = config.JSON_OUTPUT_FILE
    
    # Save JSON output
    if len(extracted_data) == 1:
        # If single report, save as single object (not array)
        utils.save_json(extracted_data[0], output_file)
    else:
        # If multiple reports, save as array
        utils.save_json(extracted_data, output_file)
    
    print(f"[SUCCESS] Results saved to: {output_file}")
    print(f"[INFO] File size: {os.path.getsize(output_file)} bytes")
    
    # Display summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    for i, data in enumerate(extracted_data, 1):
        print(f"\nReport {i}:")
        print(f"  Clinical Terms: {len(data['Clinical Terms'])}")
        print(f"  Anatomical Locations: {len(data['Anatomical Locations'])}")
        print(f"  Diagnosis: {len(data['Diagnosis'])}")
        print(f"  Procedures: {len(data['Procedures'])}")
        print(f"  ICD-10 Codes: {len(data['ICD-10'])} - {', '.join(data['ICD-10'][:5])}" + 
              (f"..." if len(data['ICD-10']) > 5 else ""))
        print(f"  CPT Codes: {len(data['CPT'])} - {', '.join(data['CPT'])}")
        print(f"  HCPCS Codes: {len(data['HCPCS'])} - {', '.join(data['HCPCS']) if data['HCPCS'] else 'None'}")
    
    print("\n" + "="*80)
    print("[SUCCESS] Extraction Complete!")
    print("="*80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract medical codes from clinical reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --pdf_path "../Input data for Assignment.pdf"
  python main.py --pdf_path "C:/path/to/clinical_report.pdf"
        """
    )
    
    parser.add_argument(
        '--pdf_path',
        type=str,
        default=None,
        help='Path to the PDF file containing clinical reports (default: uses config.INPUT_DATA_PDF)'
    )
    
    args = parser.parse_args()
    
    try:
        main(pdf_path=args.pdf_path)
    except KeyboardInterrupt:
        print("\n\n[INFO] Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

