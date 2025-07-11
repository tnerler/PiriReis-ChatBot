from typing_extensions import List, TypedDict
from langchain.schema import Document
from _faiss import build_store
from load_docs import load_docs
from openai_clients import llm
import numpy as np 
import pickle 
from tag_embeddings import update_and_get_tag_embeddings
from sentence_transformers import CrossEncoder
from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L12-v2")

# Tag embeddinglerini güncelle ve önbellekten al
tag_embeddings_cache = update_and_get_tag_embeddings()

# Kosinüs benzerliğini hesaplar
def cosine_similarity(vec1, vec2) -> float:
    vec1 = np.array(vec1).reshape(-1)
    vec2 = np.array(vec2).reshape(-1)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Kosinüs benzerliğini hesaplar
def cosine_similarity(vec1, vec2) -> float:
    vec1 = np.array(vec1).reshape(-1)
    vec2 = np.array(vec2).reshape(-1)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def build_chatbot():
    tag_embeddings_cache = update_and_get_tag_embeddings()
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
        query_embedding = vector_store.embedding_function.embed_query(query)
<<<<<<< HEAD
        results = vector_store.similarity_search_with_score(query, k=20)
=======
        results = vector_store.similarity_search_with_score(query, k=10)
>>>>>>> 1a9da20669938f90798e47175fa007104895bfeb

        boosted_docs = []

        for doc, score in results:
            tags = doc.metadata.get("tags", [])
            tag_score = 0

            for tag in tags:
                cached_tag = tag_embeddings_cache.get(tag)
                if cached_tag is None:
                    continue

                tag_embedding = np.array(cached_tag["embedding"])
                similarity = cosine_similarity(query_embedding, tag_embedding)

<<<<<<< HEAD
                if similarity > 0.45:
=======
                if similarity > 0.30:
>>>>>>> 1a9da20669938f90798e47175fa007104895bfeb
                    tag_score += (similarity - 0.3) * 0.3

            final_score = score - tag_score
            boosted_docs.append((doc, final_score))

        boosted_docs.sort(key=lambda x: x[1])
<<<<<<< HEAD
        top_boosted_docs = [doc for doc, _ in boosted_docs[:15]]
=======
        top_boosted_docs = [doc for doc, _ in boosted_docs[:10]]
>>>>>>> 1a9da20669938f90798e47175fa007104895bfeb

        cross_encoder_inputs = [(query, doc.page_content) for doc in top_boosted_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)

        reranked_docs = [doc for _, doc in sorted(zip(scores, top_boosted_docs), key=itemgetter(0), reverse=True)]
<<<<<<< HEAD
        return {"context": reranked_docs[:5]}
=======
        return {"context": reranked_docs[:3]}
>>>>>>> 1a9da20669938f90798e47175fa007104895bfeb

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