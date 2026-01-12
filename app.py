import streamlit as st
import pandas as pd
from hitung_terjun import hitung_bangunan_terjun
from cek_stabilitas import cek_stabilitas
from draw_section import gambar_potongan_bertingkat
from export_utils import generate_excel, generate_dxf

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Desain Bangunan Terjun", layout="wide")

st.title("🌊 Desain Bangunan Terjun & Kolam Olak")
st.markdown("---")

# --- 2. INPUT DATA (SIDEBAR) ---
with st.sidebar:
    st.header("1️⃣ Parameter Hidrolis")
    # Perbaikan: Menggunakan keyword arguments (value=..., step=...) agar aman
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
        # A. PROSES PERHITUNGAN
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max)
        
        stabil = cek_stabilitas(
            B=B, L=hasil["Panjang Loncatan Lj (m)"], t=t_lantai,
            y1=hasil["Kedalaman di Kaki (y1)"], y2=hasil["Kedalaman Konjugasi (y2)"],
            H_drop=hasil["Tinggi Terjun per Tingkat (m)"], qa=qa_tanah
        )

        # B. MEMBUAT TABS
        tab1, tab2 = st.tabs(["📊 Desain & Visualisasi", "📑 Rekap & Download"])

        # --- ISI TAB 1: DESAIN ---
        with tab1:
            st.subheader("Ringkasan Hasil")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Jumlah Trap", f"{hasil['Jumlah Terjun']}")
            c2.metric("Tipe USBR", hasil["Tipe Kolam"])
            c3.metric("Tinggi/Trap", f"{hasil['Tinggi Terjun per Tingkat (m)']} m")
            c4.metric("Panjang Lantai", f"{hasil['Panjang Total Lantai (Ld+Lj) (m)']} m")

            st.subheader("Cek Stabilitas")
            sc1, sc2 = st.columns(2)
            lbl_uplift = "✅ AMAN" if stabil["Aman Uplift"] else "❌ BAHAYA"
            sc1.metric("Uplift (SF > 1.5)", f"{stabil['SF Uplift']}", lbl_uplift)
            
            lbl_tanah = "✅ AMAN" if stabil["Aman Daya Dukung"] else "❌ BAHAYA"
            sc2.metric("Daya Dukung Tanah", f"{stabil['Tekanan Tanah (kN/m2)']} kN/m²", lbl_tanah)

            st.subheader("Visualisasi")
            # Pastikan urutan parameter sesuai dengan fungsi di draw_section.py
            fig = gambar_potongan_bertingkat(
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
            st.pyplot(fig, use_container_width=True)

        # --- ISI TAB 2: REKAP & DOWNLOAD ---
        with tab2:
            st.header("📂 Rekapitulasi Data")
            
            # Tampilkan Tabel
            col_a, col_b = st.columns(2)
            with col_a:
                st.caption("Data Hidrolis")
                st.dataframe(pd.DataFrame(list(hasil.items()), columns=["Parameter", "Nilai"]), hide_index=True)
            with col_b:
                st.caption("Data Stabilitas")
                st.dataframe(pd.DataFrame(list(stabil.items()), columns=["Parameter", "Nilai"]), hide_index=True)

            st.divider()
            st.header("📥 Download File")
            
            # 1. EXCEL BUTTON
            input_dict = {"Q": Q, "B": B, "H Total": H_total, "H Max": H_max, "Tebal Lantai": t_lantai, "Qa Tanah": qa_tanah}
            excel_data = generate_excel(input_dict, hasil, stabil)
            
            st.download_button(
                label="📥 Download Laporan Excel (.xlsx)",
                data=excel_data,
                file_name="Laporan_Desain_Terjun.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # 2. DXF (CAD) BUTTON
            st.write("---")
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
                mime="application/dxf",
                help="File DXF dapat dibuka dengan AutoCAD, Civil 3D, atau Software CAD lainnya."
            )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        # Tambahan info debug untuk Anda
        st.info("Jika masih error, pastikan semua file (export_utils.py, requirements.txt, dll) sudah diupdate.")
else:
    st.info("👈 Masukkan data & tekan tombol Hitung untuk melihat hasil.")
