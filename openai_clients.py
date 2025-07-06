from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()  # .env dosyasını yükle

llm = init_chat_model(
    model="gpt-4o",                    
    model_provider="openai",
    api_key=os.getenv("OPENAI_API_KEY")  
)
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},  # GPU varsa "cuda" yaz
    encode_kwargs={"normalize_embeddings": True}  # cosine similarity için çok önemli
)