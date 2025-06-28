from flask import Flask, request, jsonify, render_template
from langgraph.graph import START, StateGraph
from retrieve_and_generate import build_chatbot, State
from dotenv import load_dotenv
import os

# Ortam değişkenlerini yükle
load_dotenv()

# LangSmith izleme/loglama ayarları
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "pirix-chatbot"

app = Flask(__name__, static_folder='static', template_folder='templates')

# Chatbot iş akışını kur
retrieve, generate = build_chatbot()
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# Ana sayfa: index.html render edilir
@app.route("/")
def home():
    return render_template("index.html")

# Kullanıcıdan gelen soruları alır ve cevap döner
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question.strip():
        return jsonify({"answer": "Lütfen geçerli bir soru yazın."})

    result = graph.invoke({"question": question})
    return jsonify({"answer": result["answer"]})

# Flask uygulamasını başlat
if __name__ == "__main__":
    app.run(debug=True)
