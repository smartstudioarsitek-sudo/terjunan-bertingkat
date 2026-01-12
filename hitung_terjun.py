import numpy as np
# Kita masukkan logika USBR langsung di sini untuk optimasi penuh
# agar bisa memilih yang PALING PENDEK

def hitung_bangunan_terjun(
    Q,
    B,
    H_total,
    H_max_tiap_terjun,
    g=9.81
):
    """
    Perhitungan bangunan terjun bertingkat dengan OPTIMASI PANJANG MINIMUM.
    Menggunakan pendekatan USBR III (gigi) atau Minimum Impact Length.
    """

    # 1. Tentukan Geometri Terjun
    n_terjun = int(np.ceil(H_total / H_max_tiap_terjun))
    if n_terjun == 0: n_terjun = 1
    H_tiap = H_total / n_terjun

    # 2. Hitung Kondisi di Ambang
    q = Q / B
    yk = (q**2 / g) ** (1/3)  # Critical depth
    
    # 3. Hitung Kondisi di Kaki (Toe)
    # Energi Hulu = H_tiap + 1.5 yk
    E_total = H_tiap + (1.5 * yk)
    
    # Cari y1 (Iterasi cepat)
    y1 = 0.1 * yk # tebakan awal
    for _ in range(10):
        v1 = q / y1
        f_val = y1 + (v1**2)/(2*g) - E_total
        df_val = 1 - (v1**2)/(g*y1)
        y1_new = y1 - f_val/df_val
        if abs(y1_new - y1) < 0.001: break
        y1 = y1_new
    
    V1 = q / y1
    Fr1 = V1 / np.sqrt(g * y1)
    
    # 4. Hitung y2 (Conjugate Depth)
    y2 = 0.5 * y1 * (np.sqrt(1 + 8 * Fr1**2) - 1)

    # --- 5. LOGIKA OPTIMASI "TERPENDEK" (SESUAI REQUEST) ---
    
    # Hitung Jarak Jatuhan (Drop Length) - Rumus Rand
    # Ini adalah jarak minimal agar air tidak menimpa lantai beton terlalu ke ujung
    drop_number = (q**2) / (g * H_tiap**3)
    L_drop = 4.30 * H_tiap * (drop_number ** 0.27)

    # Hitung Panjang Kolam (L_jump)
    # KP-04 & USBR:
    # USBR I/II (Polos) -> butuh L = 5 s.d 6 * y2 (PANJANG BANGET)
    # USBR III (Gigi)   -> butuh L = 2.5 s.d 2.7 * y2 (PENDEK)
    
    # KITA PAKSA PAKAI MODE TERPENDEK (ASUMSI PAKAI BLOK/GIGI JIKA PERLU)
    # Jika Fr < 1.7 (Loncatan undular), tidak perlu kolam, cukup lantai lindung
    if Fr1 < 1.7:
        tipe_kolam = "Lantai Minim (Undular)"
        L_jump = 2.0 * y2 # Sangat pendek, hanya untuk proteksi
        hs = 0
    else:
        # Jika Fr tinggi, kita pakai rasio USBR III (paling efisien)
        # Asumsinya: User akan memasang blok muka/gigi jika Fr > 4.5
        tipe_kolam = "USBR III (Optimasi Pendek)"
        L_jump = 2.5 * y2 # Rasio terpendek yang aman secara teknis
        hs = 0.15 * y2 # Tinggi ambang (End Sill)
        
        # Safety check: Jangan sampai L_jump < 1 meter untuk kemudahan konstruksi
        if L_jump < 1.0: L_jump = 1.0

    # Total Panjang Lantai per Trap
    L_total_per_step = L_drop + L_jump

    return {
        "Jumlah Terjun": n_terjun,
        "Tinggi Terjun per Tingkat (m)": round(H_tiap, 3),
        "Debit Persatuan Lebar (q)": round(q, 3),
        "Kedalaman Kritis yc (m)": round(yk, 3),
        "Kedalaman di Kaki (y1)": round(y1, 3),
        "Kedalaman Konjugasi (y2)": round(y2, 3), # Sudah float, aman
        "Tipe Kolam": tipe_kolam,
        "Panjang Jatuhan Ld (m)": round(L_drop, 3),
        "Panjang Loncatan Lj (m)": round(L_jump, 3),
        "Panjang Total Lantai (Ld+Lj) (m)": round(L_total_per_step, 3),
        "Tinggi End Sill (m)": round(hs, 3)
    }
