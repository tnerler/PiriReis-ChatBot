from flask import Flask, request, jsonify, render_template, session, make_response
from retrieve_and_generate import build_chatbot, State
from dotenv import load_dotenv
import os
import sqlite3
import uuid
from flask_cors import CORS
import logging
import traceback
import threading

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('chatbot.log')
    ]
)
logger = logging.getLogger(__name__)

print("Script Çalışıyor")
load_dotenv()

# Set environment variables for LangChain
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "pirix-chatbot"

app = Flask(
    __name__,
    static_folder="../client/assets",
    template_folder="../client"
)
CORS(app)

secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
app.secret_key = secret_key

DB_PATH = 'database/chatbot_feedback.db'

# Ensure directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                feedback_type TEXT DEFAULT 'pending',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_ip TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_ip TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        traceback.print_exc()

init_db()

# Create a lock for chatbot initialization
chatbot_lock = threading.Lock()
retrieve = None
generate = None

def initialize_chatbot():
    global retrieve, generate
    with chatbot_lock:
        if retrieve is None or generate is None:
            logger.info("Initializing chatbot...")
            try:
                retrieve, generate = build_chatbot()
                logger.info("Chatbot initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing chatbot: {e}")
                traceback.print_exc()
                raise e

# Initialize chatbot in a separate thread to not block app startup
threading.Thread(target=initialize_chatbot).start()

@app.before_request
def ensure_session_id():
    # Check both session and cookie, create if needed
    session_id = request.cookies.get("session_id") or session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        global retrieve, generate
        
        # Ensure chatbot is initialized
        if retrieve is None or generate is None:
            initialize_chatbot()
            
        data = request.get_json()
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "Soru boş olamaz."}), 400

        # Get session ID from cookie or session
        user_ip = request.remote_addr
        session_id = data.get("session_id") or request.cookies.get("session_id") or session.get("session_id")
        
        if not session_id:
            session_id = str(uuid.uuid4())
            session["session_id"] = session_id

        # Create state
        state = {
            "question": question,
            "context": [],
            "answer": ""
        }

        # Retrieve and Generate
        logger.info(f"Processing question from session {session_id[:8]}...")
        retrieval_result = retrieve(state, session_id=session_id)
        state["context"] = retrieval_result["context"]
        generation_result = generate(state, session_id=session_id)

        # Save to database
        feedback_id = None
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (session_id, question, answer, feedback_type, user_ip)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, question, generation_result["answer"], 'pending', user_ip))
            feedback_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Question successfully saved - ID: {feedback_id}")
        except Exception as db_e:
            logger.error(f"Database error: {db_e}")
            traceback.print_exc()

        # Prepare response
        response_data = {
            "answer": generation_result["answer"],
            "feedback_id": feedback_id,
            "conversation_id": session_id,
            "question": question,
            "session_id": session_id
        }
        
        response = make_response(jsonify(response_data))
        
        # Set session ID cookie if not exists
        if not request.cookies.get("session_id"):
            response.set_cookie("session_id", session_id, max_age=30*24*60*60)
            
        return response
        
    except Exception as e:
        logger.error(f"Ask endpoint error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/feedback", methods=["POST"])
def save_feedback():
    try:
        logger.info(f"Feedback request body: {request.data}")
        data = request.get_json()
        feedback_id = data.get("feedback_id")
        feedback_type = data.get("feedback_type")
        session_id = data.get("session_id") or request.cookies.get("session_id") or session.get("session_id")

        logger.info(f"Feedback ID: {feedback_id}, Feedback Type: {feedback_type}")

        if not feedback_id:
            return jsonify({"error": "feedback_id gerekli"}), 400
        if feedback_type not in ("like", "dislike"):
            return jsonify({"error": "Geçersiz feedback türü (like/dislike olmalı)."}), 400

        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE feedback 
            SET feedback_type = ? 
            WHERE id = ?
        ''', (feedback_type, feedback_id))
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()

        if updated_rows > 0:
            logger.info(f"Feedback updated - ID: {feedback_id}, Type: {feedback_type}")
            return jsonify({
                "success": True,
                "message": "Feedback kaydedildi",
                "status": "success",
                "feedback_id": feedback_id
            })
        else:
            logger.error(f"Feedback record not found: {feedback_id}")
            return jsonify({"error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        logger.error(f"Feedback endpoint error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/feedback-stats")
def feedback_stats():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_questions = cursor.fetchone()[0]
        cursor.execute("SELECT feedback_type, COUNT(*) FROM feedback WHERE feedback_type != 'pending' GROUP BY feedback_type")
        feedback_counts = dict(cursor.fetchall())
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE feedback_type = 'pending'")
        pending_feedback_count = cursor.fetchone()[0]
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
        logger.error(f"feedback_stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/debug-db")
def debug_db():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
        table_exists = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_count = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM feedback ORDER BY timestamp DESC LIMIT 5")
        recent_records = cursor.fetchall()
        conn.close()
        return jsonify({
            "table_exists": table_exists is not None,
            "total_records": total_count,
            "recent_records": recent_records
        })
    except Exception as e:
        logger.error(f"debug_db error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/debug-feedback")
def debug_feedback():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback ORDER BY timestamp DESC")
        all_feedback = cursor.fetchall()
        conn.close()
        return jsonify({
            "all_feedback": all_feedback,
            "count": len(all_feedback)
        })
    except Exception as e:
        logger.error(f"debug_feedback error: {e}")
        return jsonify({"error": str(e)}), 500

# SSL certificate paths
crt_path = "./keys/pirireis.edu.tr.crt.key"
key_path = "./keys/pirireis.edu.tr.key"

if __name__ == "__main__":
    # Check for SSL certificates
    if os.path.exists(crt_path) and os.path.exists(key_path):
        app.run(host="0.0.0.0", port=443, ssl_context=(crt_path, key_path))
    else:
        logger.warning("SSL certificates not found, running in development mode")
        app.run(host="0.0.0.0", port=5000, debug=True)