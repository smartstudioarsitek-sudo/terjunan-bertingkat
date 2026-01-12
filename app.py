import streamlit as st
import pandas as pd
from hitung_terjun import hitung_bangunan_terjun
from draw_section import gambar_potongan_detail

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Desain Bangunan Terjun",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🌊 Desain Bangunan Terjun & Kolam Olak")
st.markdown("---")
st.write("""
Aplikasi perhitungan hidrolis bangunan terjun tegak (vertical drop) untuk irigasi. 
Menggunakan pendekatan **KP-04** untuk hidrolika terjunan dan standar **USBR** untuk dimensi kolam olak.
""")

# --- 2. INPUT DATA (SIDEBAR) ---
with st.sidebar:
    st.header("🔢 Input Parameter")
    
    Q = st.number_input(
        "Debit Rencana (Q) m³/det", 
        min_value=0.01, 
        value=1.50,
        step=0.05
    )
    
    B = st.number_input(
        "Lebar Saluran (B) m", 
        min_value=0.5, 
        value=2.0,
        step=0.1
    )
    
    H_total = st.number_input(
        "Total Beda Tinggi (H) m", 
        min_value=0.5, 
        value=3.5,
        step=0.1
    )
    
    H_max = st.number_input(
        "Tinggi Terjun Maksimum (m)", 
        min_value=0.3, 
        value=1.5,
        step=0.1,
        help="Maksimal tinggi jatuh per satu trap"
    )

    tombol_hitung = st.button("🚀 Hitung Desain", type="primary")

# --- 3. LOGIKA UTAMA ---
if tombol_hitung:
    try:
        # A. Panggil Fungsi Perhitungan
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max)

        st.success("✅ Perhitungan Selesai")
        
        # B. Tampilkan Ringkasan (Metrics)
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

        # C. Visualisasi Potongan (Gambar Teknik)
        st.markdown("---")
        st.subheader("📐 Visualisasi Potongan Melintang")
        
        try:
            # Memanggil fungsi gambar dari draw_section.py
            fig_section = gambar_potongan_detail(
                H_drop  = hasil["Tinggi Terjun per Tingkat (m)"],
                L_drop  = hasil["Panjang Jatuhan Ld (m)"],
                L_kolam = hasil["Panjang Loncatan Lj (m)"],
                y1      = hasil["Kedalaman di Kaki (y1)"],
                y2      = hasil["Kedalaman Konjugasi (y2)"],
                hs      = hasil["Tinggi End Sill (m)"],
                yc      = hasil["Kedalaman Kritis yc (m)"]
            )
            st.pyplot(fig_section)
        except Exception as e_img:
            st.warning(f"Gagal memuat gambar: {e_img}")

        # D. Tabel Detail Parameter
        st.markdown("---")
        st.subheader("📊 Detail Parameter Hidrolis")
        
        # Konversi hasil ke DataFrame agar rapi
        df_hasil = pd.DataFrame(list(hasil.items()), columns=["Parameter", "Nilai"])
        st.table(df_hasil)

        # E. Catatan Teknis
        st.info("""
        **Catatan Desain:**
        1. **Panjang Lantai Total** ($L_{total}$) adalah penjumlahan dari Panjang Lintasan Jatuhan ($L_d$) + Panjang Kolam Olak ($L_j$).
        2. **Tipe USBR** dipilih otomatis berdasarkan Bilangan Froude ($Fr$) dan Kecepatan Aliran ($V_1$).
        3. Visualisasi di atas adalah skema potongan per satu tingkat terjunan.
        """)

    except Exception as e:
        st.error(f"Terjadi kesalahan sistem: {e}")
        st.warning("Pastikan file `hitung_terjun.py` dan `draw_section.py` sudah diupdate dengan kode terbaru.")

else:
    st.info("👈 Silakan masukkan data di sidebar kiri, lalu tekan tombol **Hitung Desain**.")
