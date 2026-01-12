import numpy as np

def hitung_bangunan_terjun(
    Q,
    B,
    H_total,
    H_max_tiap_terjun,
    g=9.81
):
    """
    Perhitungan bangunan terjun bertingkat sederhana
    """

    # Jumlah terjun
    n_terjun = int(np.ceil(H_total / H_max_tiap_terjun))

    # Tinggi tiap terjun
    H_tiap = H_total / n_terjun

    # Kedalaman kritis (saluran persegi)
    yk = (Q**2 / (g * B**2)) ** (1/3)

    # Kecepatan aliran
    V = Q / (B * yk)

    # Energi spesifik
    E = yk + (V**2) / (2 * g)

    # Panjang kolam olak (pendekatan sederhana KP)
    L_olak = 5 * yk

    return {
        "Jumlah Terjun": n_terjun,
        "Tinggi Terjun per Tingkat (m)": round(H_tiap, 3),
        "Kedalaman Kritis yk (m)": round(yk, 3),
        "Kecepatan Aliran (m/s)": round(V, 3),
        "Energi Spesifik (m)": round(E, 3),
        "Panjang Kolam Olak (m)": round(L_olak, 3),
    }
