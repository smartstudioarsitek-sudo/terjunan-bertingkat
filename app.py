import streamlit as st
import pandas as pd

# Import modul perhitungan custom
from hitung_terjun import hitung_bangunan_terjun
from cek_stabilitas import cek_stabilitas

# Import modul gambar (Existing)
from draw_section import gambar_potongan_bertingkat
from draw_plan import gambar_denah_bertingkat

# Import modul gambar (BARU - Tambahan)
from draw_detail import gambar_detail_kolam
from draw_3d import gambar_3d_terjun

# Import modul export
from export_utils import generate_excel, generate_dxf_potongan, generate_dxf_denah

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Desain Bangunan Terjun Pro", layout="wide")

st.title("🌊 Desain Bangunan Terjun & Kolam Olak (Pro V2)")
st.caption("Dilengkapi Visualisasi Detail USBR & 3D Isometri")
st.markdown("---")

# --- 2. INPUT DATA (SIDEBAR) ---
with st.sidebar:
    st.header("1️⃣ Parameter Hidrolis")
    # Gunakan key agar value tersimpan di state
    Q = st.number_input("Debit (Q) m³/det", 0.01, 20.00, 1.50, 0.05, key="Q")
    B = st.number_input("Lebar (B) m", 0.5, 15.0, 2.0, 0.1, key="B")
    H_total = st.number_input("Total Tinggi (H) m", 0.5, 30.0, 3.5, 0.1, key="H_total")
    H_max = st.number_input("Tinggi Max/Trap (m)", 0.3, 4.0, 1.5, 0.1, key="H_max")
    
    st.markdown("---")
    st.header("⚙️ Opsi Desain")
    mode_hemat = st.checkbox("✅ Mode Hemat (Kolam di Bawah Saja)", value=True, 
                             help="Untuk H < 1.2m, lantai tengah dibuat pendek tanpa kolam olak penuh.", key="mode_hemat")

    st.markdown("---")
    st.header("2️⃣ Parameter Struktur")
    t_lantai = st.number_input("Tebal Lantai (m)", 0.2, 2.0, 0.5, 0.05, key="t_lantai")
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
        # A. HITUNGAN HIDROLIS
        hasil = hitung_bangunan_terjun(Q, B, H_total, H_max, mode_hemat)
        
        # B. HITUNGAN STABILITAS
        # Stabilitas dicek pada kolam terakhir (Lantai Final)
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
# Bagian ini akan selalu dijalankan jika 'sudah_dihitung' bernilai True

