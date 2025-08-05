import openai
from dotenv import load_dotenv

load_dotenv()

def summarize_messages(messages: list, model="gpt-3.5-turbo", max_tokens=200):
    
    prompt = (
    "Aşağıda bir sohbet geçmişi var. Konunun bağlamından kopmamak için, lütfen kullanıcının önceki sorularını ve taleplerini özetle ve her satırda ana bölüm veya konu adını mutlaka belirt. Eğer bir bölüm veya program hakkında konuşuluyorsa, özetin başında bu bölümü açıkça yaz ve sonraki maddelerde tekrar et.\n\n"
    + "\n".join(messages)
    + "\n\nLütfen: Sadece kullanıcı tarafından sorulan soruların ve taleplerin ana başlıklarını ve önemli terimlerini madde madde listele. Detaya girme, gereksiz açıklama ekleme.\n\nÖzet:"
)

    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens = max_tokens,
        temperature=0.2,
    )
    summary = response.choices[0].message.content.strip()
    return summary