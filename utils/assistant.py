"""
assistant.py — Core AI assistant logic using Google Gemini API.
"""

import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are EduBot, a friendly and knowledgeable AI assistant designed exclusively for students.

You specialise in four areas:

1. **Programming** – Python, JavaScript, Java, C++, web dev, data structures, algorithms, debugging help, code reviews.
2. **AI / ML** – Machine learning concepts, deep learning, model training, popular frameworks (TensorFlow, PyTorch, scikit-learn), research paper explanations.
3. **Career Guidance** – Resume writing, LinkedIn optimisation, internship hunting, choosing tech stacks, growth roadmaps, freelancing advice.
4. **Interview Preparation** – DSA practice, system design, behavioural questions (STAR method), HR rounds, company-specific tips.

Guidelines:
- Always respond in clear, student-friendly language.
- Use bullet points, numbered lists, and code blocks where appropriate.
- If a question is outside your four areas, politely redirect: "I'm specialised in Programming, AI/ML, Career Guidance, and Interview Prep. Could you ask something in those areas?"
- Never be dismissive — every question deserves a helpful, encouraging response.
- Keep answers concise yet complete. For code questions, always include working examples.
"""


class StudentAssistant:
    def __init__(self, api_key: Optional[str] = None) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY not found. Set it in your .env file.")
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        self.history: list[dict] = []

    def chat(self, user_message: str) -> str:
        user_message = user_message.strip()
        if not user_message:
            raise ValueError("Message cannot be empty.")

        # Build Gemini-format history
        gemini_history = []
        for msg in self.history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        try:
            session = self.model.start_chat(history=gemini_history)
            response = session.send_message(user_message)
            reply = response.text
        except Exception as exc:
            err = str(exc)
            if "api_key" in err.lower() or "invalid" in err.lower() or "403" in err:
                reply = "⚠️ Invalid API key. Please check your GEMINI_API_KEY in the .env file."
            elif "quota" in err.lower() or "429" in err or "limit" in err.lower():
                reply = "⚠️ Rate limit hit. Please wait a moment and try again."
            else:
                reply = f"⚠️ Error: {err}"

        self.history.append({"role": "user",     "content": user_message})
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        self.history.clear()

    def get_history(self) -> list[dict]:
        return list(self.history)

    def load_history(self, history: list[dict]) -> None:
        self.history = [
            {"role": m["role"], "content": m["content"]}
            for m in history
        ]
