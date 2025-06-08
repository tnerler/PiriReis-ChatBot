from langgraph.graph import START, StateGraph
from retrieve_and_generate import build_chatbot, State
from langchain_core.prompts import PromptTemplate
import os 


# LangSmith sitesinde loglari gormemizi saglar. Hangi cevap hangi documentten geldi? Kac token harcandi? gibi...
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "pirix-chatbot"

template = """Soruyu cevaplamak için aşağıdaki bağlam parçalarını kullanın.
Cevabı bilmiyorsanız, bilmediğinizi söyleyin, bir cevap uydurmaya çalışmayın.
Cevabı olabildiğince öz tutun.

Bağlam:
{context}

Soru:
{question}

Cevap:
"""


custom_prompt = PromptTemplate.from_template(template)
retrieve, generate = build_chatbot(custom_prompt)

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

print("PiriX: Merhabalar, Ben PiriX, senin Yardımcı Asistanınım.\nSana nasıl yardımcı olabilirim?")
question = input("Sen:")

result = graph.invoke({"question": question})
print(f"PiriX: {result['answer']}")

print("Context:")
for doc in result["context"]: 
    print("\n", doc.page_content)
