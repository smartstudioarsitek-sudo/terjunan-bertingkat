import numpy as np

def hitung_usbr(Q, B, y1, g=9.81):
    # 1. Hitung Parameter Dasar
    V1 = Q / (B * y1)
    Fr1 = V1 / np.sqrt(g * y1)
    
    # Rumus Belanger untuk kedalaman konjugasi (y2)
    y2 = 0.5 * y1 * (np.sqrt(1 + 8 * Fr1**2) - 1)

    # 2. Logika Penentuan Tipe USBR (Sesuai Standar)
    tipe = "Unknown"
    k = 0      # Koefisien panjang kolam (L = k * y2)
    hs = 0     # Tinggi ambang (End Sill)
    catatan = ""

    if Fr1 < 1.7:
        tipe = "Aliran Undular"
        catatan = "Loncatan tidak terbentuk sempurna"
        k = 4.0 # Pendekatan
        hs = 0

    elif Fr1 < 2.5:
        # Pre-Jump / Weak Jump
        tipe = "USBR I"
        catatan = "Loncatan lemah, aliran tenang"
        k = 5.0 # Biasanya 5 * y2
        hs = 0  # USBR I biasanya datar tanpa ambang

    elif Fr1 <= 4.5:
        # Transition / Oscillating Jump -> Paling berbahaya
        tipe = "USBR IV"
        catatan = "Loncatan berombang (Oscillating)"
        # USBR IV butuh kolam panjang untuk meredam gelombang
        k = 6.0 
        # Butuh chute blocks tapi opsional untuk irigasi kecil
        hs = 0.1 * y2 

    else: 
        # Fr1 > 4.5 -> Loncatan Mantap (Steady Jump)
        # Asumsi untuk irigasi V1 < 18 m/s gunakan USBR III
        # USBR III sangat efisien (pendek) karena ada blok muka & blok halang
        if V1 < 18.0:
            tipe = "USBR III"
            catatan = "Loncatan mantap, efisien dengan blok"
            k = 2.7 # USBR III jauh lebih pendek! (Grafik 2.3 - 2.7)
            hs = 0.15 * y2 # Ambang solid
        else:
            tipe = "USBR II"
            catatan = "Kecepatan tinggi (>18m/s)"
            k = 4.3
            hs = 0.1 * y2

    return {
        "Tipe USBR": tipe,
        "Catatan": catatan,
        "Fr1": round(Fr1, 3),
        "Kecepatan V1": round(V1, 3),
        "y1 (m)": round(y1, 3),
        "y2 (m)": round(y2, 3),
        "Panjang Kolam": round(k * y2, 3),
        "End Sill": round(hs, 3),
        "Tebal Lantai": round(max(0.3, 0.25 * y2), 3),
        "Cutoff Hulu": round(0.5 * y2, 3),
        "Cutoff Hilir": round(0.7 * y2, 3),
    }
