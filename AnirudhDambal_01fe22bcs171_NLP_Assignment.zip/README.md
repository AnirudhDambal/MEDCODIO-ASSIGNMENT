# Clinical NLP Assignment - Medical Code Extraction

## 📋 Overview

This project extracts structured medical data from clinical reports using Natural Language Processing (NLP) and AI-powered code extraction. It identifies:

- **ICD-10 Diagnosis Codes** (e.g., Z86.0100, K64.8, K57.90)
- **CPT Procedure Codes** (e.g., 45378, 45380, 99213)
- **HCPCS Codes** (e.g., J3490, A4216)
- **Clinical Terms** (conditions, symptoms, findings)
- **Anatomical Locations** (body parts mentioned)
- **Diagnosis Descriptions** (full diagnosis text)
- **Procedures** (performed procedures)

## 🚀 Features

- **AI-Powered Extraction**: Uses Google Gemini 2.5 Flash model for intelligent code extraction
- **Vector Database**: Semantic search using sentence transformers for code matching
- **Hybrid Approach**: Combines AI extraction with regex pattern matching for maximum accuracy
- **Multi-Format Support**: Processes PDF clinical reports
- **Structured Output**: Generates clean JSON format ready for integration

## 🏗️ Architecture

### Technical Stack

1. **Gemini API (Primary)**: Google's Gemini 2.5 Flash for context-aware code extraction
2. **Sentence Transformers**: Creates embeddings for semantic code matching
3. **Vector Database**: Fast retrieval of relevant medical codes
4. **Regex Fallback**: Pattern matching when AI is unavailable

### Workflow

```
PDF Input → Text Extraction → AI Analysis (Gemini) → Code Matching → JSON Output
                                    ↓
                            Vector DB Validation
                                    ↓
                            Structured Data
```

## 📁 Project Structure

```
clinical_nlp_assignment/
├── main.py                         # Main entry point (command-line script)
├── Clinical_NLP_Assignment.ipynb  # Jupyter notebook version
├── config.py                       # Configuration (API keys, paths, settings)
├── extractor.py                    # Core extraction logic (Gemini + regex)
├── vector_db.py                    # Vector database for code embeddings
├── utils.py                        # Utility functions
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── input/                          # Input PDF files (optional)
│   ├── Input data for Assignment-1.pdf
│   └── ...
│
├── output/                         # Generated JSON output
│   └── extracted_data.json
│
└── vector_db/                      # Cached vector databases
    ├── icd_vector_db.pkl           # ICD code embeddings
    └── cpt_vector_db.pkl           # CPT code embeddings
```

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection (for Gemini API and model downloads)

### Step 1: Install Dependencies

```bash
cd clinical_nlp_assignment
pip install -r requirements.txt
```

### Step 2: Prepare Reference Files

Ensure the following Excel files are in the **parent directory** (one level up):

- `ICD_code_Assignment.xlsx` - ICD-10 code reference with descriptions
- `cpt_code_assignment.xlsx` - CPT code reference with descriptions

These files are used to build the vector database for semantic code matching.

### Step 3: Configure Gemini API (Recommended)

For best accuracy, set up Google Gemini API:

1. **Get API Key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated key

2. **Set API Key**:

   **Option A: Environment Variable (Recommended)**
   ```powershell
   # Windows PowerShell
   $env:GEMINI_API_KEY="your-api-key-here"
   
   # Windows CMD
   set GEMINI_API_KEY=your-api-key-here
   
   # Linux/Mac
   export GEMINI_API_KEY="your-api-key-here"
   ```

   **Option B: Direct in config.py**
   ```python
   # Edit config.py
   GEMINI_API_KEY = "your-api-key-here"
   ```

3. **Verify Setup**:
   ```bash
   python main.py --help
   ```
   If Gemini is configured, you'll see: `[INFO] Gemini API enabled`

**Note**: If no API key is set, the system automatically falls back to regex-based extraction.

## 💻 Usage

### Method 1: Command-Line Interface (Recommended)

```bash
# Extract from default PDF (defined in config.py)
python main.py

# Extract from specific PDF file
python main.py --pdf_path "input/Input data for Assignment-1.pdf"

# Extract from absolute path
python main.py --pdf_path "C:/Users/YourName/Documents/report.pdf"

# View help
python main.py --help
```

### Method 2: Jupyter Notebook

1. Open `Clinical_NLP_Assignment.ipynb` in Jupyter Lab/Notebook
2. Run all cells sequentially
3. Results will be saved to `output/extracted_data.json`

### Example Output

After running, you'll see:
```
================================================================================
EXTRACTION SUMMARY
================================================================================

Report 1:
  Clinical Terms: 11
  Anatomical Locations: 7
  Diagnosis: 6
  Procedures: 5
  ICD-10 Codes: 3 - K57.90, K64.8, Z86.0100
  CPT Codes: 1 - 45378
  HCPCS Codes: 0 - None

[SUCCESS] Extraction Complete!
```

