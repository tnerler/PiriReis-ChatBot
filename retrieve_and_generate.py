from typing_extensions import List, TypedDict
from langchain.schema import Document
from _faiss import build_store
from load_docs import load_docs
from openai_clients import llm
import numpy as np 
import pickle 
from sentence_transformers import CrossEncoder
from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain.prompts import PromptTemplate
from sklearn.metrics.pairwise import cosine_similarity
from type_embedding import load_embedding_cache, save_embedding_cache

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
cache_path = "type_embeddings_cache.pkl"
type_embeddings_cache = load_embedding_cache(cache_path)  

class State(TypedDict):
    question: str
    context: str
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

        "Sen Piri Reis Üniversitesi'nin resmi bilgi asistanı PiriX'sin."
        "Öğrencilere ve ziyaretçilere üniversiteyle ilgili doğru bilgileri vermekle sorumlusun."

        "Eğer soru 'okul nasıl?', 'okul iyi mi?' gibi genel yargı sorularından biri ise,"
        "datalara bakmadan üniversitenin güçlü yönlerini vurgulayan olumlu ve motive edici bir cevap ver."

        "Diğer tüm durumlarda, aşağıdaki bağlam parçalarını kullanarak mümkün olduğunca doğru, net ve tamamlanmış cevaplar ver."

        "❗ Eğer soruda liste isteniyorsa (örneğin kulüpler, öğretim üyeleri, bölümler, programlar),"
        "verilen verideki tüm maddeleri eksiksiz ve madde madde yaz."
        "Liste uzun olsa bile tamamını belirt."

        "❗ Veride açıkça yer almayan bir bilgi varsa uydurma yapma."
        "Sadece verilen bilgiler doğrultusunda cevap ver."

        "❗ Cevapların tamamlanmış ve anlaşılır olmalı."
        "Cevabın kendi içinde yeterli olsun; 'daha fazla bilgi için...' gibi ifadeler kullanma."

        "❗ Eğer soru Piri Reis Üniversitesi ile ilgili değilse, örneğin:"
        "- Genel kültür veya bilgi (örneğin: 2+2 kaç eder?, diferansiyel denklemler nedir?, su kaç derecede donar?)"
        "- Kişisel veya anlamsız sorular (GPT misin?, kaç yaşındasın?, en sevdiğin renk nedir?)"
        "- Eğitim dışı akademik sorular (fizik, matematik, yapay zeka tanımı vs.)"
        "gibi konularsa, şu cevabı ver:"
        "Ben yalnızca Piri Reis Üniversitesi ile ilgili soruları yanıtlamak için tasarlandım."

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
        results = vector_store.similarity_search_with_score(query, k=35)


        boosted_docs = []

        for doc, score in results:
            type_boost = 0
            doc_type = doc.metadata.get("type")

            if doc_type:

                if doc_type in type_embeddings_cache:
                    type_embedding = type_embeddings_cache[doc_type]
                else:
                    type_embedding = vector_store.embedding_function.embed_query(doc_type)
                    type_embeddings_cache[doc_type] = type_embedding

                similarity = cosine_similarity(
                    np.array(query_embedding).reshape(1, -1),
                    np.array(type_embedding).reshape(1, -1)
                )[0][0]

                if similarity > 0.45:
                    type_boost += 0.2


            final_score = score - type_boost

            boosted_docs.append((doc, final_score))
        
        boosted_docs.sort(key=lambda x: x[1])
        top_boosted_docs = [doc for doc, _ in boosted_docs[:15]]

        cross_encoder_inputs = [(query, doc.page_content) for doc in top_boosted_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)

        reranked_docs = [
            doc for _, doc in sorted(zip(scores, top_boosted_docs), key=itemgetter(0), reverse=True)
        ]

        return {
        "context": reranked_docs[:5],
        "question": query
        }



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

save_embedding_cache(type_embeddings_cache, cache_path)