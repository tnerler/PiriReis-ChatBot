from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from langchain_core.embeddings import Embeddings

class BGEM3Embeddings(Embeddings):
    """BGE-M3 model için sentence-transformers ile LangChain uyumlu implementation"""
    
    def __init__(self, model_name: str = 'BAAI/bge-m3'):      
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Birden fazla döküman için embedding"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Tek bir sorgu için embedding"""
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0].tolist()

def get_embedding_model(model_type: str = "bge-m3"):
    """
    Embedding model türüne göre model döndürür
    model_type: "bge-m3" veya "openai"
    """
    if model_type == "bge-m3":
        return BGEM3Embeddings(model_name='BAAI/bge-m3')
    else:
        raise ValueError(f"Bu dosyada sadece bge-m3 destekleniyor, istenen: {model_type}")