def cek_stabilitas(
    B,          # Lebar saluran
    L,          # Panjang lantai kolam
    t,          # Tebal lantai beton
    y1,         # Kedalaman awal loncatan
    y2,         # Kedalaman akhir loncatan
    H_drop,     # Tinggi terjun (penting untuk uplift!)
    qa=150,     # Daya dukung tanah izin
    gamma_c=24, # Berat jenis beton (kN/m3)
    gamma_w=9.81 # Berat jenis air (kN/m3)
):
    """
    Cek stabilitas KHUSUS untuk LANTAI Kolam Olak (Slab Stability).
    Fokus pada Gaya Angkat (Uplift) dan Daya Dukung Tanah.
    """
    
    # --- 1. GAYA VERTIKAL KE BAWAH (PENAHAN) ---
    # Berat Sendiri Lantai Beton
    W_beton = L * B * t * gamma_c
    
    # Berat Air di atas lantai (Weight of Water)
    # Kita asumsikan profil air miring dari y1 ke y2 (Volume trapesium)
    # Ini membantu menekan lantai ke bawah
    Vol_air = 0.5 * (y1 + y2) * L * B
    W_air   = Vol_air * gamma_w
    
    Total_Berat = W_beton + W_air

    # --- 2. GAYA VERTIKAL KE ATAS (GAYA ANGKAT / UPLIFT) ---
    # Asumsi: Tidak ada cutoff pile (kondisi terburuk/konservatif).
    # Tekanan air di bawah lantai hulu (Px) diperkirakan setinggi muka air hilir + 50% tinggi terjun
    # (Ini pendekatan Lane/Bligh sederhana jika tanpa hitungan rembesan detail)
    Head_hulu_bawah_tanah = y2 + (0.5 * H_drop) 
    Head_hilir_bawah_tanah = y2
    
    # Gaya Uplift (Volume prisma tekanan di bawah lantai)
    Uplift_Force = 0.5 * (Head_hulu_bawah_tanah + Head_hilir_bawah_tanah) * L * B * gamma_w

    # --- 3. HITUNG SAFETY FACTOR (SF) ---
    
    # A. Cek Pengapungan (Flotation/Uplift)
    # Apakah Berat > Gaya Angkat?
    SF_uplift = Total_Berat / Uplift_Force if Uplift_Force > 0 else 99.0
    
    # B. Cek Tekanan Tanah (Bearing Capacity)
    # Tekanan Netto ke tanah = (Berat Total - Uplift) / Luas
    # Jika negatif, berarti lantai terangkat (bahaya!)
    Tekanan_Netto = (Total_Berat - Uplift_Force) / (B * L)
    
    # Jika Uplift > Berat, tekanan tanah jadi 0 (mengapung), bukan negatif secara fisik
    if Tekanan_Netto < 0: Tekanan_Netto = 0 

    return {
        "Berat Beton (kN)": round(W_beton, 2),
        "Berat Air (kN)": round(W_air, 2),
        "Gaya Uplift (kN)": round(Uplift_Force, 2),
        
        # Hasil Analisis
        "SF Uplift": round(SF_uplift, 2),
        "Tekanan Tanah (kN/m2)": round(Tekanan_Netto, 2),
        
        # Kesimpulan Boolean
        "Aman Uplift": SF_uplift >= 1.5,      # Standar umum > 1.5
        "Aman Daya Dukung": Tekanan_Netto <= qa
    }
