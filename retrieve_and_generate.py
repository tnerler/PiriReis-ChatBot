from typing_extensions import List, TypedDict
from langchain.schema import Document
from _faiss import build_store
from load_docs import load_docs
from openai_clients import llm



class State(TypedDict): 
        question: str
        context: List[Document]
        answer: str

def build_chatbot(prompt):

    docs = load_docs()
    vector_store = build_store(docs)

    chain = prompt | llm

    def retrieve(state:State):
        retrieved_docs = vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}

    def generate(state:State):
        docs_content = "\n\n".join(doc.page_content for doc in state['context'])
        answer = chain.invoke({'question':state["question"], "context":docs_content})

        return {"answer": answer.content}
    
    return retrieve, generate