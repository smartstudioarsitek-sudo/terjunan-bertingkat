import numpy as np
# Pastikan file usbr_stilling.py ada di folder yang sama
from usbr_stilling import hitung_usbr 

def hitung_bangunan_terjun(
    Q,
    B,
    H_total,
    H_max_tiap_terjun,
    g=9.81
):
    """
    Perhitungan bangunan terjun bertingkat dengan integrasi USBR
    sesuai kaidah hidrolika (Bernoulli + Momentum).
    """

    # 1. Tentukan Geometri Terjun
    n_terjun = int(np.ceil(H_total / H_max_tiap_terjun))
    # Hindari pembagian dengan nol jika n_terjun 0 (safety code)
    if n_terjun == 0: n_terjun = 1
        
    H_tiap = H_total / n_terjun  # Tinggi jatuh per step (Z)

    # 2. Hitung Kondisi di Ambang (Critical Flow)
    q = Q / B
    yk = (q**2 / g) ** (1/3)  # Critical depth
    
    # 3. Hitung Kondisi di Kaki Terjun (Sebelum Loncatan / Toe)
    # Menggunakan Persamaan Energi (Bernoulli):
    # E_hulu + Z = E_hilir
    # (yk + V_c^2/2g) + H_tiap = y1 + V1^2/2g
    
    # Energi total hulu dari dasar kolam olak
    # E_critical = 1.5 * yk. Ditambah tinggi jatuh H_tiap.
    E_total_hulu = H_tiap + (1.5 * yk) 
    
    # Mencari y1 (kedalaman superkritis) dengan pendekatan Velocity Head
    # V1 mendekati sqrt(2*g * Head)
    V1_approx = np.sqrt(2 * g * E_total_hulu) 
    y1 = q / V1_approx
    
    # Iterasi sederhana untuk presisi y1 (opsional, tapi lebih akurat)
    for _ in range(3):
        V1 = q / y1
        E_calc = y1 + (V1**2)/(2*g)
        # Koreksi y1 berdasarkan selisih energi (metode Newton-Raphson sederhana)
        diff = E_calc - E_total_hulu
        if abs(diff) < 0.001: break
        y1 = y1 - (diff / (1 - (V1**2)/(g*y1))) # Turunan dE/dy = 1 - Fr^2

    # Recalculate V1 final
    V1 = q / y1
    
    # 4. Hitung Kolam Olak menggunakan logika USBR
    # Memanggil fungsi dari file usbr_stilling.py
    data_usbr = hitung_usbr(Q, B, y1, g)
    
    # Panjang kolam total sebaiknya ditambah jarak jatuhan (drop length)
    # Rumus Rand (1955) untuk jarak jatuhan Ld:
    drop_number = (q**2) / (g * H_tiap**3)
    L_drop = 4.30 * H_tiap * (drop_number ** 0.27)
    
    L_kolam_usbr = data_usbr["Panjang Kolam"]
    L_total_per_step = L_drop + L_kolam_usbr

    return {
        "Jumlah Terjun": n_terjun,
        "Tinggi Terjun per Tingkat (m)": round(H_tiap, 3),
        "Debit Persatuan Lebar (q)": round(q, 3),
        "Kedalaman Kritis yc (m)": round(yk, 3),
        "Kedalaman di Kaki (y1)": round(y1, 3),
        # PERBAIKAN DI SINI: Menggunakan key "y2 (m)" sesuai usbr_stilling.py terbaru
        "Kedalaman Konjugasi (y2)": data_usbr.get("y2 (m)", 0), 
        "Tipe Kolam": data_usbr["Tipe USBR"],
        "Panjang Jatuhan Ld (m)": round(L_drop, 3),
        "Panjang Loncatan Lj (m)": round(L_kolam_usbr, 3),
        "Panjang Total Lantai (Ld+Lj) (m)": round(L_total_per_step, 3),
        "Tinggi End Sill (m)": data_usbr["End Sill"]
    }
