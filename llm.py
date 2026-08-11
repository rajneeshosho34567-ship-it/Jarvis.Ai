import os
import datetime
from groq import Groq
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except Exception as e:
        return ""

SYSTEM_PROMPT = """You are Jarvis, Mayank's personal AI assistant, speaking fluently in natural Hindi and Hinglish. 

CORE RULES:
1. IDENTITY: Your creator is Mayank, an entrepreneur from Kanpur building Zodack.
2. LANGUAGE: Always respond in natural, conversational Hindi or Hinglish, just like a helpful human assistant.
3. SMART LENGTH: Keep casual answers short and direct. Provide detailed breakdowns only when technical help or strategy is asked.
4. LIVE CAPABILITIES: Use the provided system time and web search results when up-to-date data is required.
"""

def generate_response(user_message: str, context_chunks: list):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    web_context = ""
    if any(word in user_message.lower() for word in ["search", "news", "latest", "batao", "kya hai", "aaj", "price", "time", "date"]):
        search_results = search_web(user_message)
        if search_results:
            web_context = f"\nLive Web Search Results:\n{search_results}"

    context_text = "\n---\n".join(context_chunks) if context_chunks else "No prior memory context."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Context:\n- Time: {current_time}\n- User: Mayank (Kanpur)\n- Business: Zodack{web_context}\n\nMemory:\n{context_text}"},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3,
        max_tokens=800
    )
    return response.choices[0].message.content

def transcribe_audio(audio_bytes):
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model="whisper-large-v3-turbo",
            language="hi"
        )
        return transcription.text
    except:
        return ""