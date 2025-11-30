import streamlit as st
import sys
import time
import Speech_to_Text
import Agent
import RAG
from Text_to_Speech import speak_text_from_file
import streamlit_mic_recorder as mic_recorder


def write_to_say(context):
    try:
        with open("to_say.txt", "w", encoding="utf-8") as f:
            f.write(context)
    except Exception as e:
        print(f"Error writing to 'to_say.txt': {e}")
        st.error(f"Error writing file: {e}")

@st.cache_resource
def initial_setup():
    print("--- ONE-TIME SETUP ---")
    print("Running RAG ingestion...")
    RAG.run_ingestion()
    print("Loading embedding model...")
    embeddings = RAG.get_embedding_model()
    print("--- Setup Complete ---")
    return embeddings

st.set_page_config(page_title="دستیار رباتیک IUT", layout="centered")
st.title("🤖 دستیار مسابقات رباتیک IUT")

embedding_model = initial_setup()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message["role"] == "assistant" and "video" in message:
            st.video(message["video"], loop=True, autoplay=True, muted=True)
            st.audio(message["audio"], autoplay=True)

st.write("---")
if st.button("🎙️ برای پرسیدن سوال کلیک کنید (یا نگه دارید)"):
    
    final_answer = ""
    user_question = ""
    
    with st.spinner("🎧 در حال شنیدن..."):
        user_question = Speech_to_Text.speech_to_text()

    if user_question:
        st.chat_message("user").markdown(user_question)
        st.session_state.messages.append({"role": "user", "content": user_question})

        with st.spinner("🧠 در حال پردازش..."):
            route = Agent.route(user_question)
            
            if route == "DOCUMENT":
                context = RAG.query_vector_store(user_question, embedding_model)
                if context is None:
                    final_answer = Agent.generate_general_answer(user_question)
                else:
                    final_answer = Agent.generate_rag_answer(user_question, context)
            
            elif route == "GENERAL":
                final_answer = Agent.generate_general_answer(user_question)

        
        with st.spinner("💬 در حال آماده‌سازی صدا..."):
            write_to_say(final_answer)
            generation_success = speak_text_from_file() 
        if generation_success:
            video_file = "Cute_Robot.mp4"
            audio_file = "Say.mp3"

            with st.chat_message("assistant"):
                st.markdown(final_answer)
                st.video(video_file, loop=True, autoplay=True, muted=True) # ویدیو (بی‌صدا)
                st.audio(audio_file, autoplay=True)
            
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_answer,
                "video": video_file,
                "audio": audio_file
            })
        else:
            st.error("خطا در تولید فایل صوتی.")

    else:
        st.warning("صدایی شنیده نشد. لطفاً دوباره تلاش کنید.")
