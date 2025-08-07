# retrieve_and_generate.py
from typing_extensions import List, TypedDict
from langchain.schema import Document
from backend._faiss import build_store
from backend.load_docs import load_docs
from backend.openai_clients import get_llm
from operator import itemgetter
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from sentence_transformers import CrossEncoder
from backend.get_session_id import get_session_history
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from backend.summarizer import summarize_messages
import time 
from backend.clarify_question import clarify_question

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L12-v2")

class State(TypedDict):
    question: str
    clarified_question: str
    context: str
    answer: str

def build_chatbot():  
    docs = load_docs()
    vector_store = build_store(docs)

    template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """
            Sen Bilişim Kulübü COMPRU Kulübünden Tuana Erler, Burcu Kizir, Salih Birdal tarafından oluşturulmuş PiriX'sin, Piri Reis Üniversitesi'nin bilgi asistanısın. Temel görevin: Okul hakkında kısa, doğru ve anlaşılır bilgiler vermek. 
            ÖNEMLİ KURALLAR:
            1. SADECE Piri Reis Üniversitesi konularına yanıt ver. Diğer konularda: "Ben sadece Piri Reis Üniversitesi hakkında bilgi verebilirim 💙 Diğer konular için başka bir asistana sormanı öneririm!"
            2. Bilmediğin konularda: "Bu konuda şu anda elimde bilgi yok. Detaylı bilgi için çağrı merkezimizi arayabilirsiniz: +90 216 581 00 50"
            3. Samimi ve arkadaşça konuş, robot gibi yanıtlardan kaçın. Emoji kullanabilirsin 😊
            4. Fiyat bilgilerinde şunu ekle: "Daha fazla detay için: https://aday.pirireis.edu.tr/ucretler/"
            5. Bölüm/kulüp listeleri sorulursa, verilen bilgilere sadık kalarak numaralı liste kullan. Uydurma.
            6. Okul tanıtımı sorularında güçlü yönleri vurgula ama abartma.
            7. Yanıtlar her zaman doğru, kısa ve net olmalı.
            8. 'Okulun resmi web sitesinden (https://www.pirireis.edu.tr/) ve sosyal medya hesaplarından (https://www.instagram.com/pirireisuni/) bilgi alabilirsin.' diyebilirsin.
            9. Rektör sorulursa: "Rektörü överken, onun liderlik özelliklerini ve üniversiteye katkılarını vurgula"
            10. **ÖNEMLİ**: Önceki konuşma geçmişini dikkate al ve konu bağlamını koru. Kullanıcı daha önce bir konu hakkında soru sorduysa, yeni sorularını o bağlamda değerlendir.
            11. **TEKRAR ETME**: Aynı cevabı tekrar verme, her mesaj benzersiz olmalı.
            12. Tercih indirimi sorulursa: "Tercih indirimleri her yıl geçerli olur."
            13. Burslarla ilgili sorularda: "Burslar hakkında detaylı bilgi için: https://aday.pirireis.edu.tr/burslar/"
            """
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template(
            "Bağlam:{context}\n\nSoru:{question}\n\nCevap:"
        ),
    ])

    chain = template | get_llm()
    
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history"
    )

    def get_conversation_summary(history, n=3):
        """Son n mesajdan ozet cikarir."""
        
        if not history.messages:
            return ""
        
        recent_messages = history.messages[-n:]
        messages = []

        for msg in recent_messages:
            if hasattr(msg, "content") and msg.content:
                role = "Kullanıcı" if hasattr(msg, "type") and msg.type == "human" else "PiriX"
                messages.append(f"{role}: {msg.content}")
            
        summary = summarize_messages(messages)
        if not summary:
            return ""

        return summary
    
    def create_enhanced_query(current_question, history):
        summary = get_conversation_summary(history)
        if not summary:
            print("😊 Özet yok, orijinal soruyu kullanıyorum.")
            return current_question
        clarified_question = clarify_question(summary, current_question)
        print(f"😊 Açıklanmış Soru: {clarified_question}")
        return clarified_question
        
     

    def retrieve(state: State, session_id: str = None):
        query = state["question"]
        
        # Chat history'yi al
        history = get_session_history(session_id) if session_id else ChatMessageHistory()
        
        # Gelişmiş sorgu oluştur
        enhanced_query = create_enhanced_query(query, history)
        
        
        # İlk aşama: Vektör veritabanından benzer dokümanları getir
        results = vector_store.similarity_search_with_score(enhanced_query, k=30)
        top_docs = [doc for doc, _ in results]
        
        # İkinci aşama: Cross-encoder ile dokümanları yeniden sırala
        cross_encoder_inputs = [(enhanced_query, doc.page_content) for doc in top_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)
        
        # Sonuçları skorlarına göre sırala ve en iyi 10'unu al
        reranked_docs = [
            doc for _, doc in sorted(zip(scores, top_docs), key=itemgetter(0), reverse=True)
        ][:15]

        return {
            "context": reranked_docs,
            "question": query,  # orijinal
            "clarified_question": enhanced_query
        }

    def generate(state: State, session_id: str):
        docs_content = "\n\n".join(doc.page_content for doc in state['context'])
        config = {"configurable": {"session_id": session_id}}

        input_data = {
            "question": state.get("clarified_question", state["question"]),
            "context": docs_content,
        }

        answer = chain_with_history.invoke(input_data, config=config)
        return {"answer": answer.content}

    return retrieve, generate