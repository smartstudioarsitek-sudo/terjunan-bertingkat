import numpy as np

def hitung_usbr(Q, B, y1, g=9.81):
    V1 = Q / (B * y1)
    Fr1 = V1 / np.sqrt(g * y1)

    y2 = 0.5 * y1 * (np.sqrt(1 + 8 * Fr1**2) - 1)

    if Fr1 < 2.5:
        tipe = "USBR I"
        k = 4.5
        hs = 0.10 * y2
    elif Fr1 < 4.5:
        tipe = "USBR II"
        k = 5.5
        hs = 0.10 * y2
    elif Fr1 < 9.0:
        tipe = "USBR III"
        k = 6.5
        hs = 0.15 * y2
    else:
        tipe = "USBR IV"
        k = 7.5
        hs = 0.20 * y2

    return {
        "Tipe USBR": tipe,
        "Fr1": round(Fr1, 3),
        "y2": round(y2, 3),
        "Panjang Kolam": round(k * y2, 3),
        "End Sill": round(hs, 3),
        "Tebal Lantai": round(max(0.3, 0.25 * y2), 3),
        "Cutoff Hulu": round(0.5 * y2, 3),
        "Cutoff Hilir": round(0.7 * y2, 3),
    }
