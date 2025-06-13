from langgraph.graph import START, StateGraph
from retrieve_and_generate import build_chatbot, State
from langchain_core.prompts import PromptTemplate
import os 


# LangSmith sitesinde loglari gormemizi saglar. Hangi cevap hangi documentten geldi? Kac token harcandi? gibi...
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "pirix-chatbot"


retrieve, generate = build_chatbot()
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


print("Uyarı: Daha iyi cevap verebilmesi için lütfen türkçe karakter ve güzel prompt yazmaya özen gösterin.")
print("\nKonuşmadan çıkmak isterseniz 'q' basmanız yeterli.\n")
print("PiriX: Merhabalar, Ben PiriX, senin Yardımcı Asistanınım.\nSana nasıl yardımcı olabilirim?")


while True : 

    question = input("Sen:")
    if question == "q":
        print("PiriX: Görüşmek üzere!")
        break

    result = graph.invoke({"question": question})
    print(f"PiriX: {result['answer']}")

