# MEDCODIO Assignment Submission

> Complete submission for Clinical NLP and Backend System Design assignments

---

## 📦 Repository Structure

```
MEDCODIO ASSIGNMENT/
│
├── clinical_nlp_assignment/        # Assignment 1: Clinical NLP
│   ├── main.py                     # Main extraction script
│   ├── Clinical_NLP_Assignment.ipynb
│   ├── extractor.py                # AI-powered extraction engine
│   ├── vector_db.py                # Vector database implementation
│   ├── config.py                   # Configuration
│   ├── requirements.txt            # Dependencies
│   ├── README.md                   # Detailed documentation
│   ├── output/                     # Generated JSON outputs
│   └── vector_db/                  # Cached embeddings
│
├── backend_system_design/          # Assignment 2: Backend Design
│   ├── ER_Diagram_and_Schema.md   # Database schema & ERD
│   ├── API_Design.md              # REST API specifications
│   ├── Design_Decisions.md        # Architecture rationale
│   └── README.md                  # Detailed documentation
│
├── ICD_code_Assignment.xlsx        # ICD-10 code reference
├── cpt_code_assignment.xlsx        # CPT code reference
├── Input data for Assignment.pdf   # Sample clinical reports
│
└── README.md                       # This file
```

---

## 📋 Assignment 1: Clinical NLP

### Overview

**Extract structured medical data from clinical reports** including:
- ICD-10 diagnosis codes
- CPT procedure codes
- Clinical terms, anatomical locations, diagnoses, and procedures

### Technology Stack

- **AI Extraction**: Google Gemini 2.5 Flash
- **Semantic Search**: Sentence Transformers
- **Vector Database**: Local embeddings for code matching
- **Fallback**: Regex pattern matching

### Quick Start

```bash
cd clinical_nlp_assignment

# Install dependencies
pip install -r requirements.txt

# Set Gemini API key (optional but recommended)
$env:GEMINI_API_KEY="your-api-key"

# Run extraction
python main.py --pdf_path "input/Input data for Assignment-1.pdf"
```

### Key Features

✅ AI-powered code extraction using Gemini  
✅ Semantic code matching with vector database  
✅ Hybrid approach (AI + regex) for maximum accuracy  
✅ Structured JSON output  
✅ Handles multiple report formats  

### Output Format

```json
{
  "Clinical Terms": [...],
  "Anatomical Locations": [...],
  "Diagnosis": [...],
  "Procedures": [...],
  "ICD-10": ["Z86.0100", "K64.8", "K57.90"],
  "CPT": ["45378"],
  "HCPCS": []
}
```

### Documentation

📖 **Full Documentation**: See `clinical_nlp_assignment/README.md`

---

## 📋 Assignment 2: Backend System Design

### Overview

**Complete backend system design** for a multi-tenant medical coding platform with:
- Database schema with ER diagram
- RESTful API specifications
- Multi-tenancy and security design
- Code versioning and audit trails

### Architecture Highlights

- **Multi-Tenant**: Organization-based data isolation
- **Scalable**: Designed for thousands of organizations
- **Auditable**: Complete change tracking
- **Versioned**: Support for annual code updates
- **Secure**: HIPAA-compliant design patterns

### Database Schema

- 9 core tables
- Support for organizations, providers, patients, encounters
- ICD-10 and CPT code management
- Code assignment tracking
- Complete audit trail

### API Design

- RESTful endpoints for all resources
- Multi-tenant isolation
- Bulk operations support
- Code search and retrieval
- History and audit access

### Documentation Files

1. **`ER_Diagram_and_Schema.md`** - Complete database design with SQL DDL
2. **`API_Design.md`** - Full REST API specifications
3. **`Design_Decisions.md`** - Architecture rationale and choices

📖 **Full Documentation**: See `backend_system_design/README.md`

---

## 🚀 Quick Setup Guide

### Prerequisites

- Python 3.8+
- pip package manager
- PostgreSQL/MySQL (for backend design reference)

### Assignment 1 Setup

```bash
# Navigate to assignment directory
cd clinical_nlp_assignment

# Install Python dependencies
pip install -r requirements.txt

# Ensure Excel files are in parent directory
# - ICD_code_Assignment.xlsx
# - cpt_code_assignment.xlsx

# (Optional) Set Gemini API key for better accuracy
# Get key from: https://makersuite.google.com/app/apikey
$env:GEMINI_API_KEY="your-api-key"

# Run extraction
python main.py --pdf_path "../Input data for Assignment.pdf"
```

### Assignment 2 Review

The backend design is provided as documentation:

1. Open `backend_system_design/ER_Diagram_and_Schema.md` to view database design
2. Open `backend_system_design/API_Design.md` to review API specifications
3. Open `backend_system_design/Design_Decisions.md` for architecture details

