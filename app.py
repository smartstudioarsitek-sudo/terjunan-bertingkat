import streamlit as st
import pandas as pd
from hitung_terjun import hitung_bangunan_terjun

# Konfigurasi Halaman
st.set_page_config(
    page_title="Bangunan Terjun Bertingkat",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Judul Aplikasi
st.title("🌊 Desain Bangunan Terjun & Kolam Olak")
st.markdown("---")
st.write("""
Aplikasi perhitungan hidrolis bangunan terjun tegak (vertical drop) untuk irigasi. 
Menggunakan pendekatan **KP-04** dan standar **USBR** untuk kolam olak.
""")

# --- Sidebar untuk Input Data ---
with st.sidebar:
    st.header("🔢 Input Parameter Desain")
    
    Q = st.number_input(
        "Debit Rencana (Q) m³/det", 
        min_value=0.01, 
        value=1.50,
        step=0.05,
        help="Debit desain saluran"
    )
    
    B = st.number_input(
        "Lebar Saluran (B) m", 
        min_value=0.5, 
        value=2.0,
        step=0.1,
        help="Lebar saluran (asumsi persegi)"
    )
    
    H_total = st.number_input(
        "Total Beda Tinggi (H) m", 
        min_value=0.5, 
        value=3.5,
        step=0.1,
        help="Total ketinggian dari hulu ke hilir"
    )
    
    H_max = st.number_input(
        "Tinggi Terjun Maksimum (m)", 
        min_value=0.3, 
        value=1.5,
        step=0.1,
        help="Batasan tinggi jatuh per satu trap"
    )

    tombol_hitung = st.button("🚀 Hitung Desain", type="primary")

# --- Logika Utama ---
if tombol_hitung:
    # Memanggil fungsi perhitungan (pastikan hitung_terjun.py sudah diupdate)
    try:
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max)

        st.success("✅ Perhitungan Selesai")
        
        # 1. Ringkasan Utama (Metrics)
        st.subheader("📋 Ringkasan Desain")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Jumlah Terjun", f"{hasil['Jumlah Terjun']} Buah")
        with col2:
            st.metric("Tipe USBR", hasil["Tipe Kolam"])
        with col3:
            st.metric("Tinggi Jatuh", f"{hasil['Tinggi Terjun per Tingkat (m)']} m")
        with col4:
            st.metric("Panjang Lantai", f"{hasil['Panjang Total Lantai (Ld+Lj) (m)']} m")

        # 2. Detail Hidrolis (Tabel)
        st.subheader("📊 Detail Parameter Hidrolis")
        
        # Konversi dict ke DataFrame agar tampilan lebih cantik
        df_hasil = pd.DataFrame(list(hasil.items()), columns=["Parameter", "Nilai"])
        
        # Format angka di tabel agar rapi
        st.table(df_hasil)

        # 3. Catatan Teknis
        st.info("""
        **Catatan Desain:**
        - **Panjang Lantai Total** = Panjang lintasan jatuhan air ($L_d$) + Panjang loncatan hidrolis ($L_j$).
        - **Tipe USBR** ditentukan berdasarkan Bilangan Froude ($Fr$) di kaki terjunan.
        - Pastikan elevasi muka air hilir (Tail Water Level) mencukupi untuk mendukung terjadinya loncatan air ($y_2$).
        """)

    except Exception as e:
        st.error(f"Terjadi kesalahan dalam perhitungan: {e}")
        st.warning("Pastikan Anda sudah mengupdate file `hitung_terjun.py` dengan kode revisi sebelumnya.")

else:
    # Tampilan awal sebelum tombol ditekan
    st.info("👈 Masukkan data di sidebar kiri, lalu tekan tombol **Hitung Desain**.")
