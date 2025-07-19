from flask import Flask, request, jsonify, render_template, session
from langgraph.graph import START, StateGraph
from retrieve_and_generate import build_chatbot, State
from dotenv import load_dotenv
import os
import sqlite3
import uuid
from flask_cors import CORS


# Ortam değişkenlerini yükle
load_dotenv()

# LangSmith izleme/loglama ayarları
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_PROJECT"] = "pirix-chatbot"

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)


# Secret key'i .env'den al, yoksa fallback yap
secret_key = os.getenv("FLASK_SECRET_KEY")
if not secret_key:
    print("WARNING: FLASK_SECRET_KEY environment variable not found. Using default insecure secret key.")
    secret_key = "supersecretkey"

app.secret_key = secret_key


@app.before_request
def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4)

# Veritabanı başlatma (eğer yoksa tabloyu oluşturur)
def init_db():
    conn = sqlite3.connect('chatbot_feedback.db',timeout=5000)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            feedback_type TEXT DEFAULT 'pending',  -- Varsayılan değer eklendi
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_ip TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# Chatbot iş akışını kur
retrieve, generate = build_chatbot()
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question.strip():
        return jsonify({"answer": "Lütfen geçerli bir soru yazın."})

    result = graph.invoke({"question": question})
    session_id = session.get("session_id")

    # Her soruyu kaydet
    feedback_id = None
    try:
        conn = sqlite3.connect('chatbot_feedback.db',timeout=5000)
        cursor = conn.cursor()
        
        print(f"Veritabanına kaydediliyor: session_id={session_id}, question={question[:5000]}...")
        
        # feedback_type artık 'pending' olarak başlıyor
        cursor.execute('''
            INSERT INTO feedback (session_id, question, answer, feedback_type, user_ip)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, question, result["answer"], 'pending', request.remote_addr))
        
        feedback_id = cursor.lastrowid
        print(f"Veritabanında oluşturulan ID: {feedback_id}")
        
        conn.commit()
        conn.close()
        
        print(f"Soru başarıyla kaydedildi - ID: {feedback_id}")
        
    except Exception as e:
        print(f"Feedback kayıt hatası: {e}")
        print(f"Hata detayı: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    print(f"Frontend'e gönderilecek feedback_id: {feedback_id}")
    
    return jsonify({
        "answer": result["answer"],
        "conversation_id": session_id,
        "question": question,
        "feedback_id": feedback_id
    })

@app.route("/feedback", methods=["POST"])
def save_feedback():
    try:
        data = request.get_json()
        feedback_id = data.get("feedback_id")
        feedback_type = data.get("feedback_type")

        if not feedback_id or not feedback_type:
            return jsonify({"error": "feedback_id ve feedback_type gerekli"}), 400

        conn = sqlite3.connect('chatbot_feedback.db',timeout=5000)
        cursor = conn.cursor()

        # ID ile direkt güncelle
        cursor.execute('''
            UPDATE feedback 
            SET feedback_type = ? 
            WHERE id = ?
        ''', (feedback_type, feedback_id))

        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()

        if updated_rows > 0:
            print(f"Feedback güncellendi - ID: {feedback_id}, Type: {feedback_type}")
            return jsonify({"success": True, "message": "Feedback kaydedildi"})
        else:
            return jsonify({"error": "Kayıt bulunamadı"}), 404

    except Exception as e:
        print(f"Feedback güncelleme hatası: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/feedback-stats")
def feedback_stats():
    try:
        conn = sqlite3.connect('chatbot_feedback.db',timeout=5000)
        cursor = conn.cursor()

        # Toplam kayıt sayısı
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_questions = cursor.fetchone()[0]

        # Feedback türlerine göre sayım
        cursor.execute("SELECT feedback_type, COUNT(*) FROM feedback WHERE feedback_type != 'pending' GROUP BY feedback_type")
        feedback_counts = dict(cursor.fetchall())

        # Feedback verilmeyen kayıtlar (pending olanlar)
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE feedback_type = 'pending'")
        pending_feedback_count = cursor.fetchone()[0]

        # Son 10 kayıt
        cursor.execute('''
            SELECT id, question, answer, feedback_type, timestamp 
            FROM feedback 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_feedback = cursor.fetchall()

        conn.close()

        return jsonify({
            "total_questions": total_questions,
            "feedback_counts": feedback_counts,
            "pending_feedback_count": pending_feedback_count,
            "recent_feedback": recent_feedback
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Debug için - veritabanı durumunu kontrol et
@app.route("/debug-db")
def debug_db():
    try:
        conn = sqlite3.connect('chatbot_feedback.db',timeout=5000)
        cursor = conn.cursor()
        
        # Tablo var mı kontrol et
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
        table_exists = cursor.fetchone()
        
        # Toplam kayıt sayısı
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_count = cursor.fetchone()[0]
        
        # Son 5 kayıt
        cursor.execute("SELECT * FROM feedback ORDER BY timestamp DESC LIMIT 5")
        recent_records = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            "table_exists": table_exists is not None,
            "total_records": total_count,
            "recent_records": recent_records
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/debug-feedback")
def debug_feedback():
    try:
        conn = sqlite3.connect('chatbot_feedback.db',timeout=5000)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback ORDER BY timestamp DESC")
        all_feedback = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "all_feedback": all_feedback,
            "count": len(all_feedback)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


crt_path="./pirireis.edu.tr.crt.key"
key_path="./pirireis.edu.tr.key"



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=443, ssl_context=(crt_path,key_path))
