from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimensions: int = 512):
        self.model = SentenceTransformer(model_name, truncate_dim=dimensions)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text, convert_to_numpy=True).tolist()

def get_embedding_model():
    return SentenceTransformerEmbeddings()