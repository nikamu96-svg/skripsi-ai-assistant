import streamlit as st
import pandas as pd
import os
from groq import Groq

# ======================================================
# KONFIGURASI HALAMAN
# ======================================================
st.set_page_config(
    page_title="AI Asisten Penentuan Judul Skripsi",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Asisten Penentuan Judul Skripsi")
st.caption("Berbasis data skripsi terdahulu dan tren penelitian terkini")

# ======================================================
# AMBIL GROQ API KEY (TANPA ERROR MERAH)
# ======================================================
groq_api_key = None

if "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]
elif os.getenv("GROQ_API_KEY"):
    groq_api_key = os.getenv("GROQ_API_KEY")

client = None
if groq_api_key:
    client = Groq(api_key=groq_api_key)
else:
    st.warning(
        "⚠️ API Key Groq belum dikonfigurasi. "
        "Fitur AI dinonaktifkan, namun aplikasi tetap bisa digunakan."
    )

# ======================================================
# LOAD DATA SKRIPSI
# ======================================================
st.header("📂 Data Skripsi Terdahulu")

uploaded_file = st.file_uploader(
    "Upload file Excel (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Silakan upload file data skripsi untuk melanjutkan")
    st.stop()

try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Gagal membaca file Excel: {e}")
    st.stop()

# ======================================================
# VALIDASI KOLOM
# ======================================================
required_columns = [
    "Judul", "Tahun", "Prodi",
    "Variabel", "Metode",
    "Objek", "Lokasi", "Kata_Kunci"
]

missing_cols = [c for c in required_columns if c not in df.columns]
if missing_cols:
    st.error(f"Kolom berikut tidak ditemukan: {missing_cols}")
    st.stop()

st.success("✅ Data berhasil dimuat")

# ======================================================
# FILTER INPUT USER
# ======================================================
st.header("🔍 Pencarian Penelitian")

col1, col2 = st.columns(2)

with col1:
    selected_prodi = st.multiselect(
        "Pilih Program Studi",
        options=sorted(df["Prodi"].dropna().unique())
    )

with col2:
    keyword = st.text_input(
        "Masukkan topik / kata kunci penelitian",
        placeholder="Contoh: UMKM, e-procurement, digital marketing"
    )

# ======================================================
# FILTER DATA
# ======================================================
filtered_df = df.copy()

if selected_prodi:
    filtered_df = filtered_df[filtered_df["Prodi"].isin(selected_prodi)]

if keyword:
    filtered_df = filtered_df[
        filtered_df["Judul"].str.contains(keyword, case=False, na=False) |
        filtered_df["Kata_Kunci"].str.contains(keyword, case=False, na=False)
    ]

# ======================================================
# TAMPILKAN DATA
# ======================================================
st.subheader("📑 Hasil Penelitian Terdahulu")

if filtered_df.empty:
    st.warning("Tidak ditemukan penelitian yang sesuai")
else:
    st.dataframe(filtered_df, use_container_width=True)

# ======================================================
# ANALISIS AI (AMAN)
# ======================================================
st.header("🤖 Analisis & Rekomendasi AI")

if st.button("Analisis Kelayakan Penelitian"):

    if client is None:
        st.error("❌ Fitur AI belum aktif karena API Key Groq belum diatur")
        st.stop()

    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data untuk dianalisis")
        st.stop()

    with st.spinner("AI sedang menganalisis..."):

        # Batasi context agar aman token
        context = ""
        for _, row in filtered_df.head(10).iterrows():
            context += f"""
Judul: {row['Judul']}
Tahun: {row['Tahun']}
Prodi: {row['Prodi']}
Variabel: {row['Variabel']}
Metode: {row['Metode']}
Objek: {row['Objek']}
Lokasi: {row['Lokasi']}
Kata Kunci: {row['Kata_Kunci']}
---
"""

        prompt = f"""
Anda adalah dosen pembimbing skripsi yang berpengalaman.

Tugas:
1. Menilai kelayakan topik "{keyword}"
2. Menilai kebaruan penelitian
3. Memberikan rekomendasi judul yang lebih mutakhir
4. Gunakan bahasa akademik yang mudah dipahami mahasiswa

Referensi penelitian terdahulu:
{context}
"""

        try:
            response = client.responses.create(
                model="llama3-8b-8192",
                input=prompt,
                temperature=0.4,
                max_output_tokens=700
            )

            result = response.output_text
            st.success("✅ Analisis selesai")
            st.markdown(result)

        except Exception as e:
            st.error("❌ Terjadi kesalahan saat memanggil AI")

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.caption(
    "Aplikasi ini membantu mahasiswa menentukan judul skripsi "
    "secara efisien, akademik, dan berbasis data."
)
