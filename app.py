import streamlit as st
from hitung_terjun import hitung_bangunan_terjun
from usbr_stilling import hitung_usbr
from draw_section import gambar_potongan

st.set_page_config(page_title="Bangunan Terjun + Kolam Olak USBR", layout="wide")

st.title("🏗️ Aplikasi Bangunan Terjun Bertingkat + Kolam Olak USBR")

st.sidebar.header("Input Data Hidrolika")
Q = st.sidebar.number_input("Debit Q (m³/det)", value=1.5)
B = st.sidebar.number_input("Lebar Saluran B (m)", value=2.0)
H_total = st.sidebar.number_input("Total Tinggi Terjun (m)", value=3.0)
H_max = st.sidebar.number_input("Tinggi Maks Terjun/Tingkat (m)", value=1.0)

if st.sidebar.button("🔍 Hitung Lengkap"):
    terjun = hitung_bangunan_terjun(Q, B, H_total, H_max)

    st.subheader("1️⃣ Bangunan Terjun Bertingkat")
    for k, v in terjun.items():
        st.write(f"**{k}** : {v}")

    y1 = terjun["Kedalaman Kritis yk (m)"]

    usbr = hitung_usbr(Q, B, y1)

    st.subheader("2️⃣ Desain Kolam Olak USBR")
    for k, v in usbr.items():
        st.write(f"**{k}** : {v}")

    fig = gambar_potongan(
        y1,
        usbr["y2"],
        usbr["Panjang Kolam"],
        usbr["End Sill"]
    )
    st.pyplot(fig)

    st.success("✅ Desain terjun + kolam olak selesai")
