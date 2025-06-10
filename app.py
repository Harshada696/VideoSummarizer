from flask import Flask, request, render_template, send_file, redirect, session, url_for, flash
import os
import uuid
import json
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel
from nltk.tokenize import sent_tokenize
from keybert import KeyBERT
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from graphviz import Digraph
import torch
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# --- Configs ---
UPLOAD_FOLDER = "uploads"
AUDIO_FOLDER = "audio"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Graphviz path (for Windows)
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# --- DB Connection ---
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='harshu',
        database='smarteduhub'
    )

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return wrapper

# Models
kw_model = KeyBERT()
tokenizer = AutoTokenizer.from_pretrained("google/pegasus-xsum")
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained("google/pegasus-xsum")

# --- Utils ---
def chunk_text(text, max_chunk_length=500):
    sentences = sent_tokenize(text)
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_length:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def summarize_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="longest").to(summarizer_model.device)
    with torch.no_grad():
        summary_ids = summarizer_model.generate(inputs["input_ids"], max_length=120, min_length=40, num_beams=4)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def format_summary_as_bullets(summary):
    sentences = sent_tokenize(summary)
    return "\n".join(f"{i+1}. {s}" for i, s in enumerate(sentences))

def extract_keywords(text, top_n=5):
    keywords = kw_model.extract_keywords(text, top_n=top_n)
    return [kw[0] for kw in keywords]

def create_summary_flowchart(summary_text):
    dot = Digraph()
    lines = [line.strip() for line in summary_text.strip().split('\n') if line.strip()]
    filename = f"summary_flowchart_{uuid.uuid4().hex}"
    filepath = os.path.join(STATIC_FOLDER, filename)

    for i, line in enumerate(lines):
        node_id = f"N{i}"
        dot.node(node_id, line)
        if i > 0:
            dot.edge(f"N{i-1}", node_id)

    dot.render(filepath, format="png", cleanup=True)
    return filepath + ".png"

# --- Routes ---
@app.route('/')
@login_required
def index():
    return render_template("index.html", transcript="", summary="", flowchart=None)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Admin login check
        if username == 'admin' and password == 'admin_password':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))

        # Regular user login
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash("Invalid login.")
            return redirect(url_for('login_page'))

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        conn.commit()
        flash("Registration successful! Please login.")
        return redirect(url_for('login_page'))
    except mysql.connector.IntegrityError:
        flash("Username already exists.")
        return redirect(url_for('login_page'))
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route("/upload", methods=["POST"])
@login_required
def upload_video():
    if "file" not in request.files or request.files["file"].filename == "":
        return render_template("index.html", transcript="", summary="", flowchart=None)

    file = request.files["file"]
    unique_id = uuid.uuid4().hex
    video_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{file.filename}")
    audio_filename = f"{unique_id}.wav"
    audio_path = os.path.join(AUDIO_FOLDER, audio_filename)

    file.save(video_path)

    try:
        video = VideoFileClip(video_path)
        if not video.audio:
            return render_template("index.html", transcript="", summary="No audio found in video.", flowchart=None)

        video.audio.write_audiofile(audio_path, codec="pcm_s16le")

        model = WhisperModel("tiny")
        segments, _ = model.transcribe(audio_path)

        transcript, all_text = "", ""
        for segment in segments:
            start = int(segment.start)
            timestamp = f"[{start // 60}:{start % 60:02d}]"
            text = segment.text.strip()
            transcript += f"{timestamp} {text}\n"
            all_text += " " + text

        chunks = chunk_text(all_text)
        raw_summaries = [summarize_text(chunk) for chunk in chunks]
        combined_summary = " ".join(raw_summaries)
        bullet_summary = format_summary_as_bullets(combined_summary)

        keywords = extract_keywords(all_text)
        keyword_str = ", ".join(keywords)
        final_summary = f"{bullet_summary}\n\n**Keywords:** {keyword_str}"

        flowchart_image = create_summary_flowchart(bullet_summary)

        return render_template("index.html", transcript=transcript, summary=final_summary, flowchart=flowchart_image)

    except Exception as e:
        print(f"Error: {e}")
        return render_template("index.html", transcript="", summary="An error occurred.", flowchart=None)

# --- Admin Dashboard ---
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('login_page'))

@app.route('/api/users')
@admin_required
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return json.dumps(users)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return '', 204

# --- Run App ---
if __name__ == "__main__":
    app.run(debug=True)
