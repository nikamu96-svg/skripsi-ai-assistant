import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="AI Asisten Judul Skripsi",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Asisten Judul Skripsi")

# ===============================
# STATUS & MODE
# ===============================
st.info("Mode stabil aktif")

# ===============================
# LOAD DATA
# ===============================
uploaded_file = st.file_uploader(
    "Upload data skripsi (.xlsx)",
    type=["xlsx"]
)

if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)

st.dataframe(df.head(), use_container_width=True)

# ===============================
# INPUT USER
# ===============================
topic = st.text_input(
    "Masukkan topik penelitian",
    placeholder="Contoh: e-procurement, UMKM, audit"
)

# ===============================
# CEK API KEY (TANPA ERROR)
# ===============================
groq_api_key = (
    st.secrets.get("GROQ_API_KEY")
    if hasattr(st, "secrets")
    else os.getenv("GROQ_API_KEY")
)

ai_ready = bool(groq_api_key)

if ai_ready:
    st.success("AI siap digunakan")
else:
    st.warning("AI nonaktif (API Key belum tersedia)")

# ===============================
# PROSES AI
# ===============================
if st.button("Analisis Judul"):

    if not ai_ready:
        st.warning("AI tidak aktif. Tambahkan GROQ_API_KEY untuk mengaktifkan.")
        st.stop()

    from groq import Groq
    client = Groq(api_key=groq_api_key)

    context = "\n".join(
        df["Judul"].astype(str).head(5).tolist()
    )

    prompt = f"""
Anda adalah dosen pembimbing skripsi.
Berdasarkan judul berikut:
{context}

Buatkan 3 judul skripsi baru untuk topik:
{topic}
"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )

        st.success("Hasil AI")
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error("AI gagal merespons. Periksa API key / quota.")
