import streamlit as st
import pandas as pd
from hitung_terjun import hitung_bangunan_terjun
from cek_stabilitas import cek_stabilitas
# UPDATE IMPORT: Menggunakan fungsi baru untuk gambar bertingkat
from draw_section import gambar_potongan_bertingkat

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Desain Bangunan Terjun",
    layout="wide", # Layout wide agar gambar terlihat jelas
    initial_sidebar_state="expanded"
)

st.title("🌊 Desain Bangunan Terjun & Kolam Olak")
st.markdown("---")
st.write("""
Aplikasi perhitungan hidrolis bangunan terjun tegak (vertical drop) tipe bertingkat. 
Menggunakan pendekatan **KP-04** dan standar **USBR**.
""")

# --- 2. INPUT DATA (SIDEBAR) ---
with st.sidebar:
    st.header("🔢 Input Parameter")
    
    Q = st.number_input(
        "Debit Rencana (Q) m³/det", 
        min_value=0.01, value=1.50, step=0.05
    )
    
    B = st.number_input(
        "Lebar Saluran (B) m", 
        min_value=0.5, value=2.0, step=0.1
    )
    
    H_total = st.number_input(
        "Total Beda Tinggi (H) m", 
        min_value=0.5, value=3.5, step=0.1
    )
    
    H_max = st.number_input(
        "Tinggi Terjun Maksimum (m)", 
        min_value=0.3, value=1.5, step=0.1,
        help="Maksimal tinggi jatuh per satu trap"
    )

    tombol_hitung = st.button("🚀 Hitung & Gambar Desain", type="primary")

# --- 3. LOGIKA UTAMA ---
if tombol_hitung:
    try:
        # A. Panggil Fungsi Perhitungan
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max)

        # B. Tampilkan Ringkasan (Metrics)
        st.subheader("📋 Ringkasan Desain")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1: st.metric("Jumlah Trap", f"{hasil['Jumlah Terjun']} Buah")
        with col2: st.metric("Tipe USBR", hasil["Tipe Kolam"])
        with col3: st.metric("Tinggi Jatuh/Trap", f"{hasil['Tinggi Terjun per Tingkat (m)']} m")
        with col4: st.metric("Panjang Lantai", f"{hasil['Panjang Total Lantai (Ld+Lj) (m)']} m")
st.subheader("3️⃣ Cek Stabilitas Struktur")

st.sidebar.header("Parameter Struktur")
t = st.sidebar.number_input("Tebal Lantai Kolam (m)", value=0.5)
qa = st.sidebar.number_input("Daya Dukung Tanah Izin (kN/m²)", value=150.0)

stabil = cek_stabilitas(
    B=B,
    L=usbr["Panjang Kolam"],
    t=t,
    y1=y1,
    y2=usbr["y2"],
    qa=qa
)

for k, v in stabil.items():
    if isinstance(v, bool):
        st.write(f"**{k}** : {'✅ AMAN' if v else '❌ TIDAK AMAN'}")
    else:
        st.write(f"**{k}** : {v}")


        # C. Visualisasi Potongan (Gambar Teknik BERTINGKAT)
        st.markdown("---")
        st.subheader("📐 Visualisasi Profil Memanjang")
        
        try:
            # UPDATE PEMANGGILAN FUNGSI (Sesuai draw_section.py baru)
            fig_section = gambar_potongan_bertingkat(
                n_terjun = hasil["Jumlah Terjun"],
                H_total  = H_total, # Parameter baru
                H_drop   = hasil["Tinggi Terjun per Tingkat (m)"],
                L_drop   = hasil["Panjang Jatuhan Ld (m)"],
                L_kolam  = hasil["Panjang Loncatan Lj (m)"],
                y1       = hasil["Kedalaman di Kaki (y1)"],
                y2       = hasil["Kedalaman Konjugasi (y2)"],
                hs       = hasil["Tinggi End Sill (m)"],
                yc       = hasil["Kedalaman Kritis yc (m)"]
            )
            st.pyplot(fig_section, use_container_width=True)
        except Exception as e_img:
            st.error(f"Gagal memuat gambar: {e_img}")

        # D. Tabel Detail
        st.markdown("---")
        st.subheader("📊 Detail Parameter Hidrolis")
        df_hasil = pd.DataFrame(list(hasil.items()), columns=["Parameter", "Nilai"])
        st.table(df_hasil)

    except Exception as e:
        # Menangkap error perhitungan (seperti error 'y2' di screenshot Anda)
        st.error(f"Terjadi kesalahan sistem: {e}")
        st.warning("""
        **Solusi Error:**
        Jika errornya 'y2', pastikan file `hitung_terjun.py` sudah diperbarui.
        Cari baris: `data_usbr["y2"]`
        Ubah menjadi: `data_usbr.get("y2 (m)", 0)`
        """)

else:
    st.info("👈 Silakan masukkan data di sidebar kiri, lalu tekan tombol **Hitung**.")

