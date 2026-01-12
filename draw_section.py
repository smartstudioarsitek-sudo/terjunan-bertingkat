import matplotlib.pyplot as plt
import numpy as np

def gambar_potongan_detail(H_drop, L_drop, L_kolam, y1, y2, hs, yc):
    """
    Fungsi untuk visualisasi potongan memanjang bangunan terjun
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # --- 1. KOORDINAT STRUKTUR (BETON) ---
    # Hulu (Upstream)
    x_hulu = [-2, 0, 0] 
    y_hulu = [H_drop, H_drop, 0] # Lantai hulu lalu turun vertikal ke 0
    
    # Hilir (Downstream / Kolam Olak)
    x_hilir = [0, L_drop + L_kolam, L_drop + L_kolam]
    y_hilir = [0, 0, hs] # Lantai datar lalu naik ke ambang (end sill)
    
    # Plot Garis Tanah/Beton
    ax.plot(x_hulu, y_hulu, 'k-', linewidth=3, label='Struktur')
    ax.plot(x_hilir, y_hilir, 'k-', linewidth=3)
    
    # --- 2. PROFIL MUKA AIR (BIRU) ---
    # a. Air di Hulu (Datar)
    ax.plot([-2, 0], [H_drop + yc, H_drop + yc], 'b-', linewidth=1)
    
    # b. Air Jatuh (Parabola Sederhana)
    # Membuat kurva dari bibir terjun (0, H+yc) ke titik tumbuk (L_drop, y1)
    x_drop = np.linspace(0, L_drop, 20)
    # Pendekatan kuadratik sederhana untuk visualisasi
    y_drop = (H_drop + yc) - ((H_drop + yc - y1) * (x_drop / L_drop)**2)
    ax.plot(x_drop, y_drop, 'b-', linewidth=1.5)
    
    # c. Loncatan Hidrolis (Hydraulic Jump)
    # Dari y1 (superkritis) naik ke y2 (subkritis)
    x_jump = np.linspace(L_drop, L_drop + L_kolam, 20)
    # Interpolasi linear/smooth step untuk kenaikan air
    y_jump = y1 + (y2 - y1) * ((x_jump - L_drop) / L_kolam)**0.5
    ax.plot(x_jump, y_jump, 'b-', linewidth=1.5, label='Muka Air')
    
    # d. Air Hilir (setelah ambang)
    ax.plot([L_drop + L_kolam, L_drop + L_kolam + 1], [y2, y2], 'b--')

    # Arsiran Air (Fill Between)
    # Gabungkan semua koordinat untuk fill
    x_fill = np.concatenate(([-2], x_drop, x_jump, [L_drop + L_kolam + 1]))
    y_water = np.concatenate(([H_drop + yc], y_drop, y_jump, [y2]))
    y_bottom = np.concatenate(([H_drop], np.zeros_like(x_drop), np.zeros_like(x_jump), [hs]))
    
    # Potong y_bottom agar panjangnya sama dengan x_fill (sedikit trick array)
    # Kita simplifikasi fill: Hulu, Jatuhan, Kolam
    ax.fill_between([-2, 0], [H_drop, H_drop], [H_drop+yc, H_drop+yc], color='cyan', alpha=0.3)
    ax.fill_between(x_drop, 0, y_drop, color='cyan', alpha=0.3)
    ax.fill_between(x_jump, 0, y_jump, color='cyan', alpha=0.3)

    # --- 3. ANNOTASI & DIMENSI ---
    # Label Dimensi
    ax.annotate(f"H = {H_drop}m", xy=(-0.5, H_drop/2), rotation=90)
    ax.annotate(f"Ld = {L_drop}m", xy=(L_drop/2, -0.5), ha='center', color='red')
    ax.annotate(f"Lj = {L_kolam}m", xy=(L_drop + L_kolam/2, -0.5), ha='center', color='green')
    
    # Label Kedalaman
    ax.text(L_drop, y1 + 0.1, f"y1={y1}", fontsize=8)
    ax.text(L_drop + L_kolam, y2 + 0.1, f"y2={y2}", fontsize=8)

    # Grid & Layout
    ax.set_title("Profil Memanjang Bangunan Terjun & Kolam Olak")
    ax.set_xlabel("Jarak (m)")
    ax.set_ylabel("Elevasi (m)")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.axis('equal') # Agar skala X dan Y proporsional (tidak gepeng)
    
    return fig
