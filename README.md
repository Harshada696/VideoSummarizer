# VideoSummarizer

VideoSummarizer is a Flask-based web application that allows users to upload educational videos, extract transcripts, generate summaries, extract keywords, and visualize the content flow using a flowchart. It supports user registration/login and includes an admin panel to manage users.

---

## 🚀 Features

- 🎥 Upload video files with audio
- 🔊 Extract audio from video using MoviePy
- 📝 Transcribe audio using OpenAI's Whisper
- 📚 Generate summaries using PEGASUS (transformers)
- 🧠 Extract keywords using KeyBERT
- 📊 Visualize summaries as flowcharts (Graphviz)
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

📁 Project Structure
Videosummerizer/
│
├── uploads/           # Uploaded videos
├── audio/             # Audio files extracted from video
├── static/            # Flowchart images
├── templates/         # HTML templates
├── app.py             # Flask application
├── requirements.txt   # Python dependencies
└── README.md          # Documentation
---
🔐 Admin Login
txt
Copy
Edit
Username: admin
Password: admin_password
Edit app.py to change this:

python
Copy
Edit
if username == 'admin' and password == 'admin_password':
---
🧪 Running the App
bash
Copy
Edit
python app.py
Navigate to: http://127.0.0.1:5000
---

## 📦 Installation

### Prerequisites

- Python 3.7+
- MySQL Server
- Graphviz (with PATH set)
- FFmpeg (required by MoviePy)

### Clone and Set Up

```bash
git clone https://github.com/yourusername/smarteduhub.git
cd smarteduhub
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt

