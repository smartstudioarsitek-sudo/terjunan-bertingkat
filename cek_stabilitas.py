def cek_stabilitas(
    B,
    L,
    t,
    y1,
    y2,
    gamma_c=24,   # kN/m3 beton
    gamma_w=9.81, # kN/m3 air
    mu=0.6,
    qa=150        # kN/m2 daya dukung izin tanah
):
    # Berat beton
    W = gamma_c * B * L * t

    # Gaya horizontal air
    Fh = 0.5 * gamma_w * y2**2 * B

    # Gaya uplift
    U = 0.5 * gamma_w * (y1 + y2) * B * L

    # Faktor keamanan geser
    FS_geser = (mu * (W - U)) / Fh

    # Momen guling
    M_guling = Fh * (y2 / 3)

    # Momen tahan
    M_tahan = (W - U) * (L / 2)

    FS_guling = M_tahan / M_guling

    # Tekanan tanah
    sigma = (W - U) / (B * L)

    return {
        "Berat Beton (kN)": round(W, 2),
        "Gaya Horizontal Air (kN)": round(Fh, 2),
        "Gaya Uplift (kN)": round(U, 2),
        "FS Geser": round(FS_geser, 2),
        "FS Guling": round(FS_guling, 2),
        "Tekanan Tanah (kN/m2)": round(sigma, 2),
        "Aman Geser": FS_geser >= 1.5,
        "Aman Guling": FS_guling >= 2.0,
        "Aman Daya Dukung": sigma <= qa
    }
