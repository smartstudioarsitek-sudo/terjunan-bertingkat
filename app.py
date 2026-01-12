import streamlit as st
import pandas as pd
from hitung_terjun import hitung_bangunan_terjun
from cek_stabilitas import cek_stabilitas
from draw_section import gambar_potongan_bertingkat
from draw_plan import gambar_denah_bertingkat
from export_utils import generate_excel, generate_dxf_potongan, generate_dxf_denah

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Desain Bangunan Terjun Pro", layout="wide")

st.title("🌊 Desain Bangunan Terjun & Kolam Olak (Pro)")
st.markdown("---")

# --- 2. INPUT DATA (SIDEBAR) ---
with st.sidebar:
    st.header("1️⃣ Parameter Hidrolis")
    # Gunakan key agar value tersimpan di state
    Q = st.number_input("Debit (Q) m³/det", 0.01, 10.00, 1.50, 0.05, key="Q")
    B = st.number_input("Lebar (B) m", 0.5, 10.0, 2.0, 0.1, key="B")
    H_total = st.number_input("Total Tinggi (H) m", 0.5, 20.0, 3.5, 0.1, key="H_total")
    H_max = st.number_input("Tinggi Max/Trap (m)", 0.3, 3.0, 1.5, 0.1, key="H_max")
    
    st.markdown("---")
    st.header("⚙️ Opsi Desain")
    mode_hemat = st.checkbox("✅ Mode Hemat (Kolam di Bawah Saja)", value=True, 
                             help="Untuk H < 1.2m, lantai tengah dibuat pendek tanpa kolam olak penuh.", key="mode_hemat")

    st.markdown("---")
    st.header("2️⃣ Parameter Struktur")
    t_lantai = st.number_input("Tebal Lantai (m)", 0.2, 1.5, 0.5, 0.05, key="t_lantai")
    qa_tanah = st.number_input("Daya Dukung (kN/m²)", 10.0, 500.0, 150.0, 10.0, key="qa_tanah")
    
    st.markdown("---")
    tombol_hitung = st.button("🚀 Hitung & Analisis", type="primary")

# --- 3. LOGIKA UTAMA DENGAN SESSION STATE ---

# Inisialisasi state jika belum ada
if 'hasil' not in st.session_state:
    st.session_state['hasil'] = None
if 'stabil' not in st.session_state:
    st.session_state['stabil'] = None
if 'sudah_dihitung' not in st.session_state:
    st.session_state['sudah_dihitung'] = False

# Jika tombol ditekan, lakukan perhitungan dan SIMPAN ke session_state
if tombol_hitung:
    try:
        # A. HITUNGAN
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max, mode_hemat)
        
        # Stabilitas
        L_stabil = hasil["Panjang Lantai Final (m)"] - hasil["Panjang Jatuhan Ld (m)"]
        stabil = cek_stabilitas(
            B=B, L=L_stabil, t=t_lantai,
            y1=hasil["Kedalaman di Kaki (y1)"], y2=hasil["Kedalaman Konjugasi (y2)"],
            H_drop=hasil["Tinggi Terjun per Tingkat (m)"], qa=qa_tanah
        )
        
        # Simpan ke memori
        st.session_state['hasil'] = hasil
        st.session_state['stabil'] = stabil
        st.session_state['sudah_dihitung'] = True
        
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menghitung: {e}")

# --- 4. TAMPILKAN HASIL DARI SESSION STATE ---
# Bagian ini akan selalu dijalankan jika 'sudah_dihitung' bernilai True,
# meskipun tombol hitung tidak sedang ditekan (misal saat ganti tab).

