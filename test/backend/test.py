from retrieve_and_generate_test import build_chatbot

if __name__ == "__main__":
    session_id = "1"  # sabit session
    retrieve, generate = build_chatbot()
    print(f"Yeni Oturum: {session_id}")

    while True:
        question = input("\nSoru (çıkmak için q): ")
        if question.lower() == 'q':
            print("\n[✓] Görüşme sonlandırıldı.")
            break

        state = {"question": question}
        retrieved = retrieve(state, session_id)  # ← Eksik olan argüman eklendi
        response = generate(retrieved, session_id)
        print("\n[PiriX]:", response["answer"])
