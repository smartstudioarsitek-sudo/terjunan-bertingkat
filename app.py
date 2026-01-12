import streamlit as st
from hitung_terjun import hitung_bangunan_terjun

st.set_page_config(page_title="Bangunan Terjun Bertingkat", layout="centered")

st.title("🏗️ Aplikasi Bang explain Bangunan Terjun Bertingkat")
st.write("Perhitungan awal bangunan terjun irigasi (pendekatan KP)")

st.header("🔢 Input Data")

Q = st.number_input("Debit (Q) m³/det", min_value=0.01, value=1.0)
B = st.number_input("Lebar Saluran (B) m", min_value=0.5, value=2.0)
H_total = st.number_input("Total Tinggi Terjun (m)", min_value=0.5, value=3.0)
H_max = st.number_input("Tinggi Maks Terjun per Tingkat (m)", min_value=0.3, value=1.0)

if st.button("🔍 Hitung Bangunan Terjun"):
    hasil = hitung_bangunan_terjun(Q, B, H_total, H_max)

    st.success("✅ Hasil Perhitungan")

    for k, v in hasil.items():
        st.write(f"**{k}** : {v}")

    st.info("""
    Catatan:
    - Perhitungan ini untuk **tahap perencanaan awal**
    - Belum termasuk cek stabilitas struktur
    - Belum termasuk desain detail kolam olak (USBR lengkap)
    """)
