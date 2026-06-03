"""
app.py — Main Streamlit application for the AI Student Query Assistant.

Run with:
    streamlit run app.py
"""

import os
import sys

import streamlit as st
from dotenv import load_dotenv

# ── Make sure sibling packages are importable when running from any directory ──
sys.path.insert(0, os.path.dirname(__file__))

from utils.assistant import StudentAssistant
from utils.auth import register_user, verify_user
from utils.cache import ResponseCache
from utils.logger import append_turn, load_history, save_history

load_dotenv()

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EduBot – Student AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide Streamlit's default top-right toolbar (Deploy, Stop, etc.)
st.markdown("""
<style>
#MainMenu { visibility: hidden; display: none; }
header[data-testid="stHeader"] { display: none; }
.stDeployButton { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Gradient header */
.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(99, 179, 237, 0.2);
}
.main-header h1 { color: #63b3ed; margin: 0; font-size: 2rem; font-weight: 700; }
.main-header p  { color: #a0aec0; margin: 0.3rem 0 0; font-size: 1rem; }

/* Topic pills */
.pill-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.8rem 0 1.2rem; }
.pill {
    background: rgba(99,179,237,0.12);
    color: #63b3ed;
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 20px;
    padding: 0.25rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 600;
}

/* Chat bubbles */
.user-bubble {
    background: linear-gradient(135deg, #2b6cb0, #2c5282);
    color: #fff;
    padding: 0.85rem 1.1rem;
    border-radius: 16px 16px 4px 16px;
    margin: 0.5rem 0 0.5rem 20%;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.bot-bubble {
    background: rgba(26, 32, 44, 0.85);
    color: #e2e8f0;
    padding: 0.85rem 1.1rem;
    border-radius: 16px 16px 16px 4px;
    margin: 0.5rem 20% 0.5rem 0;
    font-size: 0.95rem;
    line-height: 1.6;
    border: 1px solid rgba(99,179,237,0.15);
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.bubble-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    opacity: 0.7;
}

/* Sidebar tweaks */
section[data-testid="stSidebar"] { background: #0d1117; }
section[data-testid="stSidebar"] .stTextInput input {
    background: #161b22;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 8px;
}
section[data-testid="stSidebar"] label { color: #8b949e; }

/* Stat cards */
.stat-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    text-align: center;
    color: #58a6ff;
}
.stat-card .num { font-size: 1.6rem; font-weight: 700; }
.stat-card .lbl { font-size: 0.75rem; color: #8b949e; }

/* Input area */
div[data-testid="stChatInput"] textarea {
    background: #161b22 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "authenticated": False,
        "username": None,
        "assistant": None,
        "cache": ResponseCache(),
        "display_history": [],   # list of {role, content}
        "cache_hits": 0,
        "total_queries": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()


# ─────────────────────────────────────────────
# Helper: Build / restore assistant
# ─────────────────────────────────────────────
def _get_assistant() -> StudentAssistant | None:
    """Return (or lazily create) the StudentAssistant for the current session."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    if st.session_state.assistant is None:
        try:
            asst = StudentAssistant(api_key=api_key)
            # Restore saved history (strip timestamps so API is happy)
            saved = load_history(st.session_state.username)
            if saved:
                asst.load_history(saved)
                st.session_state.display_history = [
                    {"role": m["role"], "content": m["content"]} for m in saved
                ]
            st.session_state.assistant = asst
        except ValueError:
            return None
    return st.session_state.assistant


# ─────────────────────────────────────────────
# AUTH SCREEN
# ─────────────────────────────────────────────
def render_auth() -> None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="main-header" style="text-align:center;">
            <h1>🎓 EduBot</h1>
            <p>Your AI-powered Student Learning Companion</p>
            <div class="pill-row" style="justify-content:center;">
                <span class="pill">💻 Programming</span>
                <span class="pill">🤖 AI / ML</span>
                <span class="pill">🚀 Career Guidance</span>
                <span class="pill">🎯 Interview Prep</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Create Account"])

        with tab_login:
            st.subheader("Welcome back!")
            uname = st.text_input("Username", key="login_user", placeholder="your_username")
            pwd   = st.text_input("Password", type="password", key="login_pwd", placeholder="••••••••")
            if st.button("Login →", use_container_width=True, type="primary"):
                if uname and pwd:
                    ok, msg = verify_user(uname, pwd)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.username = uname
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in both fields.")

        with tab_register:
            st.subheader("Join EduBot")
            new_user = st.text_input("Choose a username", key="reg_user")
            new_pwd  = st.text_input("Choose a password (min 6 chars)", type="password", key="reg_pwd")
            if st.button("Create Account", use_container_width=True, type="primary"):
                ok, msg = register_user(new_user, new_pwd)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# ─────────────────────────────────────────────
# SIDEBAR (authenticated)
# ─────────────────────────────────────────────
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.divider()

        st.divider()

        # Stats
        hits  = st.session_state.cache_hits
        total = st.session_state.total_queries
        msgs  = len(st.session_state.display_history)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="stat-card"><div class="num">{msgs}</div><div class="lbl">Messages</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="stat-card"><div class="num">{hits}</div><div class="lbl">Cache Hits</div></div>""", unsafe_allow_html=True)

        st.divider()

        # Topic shortcuts
        st.markdown("**⚡ Quick Topics**")
        topics = {
            "💻 Python Basics":     "Can you explain Python lists vs tuples with examples?",
            "🤖 ML Roadmap":        "What is the best roadmap to learn Machine Learning in 2024?",
            "📄 Resume Tips":       "What should a fresher's tech resume include?",
            "🎯 DSA Practice":      "Give me a list of must-do LeetCode problems for interviews.",
            "🔥 System Design":     "Explain CAP theorem in simple terms.",
        }
        for label, prompt in topics.items():
            if st.button(label, use_container_width=True):
                st.session_state["_quick_prompt"] = prompt
                st.rerun()

        st.divider()

        col_clear, col_logout = st.columns(2)
        with col_clear:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                if st.session_state.assistant:
                    st.session_state.assistant.reset()
                st.session_state.display_history = []
                save_history(st.session_state.username, [])
                st.session_state.cache_hits = 0
                st.session_state.total_queries = 0
                st.success("Chat cleared!")
                st.rerun()
        with col_logout:
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                _init_state()
                st.rerun()


# ─────────────────────────────────────────────
# CHAT SCREEN
# ─────────────────────────────────────────────
def render_chat() -> None:
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 EduBot — Student Query Assistant</h1>
        <p>Ask me anything about Programming, AI/ML, Career Guidance, or Interview Prep.</p>
        <div class="pill-row">
            <span class="pill">💻 Programming</span>
            <span class="pill">🤖 AI / ML</span>
            <span class="pill">🚀 Career Guidance</span>
            <span class="pill">🎯 Interview Prep</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    assistant = _get_assistant()
    if assistant is None:
        st.warning("⚠️ API key not found. Please add GEMINI_API_KEY in the .env file and restart the app.")
        return

    # Display existing messages
    chat_container = st.container()
    with chat_container:
        if not st.session_state.display_history:
            st.info("👋 Hello! Ask me about programming, AI/ML, career tips, or interview prep. I'm here to help!")
        else:
            for msg in st.session_state.display_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="user-bubble">
                        <div class="bubble-label">You</div>
                        {msg["content"]}
                    </div>""", unsafe_allow_html=True)
                else:
                    # Render markdown inside bot bubble properly
                    with st.container():
                        st.markdown(f"""<div class="bot-bubble"><div class="bubble-label">🎓 EduBot</div>""", unsafe_allow_html=True)
                        st.markdown(msg["content"])
                        st.markdown("</div>", unsafe_allow_html=True)

    # Handle quick-topic button
    prefill = st.session_state.pop("_quick_prompt", None)

    # Chat input
    user_input = st.chat_input("Ask a question…", key="chat_input")
    if prefill:
        user_input = prefill

    if user_input:
        user_input = user_input.strip()
        if not user_input:
            st.warning("Please type a question first.")
            return

        st.session_state.total_queries += 1

        # Check cache
        cached = st.session_state.cache.get(user_input)
        if cached:
            reply = cached
            st.session_state.cache_hits += 1
        else:
            with st.spinner("EduBot is thinking…"):
                reply = assistant.chat(user_input)
            st.session_state.cache.set(user_input, reply)

        # Update display history
        st.session_state.display_history.append({"role": "user",      "content": user_input})
        st.session_state.display_history.append({"role": "assistant",  "content": reply})

        # Persist to disk
        append_turn(st.session_state.username, "user",      user_input)
        append_turn(st.session_state.username, "assistant", reply)

        st.rerun()


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────
def main() -> None:
    if not st.session_state.authenticated:
        render_auth()
    else:
        render_sidebar()
        render_chat()


if __name__ == "__main__":
    main()