if st.session_state['sudah_dihitung']:
    hasil = st.session_state['hasil']
    stabil = st.session_state['stabil']

    # --- TAB BARU YANG LEBIH LENGKAP ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Potongan",          # Tab Lama
        "🔍 Detail Kolam",      # TAB BARU 1
        "🧊 3D Isometri",       # TAB BARU 2
        "📐 Denah Situasi",     # Tab Lama
        "📑 Rekap & Download",  # Tab Lama
        "📚 Manual & Referensi" # Tab Lama
    ])

    # --- TAB 1: POTONGAN MEMANJANG ---
    with tab1:
        st.subheader(f"Visualisasi Potongan ({hasil['Desain Mode']})")
        
        # Metric Bar
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

    # --- TAB 2: DETAIL KOLAM (FITUR BARU) ---
    with tab2:
        st.subheader("🔍 Detail Teknis Kolam Olak (Tipe Akhir)")
        st.markdown(f"Detail di bawah adalah pembesian komponen peredam energi untuk tipe **{hasil['Tipe Kolam']}**.")
        
        col_d1, col_d2 = st.columns([1, 2])
        
        with col_d1:
            st.success("Parameter Desain")
            st.dataframe(pd.DataFrame({
                "Parameter": ["Panjang Kolam (L)", "Tinggi Ambang (End Sill)", "Kedalaman Awal (y1)", "Kedalaman Akhir (y2)", "Tebal Lantai"],
                "Nilai (m)": [hasil['Panjang Kolam Final (m)'], hasil['Tinggi End Sill (m)'], hasil['Kedalaman di Kaki (y1)'], hasil['Kedalaman Konjugasi (y2)'], t_lantai]
            }), hide_index=True)
            
        with col_d2:
            try:
                fig_detail = gambar_detail_kolam(
                    tipe_usbr=hasil["Tipe Kolam"],
                    L_kolam=hasil["Panjang Kolam Final (m)"],
                    y1=hasil["Kedalaman di Kaki (y1)"],
                    y2=hasil["Kedalaman Konjugasi (y2)"],
                    hs=hasil["Tinggi End Sill (m)"],
                    t_lantai=t_lantai
                )
                st.pyplot(fig_detail, use_container_width=True)
            except Exception as e:
                st.error(f"Error gambar detail: {e}")
                
    # --- TAB 3: 3D ISOMETRI (FITUR BARU) ---
    with tab3:
        st.subheader("🧊 Visualisasi 3D Isometri")
        st.caption("Model 3D skematik untuk memahami geometri bangunan terjun bertingkat.")
        try:
            fig_3d = gambar_3d_terjun(
                n_terjun=hasil["Jumlah Terjun"],
                B=B,
                H_total=H_total,
                H_drop=hasil["Tinggi Terjun per Tingkat (m)"],
                L_drop=hasil["Panjang Jatuhan Ld (m)"],
                L_kolam_inter=hasil["Panjang Kolam Intermediate (m)"],
                L_kolam_final=hasil["Panjang Kolam Final (m)"],
                mode_hemat=mode_hemat
            )
            st.pyplot(fig_3d, use_container_width=True)
        except Exception as e:
            st.error(f"Error gambar 3D: {e}")

    # --- TAB 4: DENAH SITUASI ---
    with tab4:
        st.subheader("Visualisasi Denah Situasi (Tampak Atas)")
        try:
            fig_plan = gambar_denah_bertingkat(
                hasil["Jumlah Terjun"], B, hasil["Panjang Jatuhan Ld (m)"],
                hasil["Panjang Kolam Intermediate (m)"], hasil["Panjang Kolam Final (m)"]
            )
            st.pyplot(fig_plan, use_container_width=True)
        except Exception as e:
            st.warning(f"Gagal menampilkan gambar denah: {e}")

    # --- TAB 5: DOWNLOAD & REKAP ---
    with tab5:
        st.header("📥 Download Data & Gambar Kerja")
        
        # Tampilkan Dataframe Preview
        col_a, col_b = st.columns(2)
        with col_a: 
            st.write("##### Rekapitulasi Hidrolis")
            st.dataframe(pd.DataFrame(list(hasil.items()), columns=["Hidrolis", "Nilai"]), hide_index=True, use_container_width=True)
        with col_b: 
            st.write("##### Cek Stabilitas (Lantai Bawah)")
            st.dataframe(pd.DataFrame(list(stabil.items()), columns=["Stabilitas", "Nilai"]), hide_index=True, use_container_width=True)
            if stabil["Aman Uplift"] and stabil["Aman Daya Dukung"]:
                st.success("✅ Struktur AMAN")
            else:
                st.error("❌ Struktur TIDAK AMAN, Coba pertebal lantai!")
        
        st.divider()
        
        # 1. Excel
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

    # --- TAB 6: MANUAL & REFERENSI ---
    with tab6:
        st.title("📚 Manual Teknis & Referensi")
        
        st.header("1. Acuan Standar")
        st.markdown("""
        * **KP-04**: Standar Perencanaan Irigasi - Bangunan Utama.
        * **USBR**: Design of Small Dams (Bureau of Reclamation).
        """)
        
        st.header("2. Rumus Penting")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.latex(r"y_c = \sqrt[3]{\frac{q^2}{g}}")
            st.caption("Kedalaman Kritis")
        with col_r2:
            st.latex(r"SF_{Uplift} = \frac{W_{total}}{F_{uplift}} \ge 1.5")
            st.caption("Safety Factor Uplift")

        st.info("Tips: Gunakan 'Mode Hemat' untuk bangunan terjun tinggi dengan debit kecil agar biaya konstruksi lebih murah.")

elif not tombol_hitung:
    # Tampilan awal jika belum pernah menghitung
    st.info("👈 Silakan masukkan parameter desain di sidebar kiri, lalu tekan tombol **Hitung & Analisis**.")
