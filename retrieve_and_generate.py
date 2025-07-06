from typing_extensions import List, TypedDict
from langchain.schema import Document
from _faiss import build_store
from load_docs import load_docs
from openai_clients import llm
from sentence_transformers import CrossEncoder
from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def build_chatbot():
    docs = load_docs()
    vector_store = build_store(docs)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key='question',
        output_key="answer"
    )

    template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "Sen Piri Reis Üniversitesi'nin resmi bilgi asistanı PiriX'sin. "
            "Öğrencilere ve ziyaretçilere üniversiteyle ilgili doğru bilgileri vermekle sorumlusun.\n\n"

            "Eğer soru doğrudan 'okul nasıl?', 'okul iyi mi?' gibi genel yargı sorularından biri ise, "
            "datalara bakmadan üniversitenin güçlü yönlerini vurgulayan olumlu ve motive edici bir cevap ver.\n\n"
            "Diğer tüm durumlarda, aşağıdaki bağlam parçalarını kullanarak mümkün olduğunca doğru, kısa ve net cevap ver.\n\n"
            "Veride açıkça yer almayan bir bilgi varsa uydurma. Sadece verilen bilgiler doğrultusunda cevap ver.\n" 
            "Cevapların kısa, samimi ve öz olmalı.\n"
            "Cevaplarının sonunda 'daha fazla bilgi için...', 'detaylar için web sitesini ziyaret edin', 'iletişime geçin' gibi ifadeler kullanma." 
            "Cevabın kendi içinde tamamlanmış ve yeterli olmalı."
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template(
            "Bağlam: {context}\nSoru: {question}\nCevap:"
        ),
    ])

    chain = template | llm

    def retrieve(state: State):
        query = state["question"]
        results = vector_store.similarity_search_with_score(query, k=15)
        top_docs = [doc for doc, _ in results[:10]]

        cross_encoder_inputs = [(query, doc.page_content) for doc in top_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)

        reranked_docs = [doc for _, doc in sorted(zip(scores, top_docs), key=itemgetter(0), reverse=True)]
        return {"context": reranked_docs[:5]}

    def generate(state: State):
        if not state["context"]:
            return {"answer": "Bilgim yok maalesef."}

        docs_content = "\n\n".join(doc.page_content for doc in state['context'])
        chat_history = memory.load_memory_variables({}).get("chat_history", [])

        input_data = {
            "context": docs_content,
            "question": state["question"],
            "chat_history": chat_history
        }

        answer = chain.invoke(input_data)
        memory.save_context({"question": state["question"]}, {"answer": answer.content})

        return {"answer": answer.content}

    return retrieve, generate
