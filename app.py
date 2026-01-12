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
    Q = st.number_input("Debit (Q) m³/det", min_value=0.01, value=1.50, step=0.05)
    B = st.number_input("Lebar (B) m", min_value=0.5, value=2.0, step=0.1)
    H_total = st.number_input("Total Tinggi (H) m", min_value=0.5, value=3.5, step=0.1)
    H_max = st.number_input("Tinggi Max/Trap (m)", min_value=0.3, value=1.5, step=0.1)
    
    st.markdown("---")
    st.header("⚙️ Opsi Desain")
    mode_hemat = st.checkbox("✅ Mode Hemat (Kolam di Bawah Saja)", value=True, 
                             help="Jika dicentang & tinggi per trap < 1.2m, lantai trap tengah akan dibuat pendek tanpa kolam olak penuh.")

    st.markdown("---")
    st.header("2️⃣ Parameter Struktur")
    t_lantai = st.number_input("Tebal Lantai (m)", min_value=0.2, value=0.5, step=0.05)
    qa_tanah = st.number_input("Daya Dukung (kN/m²)", min_value=10.0, value=150.0, step=10.0)
    
    st.markdown("---")
    tombol_hitung = st.button("🚀 Hitung & Analisis", type="primary")

# --- 3. LOGIKA UTAMA ---
if tombol_hitung:
    try:
        # A. HITUNGAN
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max, mode_hemat)
        
        # Hitung L untuk stabilitas (Ambil yang paling kritis/panjang yaitu L_final)
        # Dikurangi L_drop karena L di rumus stabilitas biasanya adalah panjang lantai datar efektif
        L_stabil = hasil["Panjang Lantai Final (m)"] - hasil["Panjang Jatuhan Ld (m)"]
        
        stabil = cek_stabilitas(
            B=B, L=L_stabil, t=t_lantai,
            y1=hasil["Kedalaman di Kaki (y1)"], y2=hasil["Kedalaman Konjugasi (y2)"],
            H_drop=hasil["Tinggi Terjun per Tingkat (m)"], qa=qa_tanah
        )

        # B. TABS
        tab1, tab2, tab3 = st.tabs(["📊 Potongan & Visualisasi", "📐 Denah Situasi", "📑 Rekap & Download"])

        with tab1:
            st.subheader(f"Hasil Desain: {hasil['Desain Mode']}")
            
            # Metric Comparison
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Panjang Lantai Tengah", f"{hasil['Panjang Lantai Intermediate (m)']} m")
            c2.metric("Panjang Lantai Bawah", f"{hasil['Panjang Lantai Final (m)']} m", "Kolam Utama")
            c3.metric("Jml Trap", hasil["Jumlah Terjun"])
            c4.metric("Tinggi/Trap", f"{hasil['Tinggi Terjun per Tingkat (m)']} m")
            
            if "Mode Hemat" in hasil["Desain Mode"]:
                st.warning("⚠️ **Mode Hemat Aktif:** Lantai pada trap tengah dibuat pendek. Pastikan beton trap tengah bermutu tinggi (K-225+).")

            fig_section = gambar_potongan_bertingkat(
                hasil["Jumlah Terjun"], H_total, hasil["Tinggi Terjun per Tingkat (m)"],
                hasil["Panjang Jatuhan Ld (m)"], 
                hasil["Panjang Kolam Intermediate (m)"], 
                hasil["Panjang Kolam Final (m)"],        
                hasil["Kedalaman di Kaki (y1)"], hasil["Kedalaman Konjugasi (y2)"],
                hasil["Tinggi End Sill (m)"], hasil["Kedalaman Kritis yc (m)"]
            )
            st.pyplot(fig_section, use_container_width=True)

        with tab2:
            st.subheader("Denah Situasi")
            fig_plan = gambar_denah_bertingkat(
                hasil["Jumlah Terjun"], B, hasil["Panjang Jatuhan Ld (m)"],
                hasil["Panjang Kolam Intermediate (m)"], 
                hasil["Panjang Kolam Final (m)"]         
            )
            st.pyplot(fig_plan, use_container_width=True)

        with tab3:
            st.header("📂 Rekapitulasi")
            st.dataframe(pd.DataFrame(list(hasil.items()), columns=["Parameter", "Nilai"]), hide_index=True)
            
            st.divider()
            st.header("📥 Download File")
            
            input_dict = {"Q": Q, "B": B, "H Total": H_total, "H Max": H_max, "Tebal Lantai": t_lantai, "Qa Tanah": qa_tanah}
            excel_data = generate_excel(input_dict, hasil, stabil)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="📥 Download Laporan Excel", 
                    data=excel_data, 
                    file_name="Laporan_Desain.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col_d2:
                # FIX ERROR HERE: Menggunakan parameter baru (L_inter & L_final)
                dxf_data = generate_dxf(
                    hasil["Jumlah Terjun"], H_total, hasil["Tinggi Terjun per Tingkat (m)"],
                    hasil["Panjang Jatuhan Ld (m)"], 
                    hasil["Panjang Kolam Intermediate (m)"], # <--- PARAMETER BARU
                    hasil["Panjang Kolam Final (m)"],        # <--- PARAMETER BARU
                    hasil["Kedalaman di Kaki (y1)"], hasil["Kedalaman Konjugasi (y2)"],
                    hasil["Tinggi End Sill (m)"], hasil["Kedalaman Kritis yc (m)"]
                )
                st.download_button(
                    label="📐 Download Gambar CAD (.dxf)", 
                    data=dxf_data, 
                    file_name="Desain_Terjun.dxf", 
                    mime="application/dxf"
                )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.info("Tips: Pastikan file `export_utils.py` sudah diupdate dengan kode terbaru.")
else:
    st.info("👈 Tekan tombol Hitung untuk memulai.")
