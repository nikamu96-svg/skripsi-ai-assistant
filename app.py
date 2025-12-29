import streamlit as st
import pandas as pd
import os

# ===============================
# KONFIGURASI HALAMAN
# ===============================
st.set_page_config(
    page_title="AI Asisten Judul Skripsi",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Asisten Judul Skripsi")
st.caption("Berbasis data skripsi terdahulu dan AI Groq")

# ===============================
# STATUS APLIKASI
# ===============================
st.info("Mode stabil aktif")

# ===============================
# LOAD DATA EXCEL
# ===============================
uploaded_file = st.file_uploader(
    "Upload data skripsi (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.warning("Silakan upload file Excel untuk memulai")
    st.stop()

try:
    df = pd.read_excel(uploaded_file)
except Exception:
    st.error("File Excel tidak dapat dibaca. Pastikan format .xlsx benar.")
    st.stop()

if df.empty:
    st.error("Data Excel kosong.")
    st.stop()

st.success("Data berhasil dimuat")
st.dataframe(df.head(), use_container_width=True)

# ===============================
# INPUT TOPIK
# ===============================
topic = st.text_input(
    "Masukkan topik penelitian",
    placeholder="Contoh: e-procurement, UMKM, audit"
)

if not topic:
    st.warning("Masukkan topik penelitian terlebih dahulu")
    st.stop()

# ===============================
# CEK API KEY GROQ (AMAN)
# ===============================
groq_api_key = (
    st.secrets.get("GROQ_API_KEY")
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets
    else os.getenv("GROQ_API_KEY")
)

ai_ready = bool(groq_api_key)

if ai_ready:
    st.success("AI AKTIF (Groq API terdeteksi)")
else:
    st.warning("AI nonaktif (GROQ_API_KEY belum tersedia)")

# ===============================
# TOMBOL ANALISIS
# ===============================
if st.button("🔍 Analisis Judul"):

    if not ai_ready:
        st.error("AI tidak aktif. Tambahkan GROQ_API_KEY di Secrets / .env")
        st.stop()

    # Import di dalam button agar lebih aman
    from groq import Groq

    try:
        client = Groq(api_key=groq_api_key)
    except Exception:
        st.error("Gagal menginisialisasi Groq client")
        st.stop()

    # ===============================
    # KONTEKS DATA
    # ===============================
    if "Judul" not in df.columns:
        st.error("Kolom 'Judul' tidak ditemukan di Excel")
        st.stop()

    context = "\n".join(
        df["Judul"]
        .dropna()
        .astype(str)
        .head(10)
        .tolist()
    )

    prompt = f"""
Anda adalah dosen pembimbing skripsi.

Berikut contoh judul skripsi terdahulu:
{context}

Buatkan 3 judul skripsi BARU, akademik, dan relevan
dengan topik:
{topic}

Formatkan dalam bentuk daftar bernomor.
"""

    # ===============================
    # PANGGIL AI GROQ
    # ===============================
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten akademik."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )

        st.success("✅ Rekomendasi Judul dari AI")
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error("AI gagal merespons.")
        st.code(str(e))
