from typing_extensions import List, TypedDict
from langchain.schema import Document
from _faiss_test import build_store
from load_docs_test import load_docs
from openai_clients_test import get_llm
from operator import itemgetter
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from sentence_transformers import CrossEncoder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from get_session_id_test import get_session_history
from summarizer_test import summarize_messages
import time  
import uuid

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L12-v2")

class State(TypedDict):
    question: str
    context: str
    answer: str
    session_id: str

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
                                    """
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template(
            "Bağlam (Özet): {context}\n\nSoru: {question}\n\nCevap:"
        ),
    ])

    chain = template | get_llm()
    
    chain_with_history = RunnableWithMessageHistory(
        chain,
        input_messages_key="question",
        history_messages_key="history",

        get_session_history= get_session_history,
    )

    def get_conversation_summary(history, n=5):
        """Kullanıcının son mesajına odaklanarak kısa ve anlamlı bir özet çıkar. 
        Bu özette, kullanıcının ne istediğini, mesajının amacını ve ifade etmeye çalıştığı temel düşünceyi belirt.
        Karmaşık ya da dolaylı ifadeleri sadeleştirerek, mesajın altında yatan niyeti açıkla.
        Özet tek cümle olmalı ve Türkçe yazılmalıdır."""
        
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
        summary_start = time.time()
        summary = get_conversation_summary(history, n=5)
        summary_duration = round(time.time() - summary_start, 3)

        if not summary:
            print(f"\n⏱️ Özet çıkarılamadı. Süre: {summary_duration}s (mesaj yok)")
            return current_question

        enhanced_query = f"Özet: {summary}\n\nSoru: {current_question}"
        print(f"\n📌 Özet: {summary}")
        print(f"⏱️ Özet çıkarma süresi: {summary_duration}s")
        print("📥 Enhanced Query:", enhanced_query)
        return enhanced_query


    def retrieve(state: State, session_id: str):
        start_time = time.time()
        query = state["question"]

        history = get_session_history(session_id) if session_id else ChatMessageHistory()
        summary_start = time.time()
        enhanced_query = create_enhanced_query(query, history)
        summary_duration = round(time.time() - summary_start, 3)

        doc_retrieval_start = time.time()
        results = vector_store.similarity_search_with_score(enhanced_query, k=25)
        doc_retrieval_duration = round(time.time() - doc_retrieval_start, 3)

        top_docs = [doc for doc, _ in results]

        cosine_start = time.time()
        cross_encoder_inputs = [(enhanced_query, doc.page_content) for doc in top_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)
        cosine_duration = round(time.time() - cosine_start, 3)

        reranked_docs = [
            doc for _, doc in sorted(zip(scores, top_docs), key=itemgetter(0), reverse=True)
        ][:10]

        total_retrieve_duration = round(time.time() - start_time, 3)
        print(f"\n⏱️ Retrieve süreleri:")
        print(f"  ➤ Özet çıkarma süresi: {summary_duration}s")
        print(f"  ➤ Belgeler (context) getirme süresi: {doc_retrieval_duration}s")
        print(f"  ➤ Cosine Similarity (cross-encoder) süresi: {cosine_duration}s")
        print(f"  ➤ Toplam retrieve süresi: {total_retrieve_duration}s")

        return {
            "context": reranked_docs,
            "question": query
        }
    def generate(state: State, session_id: str):
        start_time = time.time()
        docs_content = "\n\n".join(doc.page_content for doc in state['context'])
        config = {"configurable": {"session_id": session_id}}

        history = get_session_history(session_id) if session_id else ChatMessageHistory()
        summary = get_conversation_summary(history, n=5)
        input_data = {
            "question": state["question"],
            "context": docs_content,
            "summary": summary
        }

        llm_start = time.time()
        answer = chain_with_history.invoke(input_data, config=config)
        llm_duration = round(time.time() - llm_start, 3)
        total_generate_duration = round(time.time() - start_time, 3)

        print(f"\n⏱️ Generate süreleri:")
        print(f"  ➤ LLM cevap oluşturma süresi: {llm_duration}s")
        print(f"  ➤ Toplam generate süresi: {total_generate_duration}s")

        return {"answer": answer.content}

    return retrieve, generate