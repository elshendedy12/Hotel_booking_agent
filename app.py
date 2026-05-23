import streamlit as st
from dotenv import load_dotenv
import os
import time
from agent import StableBookingAgent
from tools import init_db

# 1. شحن الـ API Key من ملف .env
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

# 2. تهيئة قاعدة البيانات
init_db()

st.set_page_config(page_title=" Hotel Booking Agent", page_icon="🏨", layout="centered")
st.title("🏨 Smart Hotel Booking Assistant ")
st.write("Welcome! I can help you book your room smoothly. (Strictly for Room Bookings)")

# 3. إعداد الـ Agent في الـ Session
if "agent" not in st.session_state:
    if not API_KEY:
        st.error("Please add your `GROQ_API_KEY` to the `.env` file.")
        st.stop()
    st.session_state.agent = StableBookingAgent(user_id="user_101", api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you with your hotel room reservation today?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        def log_callback(log_text):
            with st.sidebar:
                st.info(log_text)

        with st.spinner(" thinking & invoking tools..."):
            try:
                final_reply = st.session_state.agent.chat(user_input, st_callback=log_callback)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.stop()
        
        response_placeholder.write(final_reply)
        st.session_state.messages.append({"role": "assistant", "content": final_reply})