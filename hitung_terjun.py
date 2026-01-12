import streamlit as st
import pandas as pd
from hitung_terjun import hitung_bangunan_terjun
from cek_stabilitas import cek_stabilitas
from draw_section import gambar_potongan_bertingkat
from draw_plan import gambar_denah_bertingkat
from export_utils import generate_excel, generate_dxf

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Desain Bangunan Terjun", layout="wide")

st.title("🌊 Desain Bangunan Terjun & Kolam Olak")
st.markdown("---")

# --- 2. INPUT DATA ---
with st.sidebar:
    st.header("1️⃣ Parameter Hidrolis")
    Q = st.number_input("Debit (Q) m³/det", 0.01, 1.50, 0.05)
    B = st.number_input("Lebar (B) m", 0.5, 2.0, 0.1)
    H_total = st.number_input("Total Tinggi (H) m", 0.5, 3.5, 0.1)
    H_max = st.number_input("Tinggi Max/Trap (m)", 0.3, 1.5, 0.1)
    
    # --- FITUR BARU: MODE HEMAT ---
    st.markdown("---")
    st.header("⚙️ Opsi Desain")
    mode_hemat = st.checkbox("✅ Mode Hemat (Kolam di Bawah Saja)", value=True, 
                             help="Jika dicentang & tinggi per trap < 1.2m, lantai trap tengah akan dibuat pendek tanpa kolam olak penuh.")

    st.markdown("---")
    st.header("2️⃣ Parameter Struktur")
    t_lantai = st.number_input("Tebal Lantai (m)", 0.2, 0.5, 0.05)
    qa_tanah = st.number_input("Daya Dukung (kN/m²)", 10.0, 150.0, 10.0)
    
    st.markdown("---")
    tombol_hitung = st.button("🚀 Hitung & Analisis", type="primary")

# --- 3. LOGIKA UTAMA ---
if tombol_hitung:
    try:
        # A. HITUNGAN (Pass parameter mode_hemat)
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max, mode_hemat)
        
        # Ambil panjang lantai final untuk cek stabilitas (karena ini yang paling kritis)
        L_stabil = hasil["Panjang Lantai Final (m)"] - hasil["Panjang Jatuhan Ld (m)"] # L_jump only
        
        stabil = cek_stabilitas(
            B=B, L=L_stabil, t=t_lantai,
            y1=hasil["Kedalaman di Kaki (y1)"], y2=hasil["Kedalaman Konjugasi (y2)"],
            H_drop=hasil["Tinggi Terjun per Tingkat (m)"], qa=qa_tanah
        )

        # B. TABS
        tab1, tab2, tab3 = st.tabs(["📊 Potongan & Visualisasi", "📐 Denah Situasi", "📑 Rekap"])

        with tab1:
            st.subheader(f"Hasil Desain: {hasil['Desain Mode']}")
            
            # Metric Comparison
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Panjang Lantai Tengah", f"{hasil['Panjang Lantai Intermediate (m)']} m")
            c2.metric("Panjang Lantai Bawah", f"{hasil['Panjang Lantai Final (m)']} m", "Kolam Utama")
            c3.metric("Jml Trap", hasil["Jumlah Terjun"])
            c4.metric("Tinggi/Trap", f"{hasil['Tinggi Terjun per Tingkat (m)']} m")
            
            # Peringatan jika mode hemat aktif
            if "Mode Hemat" in hasil["Desain Mode"]:
                st.warning("⚠️ **Mode Hemat Aktif:** Lantai pada trap tengah hanya berfungsi sebagai pelindung jatuhan (bukan peredam energi). Pastikan beton lantai trap tengah memiliki mutu tinggi (K-225 ke atas) karena kecepatan air tinggi.")

            fig_section = gambar_potongan_bertingkat(
                hasil["Jumlah Terjun"], H_total, hasil["Tinggi Terjun per Tingkat (m)"],
                hasil["Panjang Jatuhan Ld (m)"], 
                hasil["Panjang Kolam Intermediate (m)"], # Parameter baru
                hasil["Panjang Kolam Final (m)"],        # Parameter baru
                hasil["Kedalaman di Kaki (y1)"], hasil["Kedalaman Konjugasi (y2)"],
                hasil["Tinggi End Sill (m)"], hasil["Kedalaman Kritis yc (m)"]
            )
            st.pyplot(fig_section, use_container_width=True)

        with tab2:
            st.subheader("Denah Situasi")
            fig_plan = gambar_denah_bertingkat(
                hasil["Jumlah Terjun"], B, hasil["Panjang Jatuhan Ld (m)"],
                hasil["Panjang Kolam Intermediate (m)"], # Parameter baru
                hasil["Panjang Kolam Final (m)"]         # Parameter baru
            )
            st.pyplot(fig_plan, use_container_width=True)

        with tab3:
            st.header("📂 Rekapitulasi")
            st.dataframe(pd.DataFrame(list(hasil.items()), columns=["Parameter", "Nilai"]), hide_index=True)
            
            # Export (Updated logic to handle new keys if needed inside export_utils, 
            # but standard dict pass works mostly fine)
            # Note: For strict Excel/CAD export, ensure export_utils supports the new keys if necessary.
            # But standard iteration in export_utils will just print the new keys automatically.

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.info("Pastikan semua file (hitung_terjun, draw_section, draw_plan) sudah diupdate.")
else:
    st.info("👈 Tekan tombol Hitung untuk memulai.")
