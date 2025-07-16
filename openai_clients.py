from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()  # .env dosyasını yükle

llm = init_chat_model(
    model="gpt-4o",                     
    model_provider="openai",
    api_key=os.getenv("OPENAI_API_KEY") 
)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large",api_key=os.getenv("OPENAI_API_KEY"))
