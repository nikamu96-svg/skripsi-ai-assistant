import streamlit as st
import pandas as pd
import os
from groq import Groq

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="AI Asisten Judul Skripsi",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Asisten Judul Skripsi")
st.caption("Menggunakan AI Groq (LLaMA 3)")

# =====================================================
# AMBIL GROQ API KEY (PALING AMAN)
# =====================================================
groq_api_key = None

# 1. Coba dari Streamlit Secrets (Cloud)
if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]

# 2. Jika tidak ada, coba dari Environment Variable (Local)
if not groq_api_key:
    groq_api_key = os.getenv("GROQ_API_KEY")

# =====================================================
# STATUS AI
# =====================================================
if not groq_api_key:
    st.error("❌ AI NONAKTIF — GROQ_API_KEY tidak ditemukan")
    st.info(
        "Tambahkan API Key di:\n"
        "- Streamlit Cloud → Settings → Secrets\n"
        "- atau set Environment Variable (local)"
    )
    st.stop()
else:
    st.success("✅ AI AKTIF — GROQ_API_KEY terdeteksi")

# =====================================================
# INISIALISASI CLIENT GROQ
# =====================================================
try:
    client = Groq(api_key=groq_api_key)
except Exception as e:
    st.error("Gagal menginisialisasi Groq Client")
    st.code(str(e))
    st.stop()

# =====================================================
# UPLOAD DATA EXCEL
# =====================================================
uploaded_file = st.file_uploader(
    "Upload data skripsi (.xlsx)",
    type=["xlsx"]
)

if not uploaded_file:
    st.warning("Silakan upload file Excel untuk memulai")
    st.stop()

try:
    df = pd.read_excel(uploaded_file)
except Exception:
    st.error("File Excel tidak valid / rusak")
    st.stop()

if df.empty:
    st.error("Data Excel kosong")
    st.stop()

if "Judul" not in df.columns:
    st.error("Kolom 'Judul' tidak ditemukan di file Excel")
    st.stop()

st.success("📊 Data berhasil dimuat")
st.dataframe(df.head(), use_container_width=True)

# =====================================================
# INPUT TOPIK
# =====================================================
topic = st.text_input(
    "Masukkan topik penelitian",
    placeholder="Contoh: UMKM, e-procurement, audit"
)

if not topic:
    st.stop()

# =====================================================
# PROSES AI
# =====================================================
if st.button("🔍 Analisis Judul"):

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

Buatkan 3 judul skripsi BARU, akademik,
dan relevan dengan topik:
{topic}

Gunakan bahasa Indonesia.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten akademik."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )

        st.success("🎯 Rekomendasi Judul Skripsi")
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error("AI gagal merespons")
        st.code(str(e))
