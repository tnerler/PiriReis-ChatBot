import os 
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
print("API Key:", os.getenv("OPENAI_API_KEY"))
print("LANGSMITH KEY",os.getenv("LANGSMITH_API_KEY"))
