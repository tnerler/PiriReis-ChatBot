from flask import Flask, request, jsonify, render_template, session, make_response
from backend.retrieve_and_generate import build_chatbot, State
from dotenv import load_dotenv
import os
import uuid
from flask_cors import CORS
import logging
import traceback
import threading
from flask_pymongo import PyMongo
from datetime import datetime

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

# MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/pirix_chatbot")

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

# MongoDB
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)
db = mongo.db

# Create collections if not exist (MongoDB creates on first insert)

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

        if retrieve is None or generate is None:
            initialize_chatbot()

        data = request.get_json()
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "Soru boş olamaz."}), 400

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

        logger.info(f"Processing question from session {session_id[:8]}...")
        retrieval_result = retrieve(state, session_id=session_id)
        state["context"] = retrieval_result["context"]
        generation_result = generate(state, session_id=session_id)

        # Save to MongoDB
        feedback_doc = {
            "session_id": session_id,
            "question": question,
            "answer": generation_result["answer"],
            "feedback_type": "pending",
            "timestamp": datetime.utcnow(),
            "user_ip": user_ip
        }
        result = db.feedback.insert_one(feedback_doc)
        feedback_id = str(result.inserted_id)
        logger.info(f"Question successfully saved - ID: {feedback_id}")

        # Save session info if not exists
        if db.sessions.count_documents({"session_id": session_id}) == 0:
            db.sessions.insert_one({
                "session_id": session_id,
                "user_ip": user_ip,
                "created_at": datetime.utcnow()
            })

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

from bson import ObjectId

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

        result = db.feedback.update_one(
            {"_id": ObjectId(feedback_id)},
            {"$set": {"feedback_type": feedback_type}}
        )

        if result.modified_count > 0:
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
        total_questions = db.feedback.count_documents({})
        feedback_counts = {doc['_id']: doc['count'] for doc in db.feedback.aggregate([
            {"$match": {"feedback_type": {"$ne": "pending"}}},
            {"$group": {"_id": "$feedback_type", "count": {"$sum": 1}}}
        ])}
        pending_feedback_count = db.feedback.count_documents({"feedback_type": "pending"})
        recent_feedback = list(db.feedback.find({}, {"question": 1, "answer": 1, "feedback_type": 1, "timestamp": 1}).sort("timestamp", -1).limit(10))
        for doc in recent_feedback:
            doc["id"] = str(doc["_id"])
            doc.pop("_id")
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
        total_count = db.feedback.count_documents({})
        recent_records = list(db.feedback.find().sort("timestamp", -1).limit(5))
        for doc in recent_records:
            doc["id"] = str(doc["_id"])
            doc.pop("_id")
        return jsonify({
            "collection_exists": True,
            "total_records": total_count,
            "recent_records": recent_records
        })
    except Exception as e:
        logger.error(f"debug_db error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/debug-feedback")
def debug_feedback():
    try:
        all_feedback = list(db.feedback.find().sort("timestamp", -1))
        for doc in all_feedback:
            doc["id"] = str(doc["_id"])
            doc.pop("_id")
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