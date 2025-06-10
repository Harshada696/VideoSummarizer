# VideoSummarizer

**VideoSummarizer** is a Flask-based web application that allows users to upload educational videos, extract transcripts, generate summaries, extract keywords, and visualize the content flow using a flowchart. It supports user registration/login and includes an admin panel to manage users.

---

## 🚀 Features

- 🎥 Upload video files with audio
- 🔊 Extract audio from video using MoviePy
- 📝 Transcribe audio using OpenAI's Whisper (via faster-whisper)
- 📚 Generate summaries using PEGASUS (Transformers)
- 🧠 Extract keywords using KeyBERT
- 📊 Visualize summaries as flowcharts using Graphviz
- 👤 User authentication (register/login/logout)
- 🛠️ Admin dashboard to manage users

---

## 🧰 Tech Stack

- **Backend**: Flask (Python)
- **Transcription**: faster-whisper
- **Summarization**: PEGASUS via HuggingFace Transformers
- **Keyword Extraction**: KeyBERT
- **Audio Processing**: MoviePy
- **Visualization**: Graphviz
- **Database**: MySQL
- **Authentication**: Flask sessions + Werkzeug hashing

---

## 📁 Project Structure

```videosummerizer/
│
├── uploads/ # Uploaded videos
├── audio/ # Audio files extracted from videos
├── static/ # Flowchart images
├── templates/ # HTML templates (login.html, index.html, admin.html)
├── app.py # Flask application
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```

## 🔐 Admin Login

**Default Admin Credentials:**

Username: admin
Password: admin_password

css

To change these, edit the `app.py` file:

```python
if username == 'admin' and password == 'admin_password':
🧪 Running the App
bash
python app.py
Then open your browser and navigate to:

cpp
http://127.0.0.1:5000
📦 Installation
Prerequisites
Python 3.7+

MySQL Server

FFmpeg (required by MoviePy)

Graphviz (installed and added to system PATH)

Clone and Set Up
bash
git clone https://github.com/yourusername/videosummerizer.git
cd videosummerizer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
🛠️ MySQL Database Setup
Log into MySQL and run:

sql
CREATE DATABASE smarteduhub;
USE smarteduhub;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
Update your MySQL credentials in app.py:

python
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='your_mysql_password',
        database='smarteduhub'
    )
