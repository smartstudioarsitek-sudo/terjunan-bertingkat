import numpy as np
from usbr_stilling import hitung_usbr 

def hitung_bangunan_terjun(
    Q,
    B,
    H_total,
    H_max_tiap_terjun,
    mode_hemat=False,
    g=9.81
):
    """
    Perhitungan bangunan terjun bertingkat.
    Mendukung Mode Hemat (Kolam Intermediate Pendek).
    """

    # 1. Tentukan Geometri
    n_terjun = int(np.ceil(H_total / H_max_tiap_terjun))
    if n_terjun == 0: n_terjun = 1
    H_tiap = H_total / n_terjun

    # 2. Hitung Hidrolika Dasar
    q = Q / B
    yk = (q**2 / g) ** (1/3)
    
    # 3. Hitung Energi & USBR (Standard)
    # Asumsi conservative: V1 dihitung per step
    # E_total_hulu = H_tiap + (1.5 * yk) 
    V1 = np.sqrt(2 * g * H_tiap) 
    y1 = q / V1
    
    # Panggil fungsi USBR dari file lain
    data_usbr = hitung_usbr(Q, B, y1, g)
    
    # Hitung Jarak Jatuhan (Drop Length)
    drop_number = (q**2) / (g * H_tiap**3)
    L_drop = 4.30 * H_tiap * (drop_number ** 0.27)
    
    # Hitung Panjang Kolam Full (Standard)
    L_kolam_standard = data_usbr["Panjang Kolam"]
    
    # --- LOGIKA MODE HEMAT ---
    # Syarat: User minta hemat DAN tinggi terjun < 1.2 meter (limit aman)
    is_hemat_active = mode_hemat and (H_tiap <= 1.2)
    
    if is_hemat_active:
        # Tipe: Cascaded Drop (Skimming/Step)
        # Lantai Intermediate: Cukup menampung jatuhan air + sedikit safety
        L_kolam_intermediate = 0.5 # Sangat pendek, cuma space transisi
        
        # Lantai Final (Bawah): Tetap harus kolam penuh
        L_kolam_final = L_kolam_standard
        
        tipe_desain = "Mode Hemat (Kolam Hilir Saja)"
    else:
        # Tipe: Full Hydraulic Jump per Step
        L_kolam_intermediate = L_kolam_standard
        L_kolam_final = L_kolam_standard
        
        if mode_hemat and H_tiap > 1.2:
            tipe_desain = "Standard (H terlalu tinggi untuk hemat)"
        else:
            tipe_desain = "Standard (Full USBR)"

    # Total Panjang Lantai (Visualisasi)
    L_total_inter = L_drop + L_kolam_intermediate
    L_total_final = L_drop + L_kolam_final

    return {
        "Jumlah Terjun": n_terjun,
        "Tinggi Terjun per Tingkat (m)": round(H_tiap, 3),
        "Debit Persatuan Lebar (q)": round(q, 3),
        "Kedalaman Kritis yc (m)": round(yk, 3),
        "Kedalaman di Kaki (y1)": round(y1, 3),
        "Kedalaman Konjugasi (y2)": data_usbr.get("y2 (m)", 0),
        "Tipe Kolam": data_usbr["Tipe USBR"],
        "Desain Mode": tipe_desain,
        
        # DATA PENTING UNTUK GAMBAR
        "Panjang Jatuhan Ld (m)": round(L_drop, 3),
        "Panjang Kolam Intermediate (m)": round(L_kolam_intermediate, 3),
        "Panjang Kolam Final (m)": round(L_kolam_final, 3),
        "Panjang Lantai Intermediate (m)": round(L_total_inter, 3),
        "Panjang Lantai Final (m)": round(L_total_final, 3),
        
        "Tinggi End Sill (m)": data_usbr["End Sill"]
    }
