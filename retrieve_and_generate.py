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
from langchain.memory import ConversationBufferMemory
from openai_clients import llm

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Tag embeddinglerini güncelle ve önbellekten al
tag_embeddings_cache = update_and_get_tag_embeddings()


# İki vektör arasındaki kosinüs benzerliğini hesaplar (0-1 arasında değer döner)
def cosine_similarity(vec1, vec2) -> float: 
     vec1 = np.array(vec1).reshape(-1)
     vec2 = np.array(vec2).reshape(-1)
     return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Chatbotun çalışırken kullanacağı durumu temsil eden yapı
class State(TypedDict): 
    """
    Chatbot fonksiyonlarında kullanılan state yapısı.
    
    İçerik:
    - question: Kullanıcının sorduğu soru (string).
    - context: Soruyla ilişkili bulunan dokümanlar listesi (Document listesi).
    - answer: Modelin oluşturduğu cevap (string).
    """  
    question: str
    context: List[Document]
    answer: str

def build_chatbot():
    """
    Chatbot yapısını oluşturur.
    
    Args:
        prompt: LLM prompt pipeline'ı (soru ve context'i işleyip model çağıran zincir).
    
    İşleyiş:
    1. Belgeleri yükler (load_docs).
    2. Belgelerden FAISS tabanlı vektör veritabanı oluşturur veya var olanı yükler (build_store).
    3. Prompt'u LLM ile zincirler (prompt | llm).
    4. retrieve fonksiyonu:
        - Kullanıcı sorusunu embedding'e çevirir.
        - FAISS veritabanından en benzer 5 dokümanı alır.
        - Her dokümanın tag embeddingleri ile kullanıcı sorusu arasındaki benzerliği hesaplar.
        - Eğer tag benzerliği yüksekse (0.8 üzeri) dokümanın skorunu iyileştirir.
        - Dokümanları skorlarına göre sıralar ve en iyi 3 tanesini döner.
    5. generate fonksiyonu:
        - retrieve ile seçilen dokümanların içeriğini birleştirir.
        - Prompt'a soru ve context olarak verip modelden cevap üretir.
    6. retrieve ve generate fonksiyonlarını döner.
    """

    docs = load_docs()
    vector_store = build_store(docs)


    # Kullanıcının geçmiş mesajlarını hafızada tutmak için ConversationBufferMemory kullanıyoruz.
    # Bu, çok turlu sohbetlerde önceki mesajları hatırlamamıza yardımcı olur.
    # input_key="question" yaptikki konusmalari sadece sorulara gore hatirlasin asagida contextide verdigimiz icin
    # kafasi karisiyor ve uydurabiliyor.(contexte gore)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, input_key='question')




    # ChatPromptTemplate ile bir prompt şablonu oluşturuyoruz.
    # Bu şablon, sistem mesajı, geçmiş konuşmalar ve insan mesajından oluşur.
    template = ChatPromptTemplate.from_messages([

        # Sistem mesajı: PiriX'in kim olduğunu ve nasıl davranması gerektiğini tanımlar.
        SystemMessagePromptTemplate.from_template(
        "Sen Piri Reis Üniversitesi'nin bilgi asistanı PiriX'sin. Öğrencilere bilgi vermek asıl görevin. "
        "Soruyu cevaplamak için aşağıdaki bağlam parçalarını kullan. "
        "Cevabı bilmiyorsan bilmediğini söyle, uydurma. "
        "Cevabı mümkün olduğunca kısa ve net ver."
    ),
     # Önceki konuşmaları (chat_history) prompta ekliyoruz. 
    # Bu, çok turlu konuşmalarda bağlamın korunmasını sağlar.
    MessagesPlaceholder(variable_name="chat_history"),

    # İnsan (kullanıcı) mesajı için bir şablon tanımlıyoruz.
    # Modelin cevap verebilmesi için gerekli bağlam (context) ve soru (question) bilgisi sağlanıyor.
    HumanMessagePromptTemplate.from_template(
        "Bağlam: {context}\nSoru: {question}\nCevap:"
    ),
])
    # prompt ile LLM zincirini oluşturuyoruz (soru ve context'i birleştirip LLM'ye gönderiyoruz)
    chain = template | llm



    # Kullanıcının sorusuna benzer belgeleri FAISS ve tag embedding'lerini kullanarak bulur
    def retrieve(state:State):
        query = state["question"]

        # Sorguyu embedding vektörüne çevir
        query_embedding = vector_store.embedding_function.embed_query(query)

        # FAISS'ten benzer dokumanlari getir
        results = vector_store.similarity_search_with_score(query, k=10)

        boosted_docs = [] # İyileştirilmiş (boost edilmiş) dokümanlar ve skorlarını tutacak liste

        for doc, score in results:
            # Dokümanın metadata kısmından tag'leri al, yoksa boş liste al
            tags = doc.metadata.get("tags", [])
            tag_score = 0 # Her doküman için tag skorunu sıfırla

            for tag in tags:    
                # Önbellekte (cache) bu tag'ın embedding bilgisini ara
                cached_tag = tag_embeddings_cache.get(tag)
                if cached_tag is None:
                     # Eğer embedding yoksa o tag'ı atla ve diğer tag'a geç
                     continue
                     
                # Tag'ın embedding vektörünü al
                tag_embedding = cached_tag["embedding"]
                tag_embedding = np.array(tag_embedding)


                # Kullanıcının sorgusunun embedding'i ile tag embedding'i arasındaki benzerliği hesapla
                similarity = cosine_similarity(query_embedding, tag_embedding)
                if similarity > 0.40:
                    # Tag benzerliği sebebiyle dokümanın skorunu 0.2 azalt burada tag_scoreunu arttiriyoruz digerki satirda dusurecegiz (skor düştükçe doküman daha iyi)
                    tag_score += 0.2
            # Iste burada final_score'u azaltiyoruz tag_score kadar (score = distance olarak hesaplandigi icin ne kadar dusuk distance o kadar iyi bu yuzden dusuruyoruz skoru)
            final_score = score - tag_score
            boosted_docs.append((doc, final_score))
        
        # Dokümanları, skorlarına göre küçükten büyüğe sırala (daha düşük skor = daha iyi eşleşme)
        boosted_docs.sort(key=lambda x: x[1]) # x[0] == doc, x[1] == final score
        # Ilk 3 en iyi documenti aliyoruz 
        top_boosted_docs = [doc for doc, _ in boosted_docs[:10]]
        
        # Bu aşamada cross encoder'a input olarak query (soru) ile her bir dokümanın içeriğini (page_content) birlikte veriyoruz.
        # Cross encoder, bu query-doküman çiftleri için benzerlik puanı döner.
        # Bu model genellikle BERT veya benzeri transformer tabanlı modellerdir ve iki metin arasında ne kadar alakalı olduklarını anlamaya çalışır.
        cross_encoder_inputs = [(query, doc.page_content) for doc in top_boosted_docs]

        
        scores = cross_encoder.predict(cross_encoder_inputs)

        # `scores` ile `top_boosted_docs`'u birlikte sıralayıp (skora göre) en alakalı dokümanları en üste alıyoruz.
        # `itemgetter(0)` sayesinde skorlar baz alınarak sıraya konur. `reverse=True` ile en yüksek skor en öne gelir.
        reranked_docs = [doc for _, doc in sorted(zip(scores, top_boosted_docs), key=itemgetter(0), reverse=True)]
        final_top_docs = reranked_docs[:3]

        return {"context": final_top_docs}
    
    def generate(state:State):
        docs_content = "\n\n".join(doc.page_content for doc in state['context'])
        
        # chat_history'yi generate fonksiyonuna ekliyoruz ki model ona gore cevap uretebilsin.
        chat_history = memory.load_memory_variables({}).get("chat_history", [])

        # modelimize verdigimiz inputlar 
        input_data = {
        "context": docs_content,   # context = ilgili doküman içeriği
        "question": state["question"],
        "chat_history": chat_history
    }
        answer = chain.invoke(input_data)

        # Daha sonra soruyu ve modelin cevabini chat_historye kaydeder. (Memory)
        memory.save_context({"question": state["question"]}, {"answer": answer.content})

        return {"answer": answer.content}
    
    return retrieve, generate