from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt

load_dotenv()
@retry(wait=wait_random_exponential(min=1,max=30),stop=stop_after_attempt(5))

def get_llm():
    try:
        return init_chat_model(
        model="gpt-4o",
        model_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
    )
    except Exception as e:
        print(f"[!] LLM başlatılırken hata: {e}")
        raise


@retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(5))
def get_embedding_model():
    return OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=os.getenv("OPENAI_API_KEY")
    )
