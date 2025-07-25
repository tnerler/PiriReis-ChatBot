from typing_extensions import List, TypedDict
from langchain.schema import Document
from _faiss import build_store
from load_docs import load_docs
from openai_clients import get_llm
import numpy as np 
import pickle 
from sentence_transformers import CrossEncoder
from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain.prompts import PromptTemplate
from sklearn.metrics.pairwise import cosine_similarity
from type_embedding import load_embedding_cache, save_embedding_cache
import re

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L12-v2")
cache_path = "type_embeddings_cache.pkl"
type_embeddings_cache = load_embedding_cache(cache_path)  

def detect_ranking_query(query):
    """
    Sorgunun sıralama tabanlı olup olmadığını tespit eder ve sıralamayı çıkarır.
    """
    ranking_keywords = ['sıralama', 'sıralama', 'ranking', 'siralama', 'yerleştirme']
    has_ranking_keyword = any(keyword in query.lower() for keyword in ranking_keywords)
    
    # Sayısal sıralama değeri çıkar
    ranking_numbers = re.findall(r'\b(\d{1,6})\b', query)
    extracted_ranking = None
    
    if ranking_numbers and has_ranking_keyword:
        # En makul sıralama değerini seç (genellikle en büyük sayı)
        for num_str in ranking_numbers:
            num = int(num_str)
            if 1000 <= num <= 500000:  # Makul sıralama aralığı
                extracted_ranking = num
                break
    
    return has_ranking_keyword, extracted_ranking

def filter_docs_by_ranking(docs, user_ranking):
    """
    Kullanıcının sıralamasına uygun belgeleri filtreler.
    """
    if not user_ranking:
        return docs
    
    relevant_docs = []
    for doc in docs:
        # Sıralama aralığı kontrolü
        taban_siralama = doc.metadata.get('taban_siralama')
        tavan_siralama = doc.metadata.get('tavan_siralama')
        
        if taban_siralama and tavan_siralama:
            # Kullanıcının sıralaması bu bölüm için uygun mu?
            if tavan_siralama <= user_ranking <= taban_siralama:
                relevant_docs.append(doc)
        else:
            # Sıralama bilgisi olmayan dokümanları da ekle
            relevant_docs.append(doc)
    
    return relevant_docs

def boost_ranking_docs(docs, query, query_embedding, user_ranking=None):
    """
    Sıralama dokümanlarını öne çıkarır ve kullanıcı sıralamasına göre ek boost verir.
    """
    boosted_docs = []
    
    for doc, score in docs:
        boost = 0
        
        # Sıralama dokümanı boost'u
        if doc.metadata.get('is_ranking_doc', False):
            boost += 0.4
        
        # Sıralama sorgu dokümanı boost'u
        if doc.metadata.get('query_type') in ['ranking_summary', 'ranking_query']:
            boost += 0.3
        
        # Kullanıcı sıralamasına uygunluk boost'u
        if user_ranking:
            taban = doc.metadata.get('taban_siralama')
            tavan = doc.metadata.get('tavan_siralama')
            
            if taban and tavan:
                if tavan <= user_ranking <= taban:
                    boost += 0.5  # Çok yüksek boost - tam uygun
                elif abs(user_ranking - tavan) <= 10000 or abs(user_ranking - taban) <= 10000:
                    boost += 0.2  # Yakın sıralama boost'u
        
        # Type boost (orijinal sistem)
        doc_type = doc.metadata.get("type", "")
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

            if similarity > 0.6:
                boost += 0.35
        
        final_score = score - boost
        boosted_docs.append((doc, final_score))
    
    return boosted_docs  

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
        """Sen Bilişim Kulübü COMPRU tarafından oluşturulmuş, Piri Reis Üniversitesi'nin aday öğrenciler için oluşturulmuş resmi bilgi asistanı PiriX'sin.
        Öğrencilere ve ziyaretçilere üniversite ile ilgili doğru bilgileri herkesin anlayabileceği kısa ve öz cevap vermekle sorumlusun. Kullanıcı soruları 
        genel yargı içeren sorularsa ('okul nasıl?', 'okul iyi mi?'), üniversitenin güçlü yönlerini vurgulayan, pozitif, motive edici, herkesin anlayabileceği kısa 
        ve öz cevap ver. Eğer kullanıcı senden herhangi bir konuda liste (kulüpler, bölümler, öğretim üyeleri vb.) istiyorsa, sağlanan bağlamdaki maddelerin tamamını
        eksiksiz, numaralı ya da madde işaretli biçimde listele; bağlamda olmayan maddeleri ekleme. Diğer tüm durumlarda, yalnızca verilen bağlamı kullanarak kısa,
        net ve kendi içinde tamamlanmış cevaplar sun. Bağlam dışında yer almayan hiçbir bilgiyi ekleme ve kullanıcıyı ek kaynaklara yönlendirme. Tüm cevapların, 
        her zaman Üniversite hakkında ikne edici herkesin anlayabileceği kısa ve öz bir cevap üretmen gerekiyor. Fiyatlar konusunda kesinlikle bilgi ver, verilerde tüm fiyat durumları gözüküyor, Fiyatlar senelik ve 2025-2026 dönemini kapsar.
        Bilgin olmayan sorularda şu şekilde cevap ver: "Bu konuda şu anda elimde bilgi yok. Detaylı bilgi için çağrı merkezimizi arayabilirsiniz: **+90 216 581 00 50**."""


    ),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template(
        "Bağlam: {context}\nSoru: {question}\nCevap:"
    ),
])


    chain = template |get_llm()

    def retrieve(state: State):
        query = state["question"]
        
        # Sıralama sorgusu kontrolü
        is_ranking_query, user_ranking = detect_ranking_query(query)
        
        # Temel vektör araması
        query_embedding = vector_store.embedding_function.embed_query(query)
        k_value = 40 if is_ranking_query else 30
        results = vector_store.similarity_search_with_score(query, k=k_value)

        # Sıralama tabanlı filtreleme ve boost
        if is_ranking_query:
            print(f"[DEBUG] Sıralama sorgusu tespit edildi: {user_ranking}")
            
            # Sıralama dokümanlarını öne çıkar
            boosted_docs = boost_ranking_docs(results, query, query_embedding, user_ranking)
            
            # Kullanıcı sıralamasına uygun dokümanları filtrele
            if user_ranking:
                filtered_docs = []
                for doc, score in boosted_docs:
                    taban = doc.metadata.get('taban_siralama')
                    tavan = doc.metadata.get('tavan_siralama')
                    
                    # Uygun sıralama aralığında olan dokümanları öne al
                    if taban and tavan and tavan <= user_ranking <= taban:
                        filtered_docs.insert(0, (doc, score - 1.0))  # En öne al
                    else:
                        filtered_docs.append((doc, score))
                
                boosted_docs = filtered_docs
        else:
            # Standart boost sistemi
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

                    if similarity > 0.6:
                        type_boost += 0.35

                final_score = score - type_boost
                boosted_docs.append((doc, final_score))
        
        # Skorlara göre sırala
        boosted_docs.sort(key=lambda x: x[1])
        top_boosted_docs = [doc for doc, _ in boosted_docs[:20]]

        # Cross-encoder ile tekrar sırala
        cross_encoder_inputs = [(query, doc.page_content) for doc in top_boosted_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)

        reranked_docs = [
            doc for _, doc in sorted(zip(scores, top_boosted_docs), key=itemgetter(0), reverse=True)
        ]

        return {
            "context": reranked_docs[:8],
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