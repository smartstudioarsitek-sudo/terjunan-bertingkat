import streamlit as st
import pandas as pd
from hitung_terjun import hitung_bangunan_terjun
from cek_stabilitas import cek_stabilitas
from draw_section import gambar_potongan_bertingkat

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Desain Bangunan Terjun",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌊 Desain Bangunan Terjun & Kolam Olak")
st.markdown("---")
st.write("""
Aplikasi perhitungan hidrolis bangunan terjun tegak (vertical drop) tipe bertingkat. 
Termasuk analisis hidrolika (**KP-04**), dimensi kolam olak (**USBR**), dan kontrol stabilitas struktur.
""")

# --- 2. INPUT DATA (SIDEBAR) ---
with st.sidebar:
    st.header("1️⃣ Parameter Hidrolis")
    Q = st.number_input("Debit Rencana (Q) m³/det", min_value=0.01, value=1.50, step=0.05)
    B = st.number_input("Lebar Saluran (B) m", min_value=0.5, value=2.0, step=0.1)
    H_total = st.number_input("Total Beda Tinggi (H) m", min_value=0.5, value=3.5, step=0.1)
    H_max = st.number_input("Tinggi Terjun Maks (m)", min_value=0.3, value=1.5, step=0.1)

    st.markdown("---")
    st.header("2️⃣ Parameter Struktur")
    t_lantai = st.number_input("Tebal Lantai Beton (m)", min_value=0.2, value=0.5, step=0.05)
    qa_tanah = st.number_input("Daya Dukung Tanah (kN/m²)", min_value=10.0, value=150.0, step=10.0)

    st.markdown("---")
    tombol_hitung = st.button("🚀 Hitung & Analisis", type="primary")

# --- 3. LOGIKA UTAMA ---
if tombol_hitung:
    try:
        # A. HITUNGAN HIDROLIS
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max)
        
        # B. TAMPILKAN RINGKASAN
        st.subheader("📋 Ringkasan Desain Hidrolis")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Jumlah Trap", f"{hasil['Jumlah Terjun']} Buah")
        with col2: st.metric("Tipe USBR", hasil["Tipe Kolam"])
        with col3: st.metric("Tinggi Jatuh/Trap", f"{hasil['Tinggi Terjun per Tingkat (m)']} m")
        with col4: st.metric("Panjang Lantai Total", f"{hasil['Panjang Total Lantai (Ld+Lj) (m)']} m")

        # C. CEK STABILITAS STRUKTUR
        st.markdown("---")
        st.subheader("🏗️ Cek Stabilitas (Guling, Geser, Uplift)")
        
        # Mapping data dari hasil hidrolis ke fungsi stabilitas
        # Perhatikan: Kita mengambil nilai dari dictionary 'hasil'
        hasil_stabil = cek_stabilitas(
            B = B,
            L = hasil["Panjang Loncatan Lj (m)"], # Panjang lantai kolam efektif
            t = t_lantai,
            y1 = hasil["Kedalaman di Kaki (y1)"],
            y2 = hasil["Kedalaman Konjugasi (y2)"],
            qa = qa_tanah
        )

        # Tampilkan hasil stabilitas dengan indikator warna
        c1, c2, c3 = st.columns(3)
        
        # Geser
        status_geser = "✅ AMAN" if hasil_stabil["Aman Geser"] else "❌ TIDAK AMAN"
        c1.metric("Kontrol Geser (SF > 1.5)", f"{hasil_stabil['FS Geser']}", status_geser)
        
        # Guling
        status_guling = "✅ AMAN" if hasil_stabil["Aman Guling"] else "❌ TIDAK AMAN"
        c2.metric("Kontrol Guling (SF > 2.0)", f"{hasil_stabil['FS Guling']}", status_guling)
        
        # Daya Dukung
        status_tanah = "✅ AMAN" if hasil_stabil["Aman Daya Dukung"] else "❌ TIDAK AMAN"
        val_tanah = hasil_stabil['Tekanan Tanah (kN/m2)']
        c3.metric(f"Tekanan Tanah (< {qa_tanah})", f"{val_tanah} kN/m²", status_tanah)

        # Expander untuk detail gaya
        with st.expander("🔍 Lihat Detail Gaya-Gaya Struktur"):
            st.json(hasil_stabil)

    # C. CEK STABILITAS STRUKTUR (REVISI)
        st.markdown("---")
        st.subheader("🏗️ Cek Stabilitas Lantai (Uplift & Bearing)")
        
        # Pemanggilan fungsi dengan parameter baru H_drop
        hasil_stabil = cek_stabilitas(
            B = B,
            L = hasil["Panjang Loncatan Lj (m)"], 
            t = t_lantai,
            y1 = hasil["Kedalaman di Kaki (y1)"],
            y2 = hasil["Kedalaman Konjugasi (y2)"],
            H_drop = hasil["Tinggi Terjun per Tingkat (m)"], # <--- PARAMETER BARU PENTING
            qa = qa_tanah
        )

        # Tampilkan hasil stabilitas dengan layout baru
        c1, c2 = st.columns(2)
        
        # Cek Uplift
        status_uplift = "✅ AMAN" if hasil_stabil["Aman Uplift"] else "❌ BAHAYA (Uplift)"
        c1.metric("SF Uplift (Anti-Apung)", f"{hasil_stabil['SF Uplift']} (Target > 1.5)", status_uplift)
        
        # Cek Daya Dukung
        status_tanah = "✅ AMAN" if hasil_stabil["Aman Daya Dukung"] else "❌ BAHAYA (Amblas)"
        val_tanah = hasil_stabil['Tekanan Tanah (kN/m2)']
        c2.metric(f"Tekanan Tanah (Max {qa_tanah})", f"{val_tanah} kN/m²", status_tanah)

        # Expander detail
        with st.expander("🔍 Detail Gaya (Berat vs Uplift)"):
            st.write("""
            Perhitungan ini mengecek apakah lantai kolam cukup tebal untuk melawan tekanan air dari bawah tanah.
            """)
            st.json(hasil_stabil)

        # ... (Lanjut ke Visualisasi Gambar) ...

        # D. VISUALISASI GAMBAR
        st.markdown("---")
        st.subheader("📐 Visualisasi Profil Memanjang")
        try:
            fig_section = gambar_potongan_bertingkat(
                n_terjun = hasil["Jumlah Terjun"],
                H_total  = H_total,
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
            st.warning(f"Gagal memuat gambar: {e_img}")

        # E. TABEL DETAIL HIDROLIS
        st.markdown("---")
        with st.expander("📊 Lihat Detail Angka Hidrolis", expanded=False):
            df_hasil = pd.DataFrame(list(hasil.items()), columns=["Parameter", "Nilai"])
            st.table(df_hasil)

    except Exception as e:
        st.error(f"Terjadi kesalahan sistem: {e}")
        st.info("Tips: Pastikan file `hitung_terjun.py` dan `cek_stabilitas.py` sudah benar.")

else:
    st.info("👈 Masukkan parameter di sidebar kiri, lalu tekan tombol **Hitung & Analisis**.")

