import streamlit as st
from llm import generate_response, transcribe_audio
import asyncio
import edge_tts
import os

st.set_page_config(page_title="Jarvis", page_icon="🧠", layout="centered")
st.title("🧠 Jarvis")

if "messages" not in st.session_state:
    st.session_state.messages = []

# हिंदी बोलने वाली नेचुरल महिला आवाज़ (SwaraNeural)
async def generate_audio(text, output_file="response.mp3"):
    try:
        voice = "hi-IN-SwaraNeural" 
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
    except:
        pass

# साइडबार: क्लिक करने योग्य (Clickable) चैट हिस्ट्री
with st.sidebar:
    st.subheader("📜 Chat History")
    if st.session_state.messages:
        for i, m in enumerate(st.session_state.messages):
            if m["role"] == "user":
                # हर पुरानी चैट को क्लिक करने योग्य बटन बनाया गया है
                if st.button(f"💬 {m['content'][:20]}...", key=f"hist_{i}"):
                    st.info(f"Selected Query: {m['content']}")
    else:
        st.info("No chat history yet.")

    st.markdown("---")
    st.subheader("📥 Add to Knowledge Base")
    note = st.text_area("Paste notes, code, or business docs")
    if st.button("Save to memory") and note:
        @st.cache_resource
        def load_memory():
            from memory import MemoryStore
            return MemoryStore()
        load_memory().add_memory(note, category="note")
        st.success("Saved.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Suno", key=f"audio_{msg['content'][:15]}"):
                try:
                    asyncio.run(generate_audio(msg["content"]))
                    if os.path.exists("response.mp3"):
                        st.audio("response.mp3", format="audio/mp3", autoplay=True)
                except:
                    pass

st.write("🎙️ Bolne ke liye niche mic par click karein:")
audio_file = st.audio_input("MIC")

voice_text = None
if audio_file is not None:
    try:
        with st.spinner("Sun raha hoon..."):
            audio_bytes = audio_file.read()
            voice_text = transcribe_audio(audio_bytes)
        
        if voice_text:
            st.info(f"You said: {voice_text}")
    except Exception as e:
        st.warning("माइक्रोफोन या ऑडियो प्रोसेसिंग में हल्की सी दिक्कत आई, लेकिन ऐप चालू है। आप टाइप भी कर सकते हैं।")

typed_input = st.chat_input("Type here - coding, strategy, notes...")
user_input = voice_text if voice_text else typed_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    @st.cache_resource
    def load_memory():
        from memory import MemoryStore
        return MemoryStore()

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            memory = load_memory()
            context = memory.retrieve_relevant(user_input, k=2)
            reply = generate_response(user_input, context)
            st.markdown(reply)
            
            try:
                asyncio.run(generate_audio(reply))
                if os.path.exists("response.mp3"):
                    st.audio("response.mp3", format="audio/mp3", autoplay=True)
            except:
                pass
            
            memory.add_memory(f"User: {user_input}\nAssistant: {reply}", category="chat")

    st.session_state.messages.append({"role": "assistant", "content": reply})