import streamlit as st
import pandas as pd
from hitung_terjun import hitung_bangunan_terjun
from cek_stabilitas import cek_stabilitas
from draw_section import gambar_potongan_bertingkat
from draw_plan import gambar_denah_bertingkat # <--- Import File Baru
from export_utils import generate_excel, generate_dxf

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Desain Bangunan Terjun", layout="wide")

st.title("🌊 Desain Bangunan Terjun & Kolam Olak")
st.markdown("---")

# --- 2. INPUT DATA (SIDEBAR) ---
with st.sidebar:
    st.header("1️⃣ Parameter Hidrolis")
    Q = st.number_input("Debit (Q) m³/det", min_value=0.01, value=1.50, step=0.05)
    B = st.number_input("Lebar (B) m", min_value=0.5, value=2.0, step=0.1)
    H_total = st.number_input("Total Tinggi (H) m", min_value=0.5, value=3.5, step=0.1)
    H_max = st.number_input("Tinggi Max/Trap (m)", min_value=0.3, value=1.5, step=0.1)

    st.header("2️⃣ Parameter Struktur")
    t_lantai = st.number_input("Tebal Lantai (m)", min_value=0.2, value=0.5, step=0.05)
    qa_tanah = st.number_input("Daya Dukung (kN/m²)", min_value=10.0, value=150.0, step=10.0)
    
    st.markdown("---")
    tombol_hitung = st.button("🚀 Hitung & Analisis", type="primary")

# --- 3. LOGIKA UTAMA ---
if tombol_hitung:
    try:
        # A. HITUNGAN
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max)
        
        stabil = cek_stabilitas(
            B=B, L=hasil["Panjang Loncatan Lj (m)"], t=t_lantai,
            y1=hasil["Kedalaman di Kaki (y1)"], y2=hasil["Kedalaman Konjugasi (y2)"],
            H_drop=hasil["Tinggi Terjun per Tingkat (m)"], qa=qa_tanah
        )

        # B. TAB NAVIGASI (Updated: Ada 3 Tab)
        tab1, tab2, tab3 = st.tabs(["📊 Potongan Memanjang", "📐 Denah Situasi", "📑 Rekap & Download"])

        # --- TAB 1: POTONGAN MEMANJANG ---
        with tab1:
            st.subheader("Visualisasi Potongan (Long Section)")
            
            # Ringkasan Cepat di Atas Gambar
            c1, c2, c3 = st.columns(3)
            c1.metric("Jml Terjun", f"{hasil['Jumlah Terjun']} trap")
            c2.metric("Tipe Kolam", hasil["Tipe Kolam"])
            c3.metric("Panjang Total", f"{hasil['Panjang Total Lantai (Ld+Lj) (m)']} m/trap")

            fig_section = gambar_potongan_bertingkat(
                n_terjun=hasil["Jumlah Terjun"], 
                H_total=H_total, 
                H_drop=hasil["Tinggi Terjun per Tingkat (m)"],
                L_drop=hasil["Panjang Jatuhan Ld (m)"], 
                L_kolam=hasil["Panjang Loncatan Lj (m)"],
                y1=hasil["Kedalaman di Kaki (y1)"], 
                y2=hasil["Kedalaman Konjugasi (y2)"],
                hs=hasil["Tinggi End Sill (m)"], 
                yc=hasil["Kedalaman Kritis yc (m)"]
            )
            st.pyplot(fig_section, use_container_width=True)

        # --- TAB 2: DENAH SITUASI (BARU) ---
        with tab2:
            st.subheader("Visualisasi Denah (Plan View)")
            st.write("Tampak atas tata letak bangunan terjun dan lebar saluran.")
            
            fig_plan = gambar_denah_bertingkat(
                n_terjun=hasil["Jumlah Terjun"],
                B=B,
                L_drop=hasil["Panjang Jatuhan Ld (m)"],
                L_kolam=hasil["Panjang Loncatan Lj (m)"],
                t_dinding=0.30 # Asumsi tebal dinding 30cm untuk visualisasi
            )
            st.pyplot(fig_plan, use_container_width=True)
            
            st.info(f"💡 Lebar Saluran Efektif (B) = {B} meter. Garis abu-abu adalah dinding saluran.")

        # --- TAB 3: REKAP & DOWNLOAD ---
        with tab3:
            st.header("📂 Rekapitulasi & Laporan")
            
            # Tabel Data
            col_a, col_b = st.columns(2)
            with col_a:
                st.caption("Parameter Hidrolis")
                st.dataframe(pd.DataFrame(list(hasil.items()), columns=["Parameter", "Nilai"]), hide_index=True)
            with col_b:
                st.caption("Analisa Stabilitas")
                st.dataframe(pd.DataFrame(list(stabil.items()), columns=["Parameter", "Nilai"]), hide_index=True)

            st.divider()
            
            # Tombol Download
            input_dict = {"Q": Q, "B": B, "H Total": H_total, "H Max": H_max, "Tebal Lantai": t_lantai, "Qa Tanah": qa_tanah}
            excel_data = generate_excel(input_dict, hasil, stabil)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="📥 Download Laporan Excel",
                    data=excel_data,
                    file_name="Laporan_Desain_Terjun.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            with col_d2:
                dxf_data = generate_dxf(
                    hasil["Jumlah Terjun"], H_total, hasil["Tinggi Terjun per Tingkat (m)"],
                    hasil["Panjang Jatuhan Ld (m)"], hasil["Panjang Loncatan Lj (m)"],
                    hasil["Kedalaman di Kaki (y1)"], hasil["Kedalaman Konjugasi (y2)"],
                    hasil["Tinggi End Sill (m)"], hasil["Kedalaman Kritis yc (m)"]
                )
                st.download_button(
                    label="📐 Download Gambar CAD (.dxf)",
                    data=dxf_data,
                    file_name="Gambar_Desain_Terjun.dxf",
                    mime="application/dxf"
                )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("👈 Masukkan data & tekan tombol Hitung untuk melihat hasil.")
