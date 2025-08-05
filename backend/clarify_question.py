import openai
from dotenv import load_dotenv

load_dotenv()

def clarify_question(summary, question, model="gpt-3.5-turbo", max_tokens=100):
    prompt = f"""
        Aşağıda bir kullanıcının önceki konuşma geçmişi ve yeni sorusu verilmiştir.
        Eğer yeni soru önceki konuşmanın devamıysa, soruyu daha açık hale getir.
        Eğer konu değişmişse, sadece yeni soruyu açıklığa kavuştur. Eski konudan bağlam çekme.

        Aşağıda bazı örnekler verilmiştir:

        Örnek 1:
        Geçmiş:
        "Piri Reis Üniversitesi Bilgisayar Mühendisliği hakkında bilgi alabilir miyim?"
        Soru:
        "Akademik kadrosunda kimler var?"
        Netleştirilmiş Soru:
        "Piri Reis Üniversitesi Bilgisayar Mühendisliği bölümünün akademik kadrosunda kimler var?"
        
        Örnek 2:
        Geçmiş:
        "Piri Reis Üniversitesi Bilgisayar Mühendisliği bölümünün akademik kadrosunda kimler var?"
        Soru:
        "rektör kimdir?"
        Netleştirilmiş Soru:
        "Piri Reis Üniversiteninin rektörü kimdir?"

        Şimdi senin örneğine geçelim:
        Geçmiş:
        {summary}

        Soru:
        {question}

        Lütfen yalnızca netleştirilmiş yeni soruyu döndür.
        """

    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens = max_tokens,
        temperature=0.3,
    )
    clarify = response.choices[0].message.content.strip()
    return clarify