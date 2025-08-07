import os
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not GEMINI_API_KEY:
    raise RuntimeError("Falta GEMINI_API_KEY en variables de entorno")

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel(MODEL_NAME)

async def ask_gemini(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    def _call():
        resp = _model.generate_content(prompt)
        return resp.text.strip() if hasattr(resp, "text") and resp.text else "Sin respuesta."
    return await loop.run_in_executor(None, _call)
