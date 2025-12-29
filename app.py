import streamlit as st
import pandas as pd
import os
from groq import Groq

# ===============================
# KONFIGURASI HALAMAN
# ===============================
st.set_page_config(
    page_title="AI Asisten Penentuan Judul Skripsi",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Asisten Penentuan Judul Skripsi")
st.write("Berbasis data skripsi terdahulu dan tren penelitian terkini")

# ===============================
# CEK API KEY GROQ
# ===============================
if "GROQ_API_KEY" not in os.environ:
    st.error("❌ GROQ_API_KEY belum diatur di Streamlit Secrets")
    st.stop()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# ===============================
# UPLOAD DATA EXCEL
# ===============================
st.header("📂 Upload Data Skripsi Terdahulu")
uploaded_file = st.file_uploader(
    "Upload file Excel (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Silakan upload data skripsi terlebih dahulu")
    st.stop()

# ===============================
# BACA DATA
# ===============================
try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Gagal membaca file Excel: {e}")
    st.stop()

# ===============================
# VALIDASI KOLOM
# ===============================
required_columns = [
    "Judul", "Tahun", "Prodi",
    "Variabel", "Metode",
    "Objek", "Lokasi", "Kata_Kunci"
]

missing_cols = [c for c in required_columns if c not in df.columns]
if missing_cols:
    st.error(f"Kolom berikut tidak ditemukan: {missing_cols}")
    st.stop()

# ===============================
# FILTER INPUT USER
# ===============================
st.header("🔍 Pencarian Penelitian")

col1, col2 = st.columns(2)

with col1:
    selected_prodi = st.multiselect(
        "Pilih Program Studi",
        options=sorted(df["Prodi"].unique())
    )

with col2:
    keyword = st.text_input(
        "Masukkan topik / kata kunci penelitian",
        placeholder="Contoh: UMKM, e-procurement, digital marketing"
    )

# ===============================
# FILTER DATA
# ===============================
filtered_df = df.copy()

if selected_prodi:
    filtered_df = filtered_df[filtered_df["Prodi"].isin(selected_prodi)]

if keyword:
    filtered_df = filtered_df[
        filtered_df["Judul"].str.contains(keyword, case=False, na=False) |
        filtered_df["Kata_Kunci"].str.contains(keyword, case=False, na=False)
    ]

# ===============================
# TAMPILKAN DATA
# ===============================
st.subheader("📑 Hasil Penelitian Terdahulu")

if filtered_df.empty:
    st.warning("Tidak ditemukan penelitian yang sesuai")
    st.stop()

st.dataframe(filtered_df, use_container_width=True)

# ===============================
# ANALISIS AI
# ===============================
st.header("🤖 Analisis & Rekomendasi AI")

if st.button("Analisis Kelayakan Penelitian"):
    with st.spinner("AI sedang menganalisis..."):

        context = ""
        for _, row in filtered_df.iterrows():
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
Kamu adalah AI akademik yang membantu mahasiswa menentukan judul skripsi.

Tugas kamu:
1. Menilai apakah topik "{keyword}" masih relevan dan layak diteliti
2. Menilai tingkat kebaruan berdasarkan penelitian terdahulu
3. Memberikan rekomendasi:
   - Layak diteliti / Tidak layak
   - Alasan akademik
   - Saran pengembangan judul agar lebih baru
4. Gunakan bahasa akademik yang mudah dipahami mahasiswa

Data penelitian terdahulu:
{context}
"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Kamu adalah dosen pembimbing skripsi berpengalaman."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1200
        )

        result = response.choices[0].message.content
        st.success("✅ Analisis selesai")
        st.markdown(result)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("Dikembangkan untuk membantu mahasiswa menentukan judul skripsi secara efisien dan akademis")
