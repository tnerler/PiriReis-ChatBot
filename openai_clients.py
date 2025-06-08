from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings

llm = init_chat_model("gpt-4o-mini", model_provider="openai")
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")