## 📤 Output Format

The JSON output is saved to `output/extracted_data.json`:

```json
{
  "Clinical Terms": [
    "colon polyps",
    "Internal hemorrhoids",
    "Diverticulosis",
    "melanosis coli",
    "sigmoid diverticulosis"
  ],
  "Anatomical Locations": [
    "rectum",
    "cecum",
    "ileocecal valve",
    "proximal colon",
    "sigmoid colon"
  ],
  "Diagnosis": [
    "History of colon polyps",
    "Personal history of colonic polyps",
    "Internal hemorrhoids",
    "Diverticulosis",
    "Melanosis coli"
  ],
  "Procedures": [
    "Colonoscopy",
    "Monitored Anesthesia Care",
    "Rectal exam"
  ],
  "ICD-10": [
    "K57.90",
    "K64.8",
    "Z86.0100"
  ],
  "CPT": [
    "45378"
  ],
  "HCPCS": []
}
```

**Multiple Reports**: If processing multiple reports, the output will be an array of objects.

## 🔍 How It Works

### 1. Vector Database Construction (First Run)

- Reads ICD and CPT code Excel files
- Generates embeddings using sentence transformers
- Stores in `vector_db/` directory for fast retrieval
- **One-time process**: Takes a few minutes, then cached

### 2. PDF Text Extraction

- Extracts plain text from PDF clinical reports
- Handles multi-page documents
- Preserves document structure

### 3. Code Extraction Process

**Primary Method (Gemini API)**:
- Analyzes clinical text with Gemini 2.5 Flash
- Identifies medical codes using context understanding
- Extracts structured information intelligently

**Fallback Method (Regex)**:
- Pattern matching for explicit codes
- Semantic search in vector database
- Validates against code reference files

**Hybrid Approach**:
- Combines AI extraction with regex validation
- Ensures all codes are captured
- Improves accuracy through dual methods

### 4. Post-Processing

- Validates extracted codes
- Enhances with descriptions from vector DB
- Formats output as structured JSON

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# API Configuration
GEMINI_API_KEY = "your-key"  # Set here or via environment variable
GEMINI_MODEL = 'gemini-1.5-flash'  # Model to use
USE_GEMINI = True  # Enable/disable Gemini

# Extraction Settings
TOP_K_RESULTS = 5  # Number of top matches to retrieve
SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score

# File Paths
INPUT_DATA_PDF = "path/to/default/pdf"  # Default PDF path
```

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not set"
**Solution**: Set the API key as described in Step 3, or the system will use regex fallback.

### Issue: "PDF file not found"
**Solution**: 
- Check the file path is correct
- Use absolute path if relative path doesn't work
- Ensure PDF file exists and is readable

### Issue: "No codes extracted"
**Solution**:
- Check PDF text extraction quality (some scanned PDFs may have issues)
- Verify reference Excel files are in parent directory
- Try increasing `SIMILARITY_THRESHOLD` in config.py

### Issue: Vector database not building
**Solution**:
- Ensure Excel files (`ICD_code_Assignment.xlsx`, `cpt_code_assignment.xlsx`) exist
- Check file paths in `config.py`
- Verify `openpyxl` is installed: `pip install openpyxl`

### Issue: Slow extraction
**Solution**:
- Vector databases are built once and cached
- Subsequent runs are much faster
- Gemini API calls take a few seconds per report

## 📊 Performance

- **First Run**: ~2-3 minutes (builds vector databases)
- **Subsequent Runs**: ~10-30 seconds per report (depending on PDF size)
- **Gemini API**: ~5-10 seconds per extraction call
- **Regex Fallback**: ~2-5 seconds per report

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **Patient Data**: Ensure HIPAA compliance when processing real patient data
- **Data Storage**: Vector databases are stored locally; no data sent to external servers (except Gemini API)

## 📚 Dependencies

Key libraries:
- `google-generativeai` - Gemini API client
- `sentence-transformers` - Embedding generation
- `pandas` - Data manipulation
- `PyPDF2` - PDF text extraction
- `torch` - Deep learning backend
- `numpy` - Numerical operations

See `requirements.txt` for complete list.

## 🎯 Evaluation Metrics

For assessing extraction quality:

- **Accuracy**: Correctly identified codes / Total codes
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **Clinical Precision**: Expert validation of code appropriateness

## 🔮 Future Enhancements

- [ ] Support for HCPCS code extraction
- [ ] Code modifier detection (CPT modifiers)
- [ ] Multi-language support
- [ ] Batch processing for multiple PDFs
- [ ] Web interface
- [ ] Integration with EHR systems
- [ ] Confidence scoring visualization
- [ ] Audit trail for extracted codes

## 📝 License

This project is part of the MEDCODIO assignment submission.

## 👤 Author

Assignment submission for MEDCODIO AI Engineer position.

---

**Need Help?** Check the troubleshooting section or review the code comments for detailed explanations.
