import streamlit as st
import pandas as pd
from groq import Groq

# ===============================
# KONFIGURASI HALAMAN
# ===============================
st.set_page_config(
    page_title="AI Asisten Skripsi",
    layout="wide"
)

st.title("🎓 AI Asisten Penentuan Judul Skripsi")
st.write("Berbasis data skripsi terdahulu dan tren penelitian terkini")

# ===============================
# API KEY GROQ
# ===============================
client = Groq(
    api_key="ISI_API_KEY_GROQ_KAMU_DI_SINI"
)

# ===============================
# UPLOAD DATA
# ===============================
st.subheader("📂 Upload Data Skripsi Terdahulu")

uploaded_file = st.file_uploader(
    "Upload file Excel (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Silakan upload data skripsi terlebih dahulu")
    st.stop()

df = pd.read_excel(uploaded_file)
st.success("Data berhasil dimuat")

# ===============================
# PILIH PROGRAM STUDI
# ===============================
st.subheader("🎯 Pilih Program Studi")

prodi_list = df["Prodi"].dropna().unique()
selected_prodi = st.multiselect(
    "Centang Program Studi",
    prodi_list
)

if not selected_prodi:
    st.warning("Pilih minimal satu program studi")
    st.stop()

# ===============================
# INPUT TOPIK
# ===============================
st.subheader("📝 Topik Penelitian")

topik = st.text_input(
    "Masukkan topik atau kata kunci penelitian"
)

if not topik:
    st.stop()

# ===============================
# FILTER DATA
# ===============================
filtered_df = df[
    (df["Prodi"].isin(selected_prodi)) &
    (
        df["Judul"].str.contains(topik, case=False, na=False) |
        df["Kata_Kunci"].str.contains(topik, case=False, na=False)
    )
]

if filtered_df.empty:
    st.error("Tidak ditemukan skripsi yang sesuai")
    st.stop()

# ===============================
# RINGKASAN DATA
# ===============================
jumlah = len(filtered_df)
tahun_min = filtered_df["Tahun"].min()
tahun_max = filtered_df["Tahun"].max()
variabel_umum = filtered_df["Variabel"].value_counts().head(3).to_dict()
metode_umum = filtered_df["Metode"].value_counts().head(3).to_dict()

# ===============================
# PROMPT UNTUK GROQ
# ===============================
prompt = f"""
Anda adalah asisten akademik untuk mahasiswa.

Informasi penelitian terdahulu:
- Program Studi: {', '.join(selected_prodi)}
- Topik: {topik}
- Jumlah skripsi: {jumlah}
- Rentang tahun: {tahun_min}–{tahun_max}
- Variabel dominan: {variabel_umum}
- Metode dominan: {metode_umum}

Tugas Anda:
1. Nilai kelayakan topik penelitian.
2. Tentukan status: Direkomendasikan / Perlu Modifikasi / Tidak Direkomendasikan.
3. Berikan alasan akademik yang jelas.
4. Bandingkan dengan tren penelitian terkini.
5. Usulkan satu judul penelitian yang relevan dan realistis untuk skripsi S1.
"""

# ===============================
# ANALISIS AI
# ===============================
if st.button("🔍 Analisis Penelitian"):
    with st.spinner("AI sedang menganalisis..."):
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        hasil = response.choices[0].message.content

    st.subheader("📌 Hasil Analisis AI")
    st.write(hasil)
