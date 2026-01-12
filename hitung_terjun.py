import numpy as np
# Kita import fungsi USBR yang sudah Anda buat di file lain
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
    H_tiap = H_total / n_terjun  # Tinggi jatuh per step (Z)

    # 2. Hitung Kondisi di Ambang (Critical Flow)
    q = Q / B
    yk = (q**2 / g) ** (1/3)  # Critical depth
    
    # 3. Hitung Kondisi di Kaki Terjun (Sebelum Loncatan / Toe)
    # Menggunakan Persamaan Energi (Bernoulli):
    # E_hulu + Z = E_hilir
    # (yk + V_c^2/2g) + H_tiap = y1 + V1^2/2g
    # Untuk penyederhanaan praktis, kita asumsikan kehilangan energi saat jatuh diabaikan dulu 
    # untuk mendapatkan V1 maksimum (conservative design).
    
    E_total_hulu = H_tiap + (1.5 * yk) # Energi total dari dasar kolam olak
    
    # Mencari y1 (kedalaman superkritis) dengan iterasi atau pendekatan
    # V1 = sqrt(2*g * (H_tiap + 0.5*yk)) adalah pendekatan kasar tapi umum
    # Kita gunakan pendekatan velocity head dominan:
    V1 = np.sqrt(2 * g * (H_tiap)) 
    y1 = q / V1
    
    # Recalculate V1 yang lebih presisi berdasarkan y1
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
        "Kedalaman Konjugasi (y2)": data_usbr["y2"],
        "Tipe Kolam": data_usbr["Tipe USBR"],
        "Panjang Jatuhan Ld (m)": round(L_drop, 3),
        "Panjang Loncatan Lj (m)": round(L_kolam_usbr, 3),
        "Panjang Total Lantai (Ld+Lj) (m)": round(L_total_per_step, 3),
        "Tinggi End Sill (m)": data_usbr["End Sill"]
    }
