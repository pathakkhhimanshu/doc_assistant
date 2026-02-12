import os
import requests

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/models/"
    "gemini-1.5-flash:generateContent"
)

def rewrite_answer(question: str, raw_answer: str, mode: str = "quick") -> str:
    if not raw_answer.strip():
        return raw_answer

    style = (
        "short, exam-ready explanation"
        if mode == "quick"
        else "clear, structured explanation for study notes"
    )

    prompt = f"""
Rewrite the content below into clean, simple English.

Rules:
- English only
- Do NOT repeat the question
- Do NOT add new information
- Do NOT mention sources
- Remove OCR noise
- Style: {style}

Question:
{question}

Content:
{raw_answer}
"""

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={API_KEY}",
            json=payload,
            timeout=20
        )
        response.raise_for_status()

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    except Exception as e:
        print("Gemini REST rewrite failed:", e)
        return raw_answer

# debug change
