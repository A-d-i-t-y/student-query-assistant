# 🎓 EduBot – AI-Powered Student Query Assistant

A conversational AI assistant that helps students with **Programming**, **AI/ML**, **Career Guidance**, and **Interview Preparation** — powered by the Anthropic Claude API and built with Streamlit.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🤖 AI Responses | Claude-powered answers tailored for students |
| 💬 Chat History | Full multi-turn conversation with context |
| 💾 Persistent Logs | Conversations saved to JSON per user |
| ⚡ Response Cache | Identical questions served instantly (no API call) |
| 🔐 User Auth | Register / login with bcrypt-hashed passwords |
| 🎨 Streamlit UI | Clean, themed chat interface |
| ⚡ Quick Topics | One-click prompts for common questions |

---

## 🗂️ Project Structure

```
student_query_assistant/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── utils/
│   ├── __init__.py
│   ├── assistant.py        # Claude API wrapper + conversation logic
│   ├── auth.py             # User registration & login (bcrypt)
│   ├── cache.py            # In-process response cache
│   └── logger.py           # JSON-based conversation logger
├── components/
│   └── __init__.py
└── logs/                   # Auto-created; stores user history & credentials
```

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/student-query-assistant.git
cd student-query-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

```bash
cp .env.example .env
# Open .env and replace the placeholder with your actual key:
# ANTHROPIC_API_KEY=sk-ant-...
```

> You can also paste the key directly in the sidebar when the app is running — no .env required.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

---

## 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (get one at https://console.anthropic.com) |

---

## 🧠 Architecture Overview

```
User (Browser)
     │
     ▼
app.py  (Streamlit UI)
     │
     ├── utils/auth.py      ← Login / Register (bcrypt)
     ├── utils/assistant.py ← Claude API calls + history management
     ├── utils/cache.py     ← Avoids duplicate API calls
     └── utils/logger.py    ← Saves chats as JSON to logs/
```

1. User authenticates via `auth.py` (credentials in `logs/users.json`).
2. On first message, `assistant.py` initialises a `StudentAssistant` and loads any saved history from `logger.py`.
3. Each query first checks `cache.py`; a cache miss calls the Claude API.
4. Every turn is immediately appended to the user's log file.

---

## 📦 Dependencies

```
streamlit>=1.32.0
anthropic>=0.25.0
python-dotenv>=1.0.0
bcrypt>=4.1.0
```

---

## 🙌 Acknowledgements

Built with [Anthropic Claude](https://www.anthropic.com) and [Streamlit](https://streamlit.io).