if st.session_state['sudah_dihitung']:
    hasil = st.session_state['hasil']
    stabil = st.session_state['stabil']

    # B. TABS UTAMA
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Potongan", "📐 Denah Situasi", "📑 Rekap & Download", "📚 Manual & Referensi"])

    # --- TAB 1: POTONGAN ---
    with tab1:
        st.subheader(f"Visualisasi Potongan ({hasil['Desain Mode']})")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Jml Trap", hasil["Jumlah Terjun"])
        c2.metric("Panjang Tengah", f"{hasil['Panjang Lantai Intermediate (m)']} m")
        c3.metric("Panjang Bawah", f"{hasil['Panjang Lantai Final (m)']} m")
        c4.metric("Tipe USBR", hasil["Tipe Kolam"])

        try:
            fig_section = gambar_potongan_bertingkat(
                hasil["Jumlah Terjun"], H_total, hasil["Tinggi Terjun per Tingkat (m)"],
                hasil["Panjang Jatuhan Ld (m)"], hasil["Panjang Kolam Intermediate (m)"], 
                hasil["Panjang Kolam Final (m)"], hasil["Kedalaman di Kaki (y1)"], 
                hasil["Kedalaman Konjugasi (y2)"], hasil["Tinggi End Sill (m)"], hasil["Kedalaman Kritis yc (m)"]
            )
            st.pyplot(fig_section, use_container_width=True)
        except Exception as e:
            st.warning(f"Gagal menampilkan gambar potongan: {e}")

    # --- TAB 2: DENAH ---
    with tab2:
        st.subheader("Visualisasi Denah Situasi")
        try:
            fig_plan = gambar_denah_bertingkat(
                hasil["Jumlah Terjun"], B, hasil["Panjang Jatuhan Ld (m)"],
                hasil["Panjang Kolam Intermediate (m)"], hasil["Panjang Kolam Final (m)"]
            )
            st.pyplot(fig_plan, use_container_width=True)
        except Exception as e:
            st.warning(f"Gagal menampilkan gambar denah: {e}")

    # --- TAB 3: DOWNLOAD ---
    with tab3:
        st.header("📥 Download Data & Gambar Kerja")
        
        # Dataframe Preview
        col_a, col_b = st.columns(2)
        with col_a: st.dataframe(pd.DataFrame(list(hasil.items()), columns=["Hidrolis", "Nilai"]), hide_index=True)
        with col_b: st.dataframe(pd.DataFrame(list(stabil.items()), columns=["Stabilitas", "Nilai"]), hide_index=True)
        
        st.divider()
        
        # 1. Excel
        # Ambil input terbaru dari session state widget
        input_dict = {
            "Q": Q, "B": B, "H Total": H_total, "H Max": H_max, 
            "Mode Hemat": mode_hemat, "Tebal Lantai": t_lantai, "Qa Tanah": qa_tanah
        }
        excel_data = generate_excel(input_dict, hasil, stabil)
        st.download_button("📥 Download Laporan Excel (.xlsx)", excel_data, "Laporan_Desain.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        st.write("---")
        
        # 2. CAD Buttons
        col_cad1, col_cad2 = st.columns(2)
        
        with col_cad1:
            dxf_pot = generate_dxf_potongan(
                hasil["Jumlah Terjun"], H_total, hasil["Tinggi Terjun per Tingkat (m)"],
                hasil["Panjang Jatuhan Ld (m)"], hasil["Panjang Kolam Intermediate (m)"], 
                hasil["Panjang Kolam Final (m)"], hasil["Kedalaman di Kaki (y1)"], 
                hasil["Kedalaman Konjugasi (y2)"], hasil["Tinggi End Sill (m)"], hasil["Kedalaman Kritis yc (m)"]
            )
            st.download_button("📐 Download CAD Potongan (.dxf)", dxf_pot, "Potongan_Terjun.dxf", "application/dxf")
        
        with col_cad2:
            dxf_denah = generate_dxf_denah(
                hasil["Jumlah Terjun"], B, hasil["Panjang Jatuhan Ld (m)"],
                hasil["Panjang Kolam Intermediate (m)"], hasil["Panjang Kolam Final (m)"]
            )
            st.download_button("📐 Download CAD Denah (.dxf)", dxf_denah, "Denah_Terjun.dxf", "application/dxf")

    # --- TAB 4: MANUAL & REFERENSI ---
    with tab4:
        st.title("📚 Manual Teknis & Referensi")
        
        st.header("1. Acuan Standar")
        st.markdown("""
        Aplikasi ini dikembangkan berdasarkan standar perencanaan irigasi yang berlaku di Indonesia:
        * **KP-04 (Standar Perencanaan Irigasi - Bagian Bangunan Utama)**: Digunakan untuk penentuan dimensi hidrolis bangunan terjun.
        * **USBR (Design of Small Dams)**: Digunakan untuk penentuan tipe kolam olak (*stilling basin*) berdasarkan Bilangan Froude ($Fr$).
        """)
        
        st.header("2. Rumus Hidrolika")
        st.markdown("Berikut adalah rumus-rumus kunci yang digunakan dalam perhitungan:")
        
        st.subheader("A. Kedalaman Kritis ($y_c$)")
        st.latex(r"y_c = \sqrt[3]{\frac{q^2}{g}}")
        st.caption("Dimana $q = Q/B$ adalah debit per satuan lebar.")

        st.subheader("B. Kecepatan & Kedalaman Awal ($V_1, y_1$)")
        st.markdown("Dihitung menggunakan Persamaan Energi (Bernoulli) dari hulu ke kaki terjun:")
        st.latex(r"E_{hulu} + Z = E_{hilir} \rightarrow H + 1.5 y_c = y_1 + \frac{V_1^2}{2g}")

        st.subheader("C. Bilangan Froude ($Fr$) & Kedalaman Konjugasi ($y_2$)")
        st.latex(r"Fr_1 = \frac{V_1}{\sqrt{g y_1}}")
        st.markdown("Rumus Belanger untuk Hydraulic Jump:")
        st.latex(r"y_2 = \frac{y_1}{2} (\sqrt{1 + 8 Fr_1^2} - 1)")

        st.header("3. Logika Desain")
        st.subheader("Fitur Mode Hemat (Cascaded Drop)")
        st.markdown("""
        Jika opsi **Mode Hemat** diaktifkan, aplikasi menggunakan logika berikut:
        1.  Jika tinggi terjun per trap ($H$) < 1.2 meter:
            * Trap Tengah (Intermediate): Lantai dibuat pendek ($L \approx L_{drop} + 0.5m$).
            * Trap Akhir (Final): Lantai dibuat normal sesuai hitungan USBR.
        2.  Jika $H > 1.2$ meter: Mode hemat dimatikan otomatis demi keamanan struktur.
        """)
        
        st.header("4. Analisa Stabilitas")
        st.markdown("Analisa dilakukan pada lantai kolam olak terbawah (kondisi paling kritis).")
        st.latex(r"SF_{Uplift} = \frac{W_{beton} + W_{air}}{F_{uplift}} \ge 1.5")
        st.latex(r"\sigma_{tanah} = \frac{\Sigma V}{A} \le \bar{\sigma}_{izin}")

elif not tombol_hitung:
    # Tampilan awal jika belum pernah menghitung
    st.info("👈 Silakan masukkan parameter desain di sidebar kiri, lalu tekan tombol **Hitung & Analisis**.")
