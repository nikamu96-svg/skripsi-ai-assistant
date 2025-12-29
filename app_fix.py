import streamlit as st
import os

st.set_page_config(page_title="TEST GROQ", layout="wide")
st.title("TEST GROQ API KEY")

groq_api_key = None

try:
    groq_api_key = st.secrets.get("GROQ_API_KEY")
except Exception:
    groq_api_key = None

if not groq_api_key:
    groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.warning("API Key belum ada, silakan input manual")
    groq_api_key = st.text_input("Masukkan GROQ API Key", type="password")
    if not groq_api_key:
        st.stop()

st.success("API Key terdeteksi / diinput dengan benar ✅")
