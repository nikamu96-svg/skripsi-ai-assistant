import streamlit as st
st.error("🚨 INI APP BARU - JIKA MUNCUL, BERHASIL 🚨")
import pandas as pd
import os

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="AI Asisten Penentuan Judul Skripsi",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Asisten Penentuan Judul Skripsi")
st.caption("Berbasis data skripsi terdahulu dan tren penelitian terkini")

# =====================================================
# AMBIL API KEY (TANPA ERROR & TANPA STOP APP)
# =====================================================
groq_api_key = None

try:
    if "GROQ_API_KEY" in st.secrets:
        groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not groq_api_key:
    groq_api_key = os.getenv("GROQ_API_KEY")

client = None
if groq_api_key:
    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key)
    except Exception:
        client = None

# =====================================================
# STATUS AI (INFORMASI SAJA, BUKAN ERROR)
# =====================================================
if client is None:
    st.info("ℹ️ Mode demo aktif (AI nonaktif karena API key belum tersedia)")
else:
    st.success("🤖 AI aktif dan siap digunakan")

# =====================================================
# UPLOAD DATA
# =====================================================
st.header("📂 Upload Data Skripsi Terdahulu")

uploaded_file = st.file_uploader(
    "Upload file Excel (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.warning("Silakan upload file Excel untuk memulai")
    st.stop()

try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

# =====================================================
# VALIDASI KOLOM
# =====================================================
required_columns = [
    "Judul", "Tahun", "Prodi",
    "Variabel", "Metode",
    "Objek", "Lokasi", "Kata_Kunci"
]

missing = [c for c in required_columns if c not in df.columns]
if missing:
    st.error(f"Kolom tidak ditemukan: {missing}")
    st.stop()

# =====================================================
# FILTER
# =====================================================
st.header("🔍 Filter Penelitian")

col1, col2 = st.columns(2)

with col1:
    prodi = st.multiselect(
        "Program Studi",
        options=sorted(df["Prodi"].dropna().unique())
    )

with col2:
    keyword = st.text_input(
        "Topik / Kata Kunci",
        placeholder="Contoh: UMKM, e-procurement, digital marketing"
    )

filtered_df = df.copy()

if prodi:
    filtered_df = filtered_df[filtered_df["Prodi"].isin(prodi)]

if keyword:
    filtered_df = filtered_df[
        filtered_df["Judul"].str.contains(keyword, case=False, na=False) |
        filtered_df["Kata_Kunci"].str.contains(keyword, case=False, na=False)
    ]

# =====================================================
# TAMPILKAN DATA
# =====================================================
st.subheader("📑 Hasil Penelitian")

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai")
else:
    st.dataframe(filtered_df, use_container_width=True)

# =====================================================
# ANALISIS AI (OPSIONAL)
# =====================================================
st.header("🤖 Analisis & Rekomendasi")

if st.button("Analisis Judul Skripsi"):

    if client is None:
        st.warning(
            "AI tidak aktif karena API key belum tersedia.\n\n"
            "Namun aplikasi tetap dapat digunakan untuk eksplorasi data."
        )
        st.stop()

    if filtered_df.empty:
        st.warning("Tidak ada data untuk dianalisis")
        st.stop()

    with st.spinner("AI sedang menganalisis..."):

        context = ""
        for _, row in filtered_df.head(8).iterrows():
            context += f"""
Judul: {row['Judul']}
Tahun: {row['Tahun']}
Variabel: {row['Variabel']}
Metode: {row['Metode']}
---
"""

        prompt = f"""
Anda adalah dosen pembimbing skripsi.

Berdasarkan data penelitian terdahulu berikut:
{context}

Jawablah:
1. Apakah topik "{keyword}" masih relevan?
2. Apakah ada peluang kebaruan?
3. Berikan 3 rekomendasi judul skripsi beserta variabel dan metode.
"""

        try:
            response = client.responses.create(
                model="llama3-8b-8192",
                input=prompt,
                temperature=0.4,
                max_output_tokens=600
            )

            st.success("✅ Analisis selesai")
            st.markdown(response.output_text)

        except Exception as e:
            st.error("Terjadi kesalahan saat memanggil AI")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Aplikasi pendukung penentuan judul skripsi berbasis data & AI")
