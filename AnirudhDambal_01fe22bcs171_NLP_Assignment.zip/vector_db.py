"""
Vector Database for ICD and CPT Code Retrieval
"""
import pandas as pd
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import config

class CodeVectorDB:
    """Vector database for medical code retrieval"""
    
    def __init__(self, embedding_model: str = None):
        """Initialize the vector database"""
        self.embedding_model_name = embedding_model or config.EMBEDDING_MODEL
        self.model = SentenceTransformer(self.embedding_model_name)
        self.icd_codes = []
        self.icd_descriptions = []
        self.icd_embeddings = None
        self.cpt_codes = []
        self.cpt_descriptions = []
        self.cpt_embeddings = None
        
    def build_icd_database(self, icd_file: str = None):
        """Build vector database from ICD codes Excel file"""
        icd_file = icd_file or config.ICD_FILE
        print(f"Loading ICD codes from {icd_file}...")
        
        df = pd.read_excel(icd_file)
        
        # Handle different possible column names
        code_col = None
        desc_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'code' in col_lower or 'icd' in col_lower:
                code_col = col
            if 'description' in col_lower or 'desc' in col_lower or 'name' in col_lower:
                desc_col = col
        
        if code_col is None or desc_col is None:
            # Use first two columns as fallback
            code_col = df.columns[0]
            desc_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        self.icd_codes = df[code_col].astype(str).tolist()
        self.icd_descriptions = df[desc_col].astype(str).tolist()
        
        # Create searchable text: code + description
        searchable_texts = [
            f"{code} {desc}" for code, desc in zip(self.icd_codes, self.icd_descriptions)
        ]
        
        print(f"Generating embeddings for {len(searchable_texts)} ICD codes...")
        self.icd_embeddings = self.model.encode(searchable_texts, show_progress_bar=True)
        
        # Save to disk
        icd_db_path = os.path.join(config.VECTOR_DB_DIR, 'icd_vector_db.pkl')
        with open(icd_db_path, 'wb') as f:
            pickle.dump({
                'codes': self.icd_codes,
                'descriptions': self.icd_descriptions,
                'embeddings': self.icd_embeddings
            }, f)
        
        print(f"ICD vector database saved to {icd_db_path}")
        return len(self.icd_codes)
    
    def build_cpt_database(self, cpt_file: str = None):
        """Build vector database from CPT codes Excel file"""
        cpt_file = cpt_file or config.CPT_FILE
        print(f"Loading CPT codes from {cpt_file}...")
        
        df = pd.read_excel(cpt_file)
        
        # Handle different possible column names
        code_col = None
        desc_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'code' in col_lower or 'cpt' in col_lower:
                code_col = col
            if 'description' in col_lower or 'desc' in col_lower or 'name' in col_lower:
                desc_col = col
        
        if code_col is None or desc_col is None:
            # Use first two columns as fallback
            code_col = df.columns[0]
            desc_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        self.cpt_codes = df[code_col].astype(str).tolist()
        self.cpt_descriptions = df[desc_col].astype(str).tolist()
        
        # Create searchable text: code + description
        searchable_texts = [
            f"{code} {desc}" for code, desc in zip(self.cpt_codes, self.cpt_descriptions)
        ]
        
        print(f"Generating embeddings for {len(searchable_texts)} CPT codes...")
        self.cpt_embeddings = self.model.encode(searchable_texts, show_progress_bar=True)
        
        # Save to disk
        cpt_db_path = os.path.join(config.VECTOR_DB_DIR, 'cpt_vector_db.pkl')
        with open(cpt_db_path, 'wb') as f:
            pickle.dump({
                'codes': self.cpt_codes,
                'descriptions': self.cpt_descriptions,
                'embeddings': self.cpt_embeddings
            }, f)
        
        print(f"CPT vector database saved to {cpt_db_path}")
        return len(self.cpt_codes)
    
    def load_icd_database(self):
        """Load ICD vector database from disk"""
        icd_db_path = os.path.join(config.VECTOR_DB_DIR, 'icd_vector_db.pkl')
        if os.path.exists(icd_db_path):
            with open(icd_db_path, 'rb') as f:
                data = pickle.load(f)
                self.icd_codes = data['codes']
                self.icd_descriptions = data['descriptions']
                self.icd_embeddings = data['embeddings']
            print(f"Loaded {len(self.icd_codes)} ICD codes from database")
        else:
            print(f"ICD database not found at {icd_db_path}. Please build it first.")
    
    def load_cpt_database(self):
        """Load CPT vector database from disk"""
        cpt_db_path = os.path.join(config.VECTOR_DB_DIR, 'cpt_vector_db.pkl')
        if os.path.exists(cpt_db_path):
            with open(cpt_db_path, 'rb') as f:
                data = pickle.load(f)
                self.cpt_codes = data['codes']
                self.cpt_descriptions = data['descriptions']
                self.cpt_embeddings = data['embeddings']
            print(f"Loaded {len(self.cpt_codes)} CPT codes from database")
        else:
            print(f"CPT database not found at {cpt_db_path}. Please build it first.")
    
    def search_icd(self, query_text: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict]:
        """Search for matching ICD codes"""
        if self.icd_embeddings is None:
            self.load_icd_database()
        
        if self.icd_embeddings is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query_text])[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self.icd_embeddings, query_embedding) / (
            np.linalg.norm(self.icd_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] >= threshold:
                results.append({
                    'code': self.icd_codes[idx],
                    'description': self.icd_descriptions[idx],
                    'similarity_score': float(similarities[idx])
                })
        
        return results
    
    def search_cpt(self, query_text: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict]:
        """Search for matching CPT codes"""
        if self.cpt_embeddings is None:
            self.load_cpt_database()
        
        if self.cpt_embeddings is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query_text])[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self.cpt_embeddings, query_embedding) / (
            np.linalg.norm(self.cpt_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] >= threshold:
                results.append({
                    'code': self.cpt_codes[idx],
                    'description': self.cpt_descriptions[idx],
                    'similarity_score': float(similarities[idx])
                })
        
        return results

