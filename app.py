import streamlit as st
import pandas as pd
from groq import Groq

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="AI Asisten Penentuan Judul Skripsi",
    page_icon="🎓",
    layout="wide"
)

# =========================
# VALIDASI API KEY (TANPA UI INPUT)
# =========================
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ_API_KEY belum diatur di Streamlit Secrets")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# =========================
# HEADER
# =========================
st.title("🎓 AI Asisten Penentuan Judul Skripsi")
st.caption("Berbasis skripsi terdahulu dan tren penelitian terkini")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    return pd.read_csv("data_skripsi.csv")

try:
    df = load_data()
except Exception as e:
    st.error("❌ Gagal memuat data_skripsi.csv")
    st.stop()

# =========================
# FILTER SIDEBAR
# =========================
with st.sidebar:
    st.header("🔍 Filter Penelitian")

    prodi = st.multiselect(
        "Program Studi",
        options=sorted(df["Prodi"].dropna().unique())
    )

    metode = st.multiselect(
        "Metode Penelitian",
        options=sorted(df["Metode"].dropna().unique())
    )

# =========================
# FILTER DATA
# =========================
filtered_df = df.copy()

if prodi:
    filtered_df = filtered_df[filtered_df["Prodi"].isin(prodi)]

if metode:
    filtered_df = filtered_df[filtered_df["Metode"].isin(metode)]

# =========================
# TAMPILKAN DATA
# =========================
st.subheader("📚 Data Skripsi Terdahulu")
st.dataframe(filtered_df, use_container_width=True)

# =========================
# INPUT PERTANYAAN
# =========================
st.subheader("✍️ Konsultasi Judul Skripsi")

user_question = st.text_area(
    "Masukkan topik atau minat penelitian Anda:",
    height=120,
    placeholder="Contoh: pengaruh digitalisasi terhadap kinerja keuangan UMKM"
)

# =========================
# PROSES AI
# =========================
if st.button("🚀 Analisis & Rekomendasi Judul"):

    if user_question.strip() == "":
        st.warning("⚠️ Pertanyaan tidak boleh kosong")
        st.stop()

    if filtered_df.empty:
        st.warning("⚠️ Data kosong setelah filter")
        st.stop()

    # =========================
    # BATASI CONTEXT (AMAN TOKEN)
    # =========================
    context = ""
    for _, row in filtered_df.head(10).iterrows():
        context += f"""
Judul: {row['Judul']}
Tahun: {row['Tahun']}
Variabel: {row['Variabel']}
Metode: {row['Metode']}
---
"""

    prompt = f"""
Anda adalah dosen pembimbing skripsi yang berpengalaman.

Gunakan referensi skripsi berikut sebagai bahan pertimbangan:
{context}

Tugas Anda:
1. Memberikan 3 rekomendasi judul skripsi
2. Setiap judul disertai variabel, metode, dan objek penelitian
3. Judul harus relevan, akademik, dan layak diteliti

Pertanyaan mahasiswa:
{user_question}
"""

    # =========================
    # PANGGIL GROQ (ENDPOINT BARU)
    # =========================
    try:
        response = client.responses.create(
            model="llama3-8b-8192",
            input=prompt,
            temperature=0.4,
            max_output_tokens=600
        )

        result = response.output_text

        st.success("✅ Rekomendasi Berhasil Dibuat")
        st.markdown(result)

    except Exception as e:
        st.error("❌ Terjadi kesalahan saat memanggil AI")
        st.stop()
