import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def gambar_detail_kolam(tipe_usbr, L_kolam, y1, y2, hs, t_lantai):
    """
    Menggambar Detail Pembesian / Layout Kolam Olak (Fokus pada USBR III/Standard)
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Koordinat Dasar
    x_awal = 0
    x_akhir = L_kolam
    y_lantai = 0
    y_bawah_beton = -t_lantai
    
    # 1. GAMBAR STRUKTUR UTAMA (Lantai & Dinding Potongan)
    # Lantai Beton
    rect_lantai = patches.Rectangle((x_awal, y_bawah_beton), L_kolam, t_lantai, 
                                    linewidth=2, edgecolor='black', facecolor='lightgray', hatch='///')
    ax.add_patch(rect_lantai)
    
    # Dinding/Cutoff Hulu (Simbolis)
    ax.plot([0, 0], [0, y1*1.5], 'k-', linewidth=3)
    
    # 2. GAMBAR KOMPONEN USBR (Berdasarkan Tipe)
    
    # --- LOGIKA USBR III (Gigi & Blok) ---
    if "USBR III" in tipe_usbr:
        # A. CHUTE BLOCKS (Gigi Hulu) - Biasanya tinggi = y1
        h_chute = y1
        w_chute = 0.75 * y1 # Lebar visual saja
        # Gambar satu blok sebagai representasi
        rect_chute = patches.Rectangle((0, 0), w_chute, h_chute, 
                                       linewidth=1, edgecolor='black', facecolor='gray')
        ax.add_patch(rect_chute)
        ax.text(w_chute/2, h_chute + 0.1, "Chute\nBlock", fontsize=8, ha='center', color='red')

        # B. BAFFLE BLOCKS (Gigi Benturan) - Biasanya di 0.8 L_kolam atau jarak tertentu
        # Standar USBR III: Lokasi sekitar 0.8 * y2 dari kaki terjun
        x_baffle = 0.8 * y2
        h_baffle = y1 # Aproksimasi visual (aslinya ada hitungan rumit h3)
        w_baffle = 0.75 * h_baffle
        
        rect_baffle = patches.Rectangle((x_baffle, 0), w_baffle, h_baffle, 
                                        linewidth=1, edgecolor='black', facecolor='gray')
        ax.add_patch(rect_baffle)
        ax.text(x_baffle + w_baffle/2, h_baffle + 0.1, "Baffle\nPier", fontsize=8, ha='center', color='red')
        
        # Dimensi Jarak
        ax.annotate(f"0.8 y2 = {round(x_baffle,2)}m", xy=(x_baffle, -0.2), xytext=(x_baffle, -0.5),
                    arrowprops=dict(arrowstyle='->'), ha='center', fontsize=8)

    # --- END SILL (Ambang Akhir) - Semua Tipe yang punya hs > 0 ---
    if hs > 0:
        # Ambang Solid
        x_sill = x_akhir
        # Gambar bentuk trapesium atau kotak untuk sill
        sill_points = [
            (x_sill, 0), 
            (x_sill, hs), 
            (x_sill + 0.2, hs), # Tebal atas sill 20cm
            (x_sill + 0.2, -t_lantai), # Tanam ke bawah
            (x_sill, -t_lantai)
        ]
        poly_sill = patches.Polygon(sill_points, closed=True, edgecolor='black', facecolor='gray')
        ax.add_patch(poly_sill)
        ax.text(x_sill, hs + 0.1, f"End Sill\nH={hs}m", fontsize=9, ha='center', fontweight='bold')
    
    # 3. GAMBAR PROFIL AIR (Hydraulic Jump)
    x_air = np.linspace(0, L_kolam, 100)
    # Kurva pendekatan loncatan air
    y_air = y1 + (y2 - y1) * (x_air / (0.6*L_kolam))**0.5 # Naik cepat
    y_air[y_air > y2] = y2 # Flat setelah mencapai y2
    
    ax.plot(x_air, y_air, 'b-', linewidth=2, alpha=0.7)
    ax.fill_between(x_air, 0, y_air, color='cyan', alpha=0.2)
    
    # Label y1 dan y2
    ax.annotate(f"y1={y1}m", xy=(0.1, y1), xytext=(0.5, y1+0.5), arrowprops=dict(arrowstyle='->'))
    ax.annotate(f"y2={y2}m", xy=(L_kolam*0.8, y2), xytext=(L_kolam*0.8, y2+0.5), arrowprops=dict(arrowstyle='->'))

    # Label L Kolam
    ax.annotate(f"Panjang Kolam L = {L_kolam}m", xy=(L_kolam/2, -0.1), xytext=(L_kolam/2, -t_lantai - 0.5), 
                arrowprops=dict(arrowstyle='<->'), ha='center', fontsize=10, fontweight='bold')

    # Formatting
    ax.set_title(f"Detail Desain Kolam Olak (Tipe: {tipe_usbr})", fontsize=12, fontweight='bold')
    ax.set_xlim(-1, L_kolam + 1)
    ax.set_ylim(-t_lantai - 1, max(y2, hs) + 1.5)
    ax.set_aspect('equal')
    ax.axis('off') # Matikan axis grid biar seperti gambar teknis
    
    return fig