All documents are in Markdown format and can be:
- Read directly
- Converted to Word/PDF
- Visualized using database design tools

---

## 📊 Submission Contents

### ✅ Assignment 1: Clinical NLP

- [x] Python code for medical code extraction
- [x] Jupyter notebook with complete workflow
- [x] JSON output from clinical reports
- [x] Comprehensive README documentation
- [x] Requirements.txt with all dependencies
- [x] Configuration files

**Key Files**:
- `main.py` - Command-line interface
- `Clinical_NLP_Assignment.ipynb` - Notebook version
- `extractor.py` - Core extraction engine
- `output/extracted_data.json` - Sample output

### ✅ Assignment 2: Backend System Design

- [x] ER Diagram and Schema Design document
- [x] REST API Design specifications
- [x] Design Decisions explanation
- [x] Multi-tenancy implementation details
- [x] Security and scalability considerations

**Key Files**:
- `ER_Diagram_and_Schema.md` - Database design (479 lines)
- `API_Design.md` - API specifications (666 lines)
- `Design_Decisions.md` - Architecture rationale

---

## 🎯 Key Highlights

### Clinical NLP Assignment

- **AI-Powered**: Uses Google Gemini for intelligent extraction
- **Accurate**: Successfully extracts CPT code 45378 and other codes
- **Robust**: Hybrid approach ensures codes are found even with formatting variations
- **Production-Ready**: Error handling, fallbacks, and validation

### Backend System Design

- **Comprehensive**: Complete database and API design
- **Scalable**: Multi-tenant architecture supporting thousands of organizations
- **Secure**: HIPAA-compliant with audit trails
- **Well-Documented**: Detailed explanations for all design decisions

---

## 📝 Assignment Requirements Met

### Clinical NLP Requirements

✅ Extract ICD-10 diagnosis codes from clinical reports  
✅ Extract CPT procedure codes from clinical reports  
✅ Build vector database from reference Excel files  
✅ Use retrieval-based prediction  
✅ Generate JSON output in required format  
✅ Clean, readable, well-documented code  
✅ Jupyter notebook implementation  

### Backend System Design Requirements

✅ ER Diagram and Schema Design  
✅ Multi-tenancy support  
✅ REST API design for all resources  
✅ Code management (ICD/CPT)  
✅ Design decisions explanation  
✅ Versioning approach documented  

---

## 🔍 Testing & Validation

### Assignment 1

Tested with:
- ✅ Multiple PDF formats
- ✅ Various code formats (explicit and implicit)
- ✅ Different report structures
- ✅ Edge cases and error handling

**Sample Results**:
- Successfully extracts CPT 45378 from clinical reports
- Accurately identifies ICD-10 codes (Z86.0100, K64.8, K57.90)
- Extracts clinical terms, anatomical locations, and procedures

### Assignment 2

Design validated for:
- ✅ Multi-tenant data isolation
- ✅ Scalability (tested with sample queries)
- ✅ Security best practices
- ✅ Audit trail completeness
- ✅ Code versioning support

---

## 📚 Additional Information

### For Assignment 1

- **Dependencies**: See `clinical_nlp_assignment/requirements.txt`
- **Configuration**: See `clinical_nlp_assignment/config.py`
- **Detailed Docs**: See `clinical_nlp_assignment/README.md`

### For Assignment 2

- **Database**: SQL DDL ready for PostgreSQL/MySQL
- **APIs**: RESTful specifications ready for implementation
- **Documentation**: All design decisions explained
- **Detailed Docs**: See `backend_system_design/README.md`

---

## 🛠️ Technology Used

### Clinical NLP
- Python 3.8+
- Google Gemini API
- Sentence Transformers
- PyTorch
- Pandas, NumPy
- PyPDF2

### Backend Design
- PostgreSQL/MySQL (recommended)
- REST API patterns
- JWT authentication
- Row-Level Security
- Full-text search

---

## 📞 Notes

- **Clinical NLP**: First run builds vector databases (~2-3 minutes). Subsequent runs are much faster.
- **Backend Design**: All documents are in Markdown and can be converted to Word/PDF as needed.
- **Code Quality**: All code follows best practices with comprehensive error handling.
- **Documentation**: Extensive comments and documentation throughout.

---

## ✅ Submission Checklist

### Clinical NLP Assignment
- [x] Python code files
- [x] Jupyter notebook
- [x] JSON output sample
- [x] README documentation
- [x] Requirements.txt
- [x] Configuration files

### Backend System Design
- [x] ER Diagram & Schema (Word-ready format)
- [x] API Design document
- [x] Design Decisions explanation
- [x] README documentation

---

**Author**: MEDCODIO Assignment Submission  
**Date**: December 2024  
**Status**: ✅ Complete and Ready for Submission
