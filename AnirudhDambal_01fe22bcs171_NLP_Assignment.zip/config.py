"""
Configuration file for Clinical NLP Assignment
"""
import os

# Paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(ROOT_DIR))
ICD_FILE = os.path.join(DATA_DIR, 'ICD_code_Assignment.xlsx')
CPT_FILE = os.path.join(DATA_DIR, 'cpt_code_assignment.xlsx')
# Default input PDF path (can be overridden via command line argument)
INPUT_DATA_PDF = os.path.join(DATA_DIR, 'Input data for Assignment.pdf')

# Output paths
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')
VECTOR_DB_DIR = os.path.join(ROOT_DIR, 'vector_db')
JSON_OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'extracted_data.json')

# Model configuration
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
TOP_K_RESULTS = 5  # Number of top matches to retrieve
SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score for code assignment

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyDXnFqLaYrIHOB8mA2Q5S9ThNyH14yfkpg"  
# Available models: 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro'
GEMINI_MODEL = 'gemini-2.5-flash'  # Fast and efficient model (similar to 2.5 Flash)
USE_GEMINI = True  # Set to False to use regex-only extraction

# Create directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

