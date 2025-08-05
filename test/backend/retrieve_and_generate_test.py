# retrieve_and_generate.py (simplified for terminal/test usage)
from typing_extensions import TypedDict
from langchain.schema import Document
from backend._faiss import build_store
from backend.load_docs import load_docs
from backend.openai_clients import get_llm
from operator import itemgetter
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from sentence_transformers import CrossEncoder

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L12-v2", device="cuda")

class State(TypedDict):
    question: str
    context: str
    answer: str

def build_chatbot():
    docs = load_docs()
    vector_store = build_store(docs)

    template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """
            Sen **PiriX’sin**, COMPRU (Tuana Erler, Burcu Kizir, Salih Birdal) tarafından geliştirilen, Piri Reis Üniversitesi hakkında samimi ve kısa yanıtlar veren yapay zekâ asistanısın.  

            Kurallar:  
            -  PRU dışı soru → "Ben sadece Piri Reis Üniversitesi hakkında bilgi verebilirim 💙"  
            -  Bilgi yoksa → "Bu konuda şu anda elimde bilgi yok. Detaylı bilgi için: +90 216 581 00 50"  
            -  Ücret → ekle: https://aday.pirireis.edu.tr/ucretler/  
            -  Burs → ekle: https://aday.pirireis.edu.tr/burslar/  
            -  Tercih indirimi → "Tercih indirimleri her yıl geçerli olur."  
            -  Bölüm/kulüp listeleri → numaralı, uydurma yok  
            -  Tanıtım → güçlü yönleri vurgula ama abartma  
            -  Rektör → liderlik ve katkılarını belirt  
            -  Resmi site/Instagram linki verebilirsin  
            -  Konu bağlamını koru, aynı cevabı tekrar etme
            """
        ),
        HumanMessagePromptTemplate.from_template(
            "Bağlam: {context}\n\nSoru: {question}\n\nCevap:"
        ),
    ])

    chain = template | get_llm()

    def retrieve(state: State):
        query = state["question"]

        # Vektör veritabanından benzer dokümanları getir
        results = vector_store.similarity_search_with_score(query, k=12)
        top_docs = [doc for doc, _ in results]

        # Cross-encoder ile yeniden sırala
        cross_encoder_inputs = [(query, doc.page_content) for doc in top_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)

        reranked_docs = [
            doc for _, doc in sorted(zip(scores, top_docs), key=itemgetter(0), reverse=True)
        ][:7]

        return {
            "context": reranked_docs,
            "question": query
        }

    def generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        input_data = {
            "question": state["question"],
            "context": docs_content,
        }

        answer = chain.invoke(input_data)  # geçmiş / session_id yok
        return {"answer": answer.content}

    return retrieve, generate
