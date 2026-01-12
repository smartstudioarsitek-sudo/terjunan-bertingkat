import matplotlib.pyplot as plt
import numpy as np

def gambar_denah_bertingkat(n_terjun, B, L_drop, L_kolam, t_dinding=0.30):
    """
    Fungsi menggambar Denah (Tampak Atas) Bangunan Terjun
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Warna & Style
    color_wall = 'gray'
    color_water = 'cyan'
    
    # Koordinat Awal (Mulai dari Hulu X=0)
    curr_x = 0.0
    half_B = B / 2.0
    
    # Garis As (Centerline)
    # Kita estimasi panjang total dulu untuk garis as
    total_len_est = 2 + (n_terjun * (L_drop + L_kolam + 0.5)) + 3
    ax.plot([-2, total_len_est], [0, 0], color='blue', linestyle='-.', linewidth=0.8, alpha=0.5, label='As Saluran')

    # --- 1. GAMBAR SALURAN PENGARAH HULU ---
    # Dinding Dalam
    ax.plot([-2, 0], [half_B, half_B], 'k-', linewidth=2)
    ax.plot([-2, 0], [-half_B, -half_B], 'k-', linewidth=2)
    # Dinding Luar
    ax.plot([-2, 0], [half_B + t_dinding, half_B + t_dinding], 'k-', linewidth=2)
    ax.plot([-2, 0], [-half_B - t_dinding, -half_B - t_dinding], 'k-', linewidth=2)
    # Arsiran Dinding
    ax.fill_between([-2, 0], half_B, half_B + t_dinding, color=color_wall, alpha=0.5)
    ax.fill_between([-2, 0], -half_B - t_dinding, -half_B, color=color_wall, alpha=0.5)

    # --- 2. LOOP SETIAP TRAP ---
    for i in range(n_terjun):
        # Titik-titik penting dalam satu trap
        x_bibir = curr_x
        x_tumbuk = x_bibir + L_drop
        x_akhir = x_tumbuk + L_kolam
        
        # Panjang total trap ini
        x_range = [x_bibir, x_akhir]
        
        # Gambar Dinding Menerus
        ax.plot(x_range, [half_B, half_B], 'k-', linewidth=2)
        ax.plot(x_range, [-half_B, -half_B], 'k-', linewidth=2)
        ax.plot(x_range, [half_B + t_dinding, half_B + t_dinding], 'k-', linewidth=2)
        ax.plot(x_range, [-half_B - t_dinding, -half_B - t_dinding], 'k-', linewidth=2)
        
        # Arsiran Dinding
        ax.fill_between(x_range, half_B, half_B + t_dinding, color=color_wall, alpha=0.5)
        ax.fill_between(x_range, -half_B - t_dinding, -half_B, color=color_wall, alpha=0.5)
        
        # GARIS SITUASI:
        # A. Garis Bibir Terjun (Garis Tegas Melintang)
        ax.plot([x_bibir, x_bibir], [-half_B, half_B], 'k-', linewidth=1.5)
        
        # B. Garis Ambang Akhir / End Sill (Garis Ganda)
        ax.plot([x_akhir, x_akhir], [-half_B, half_B], 'k-', linewidth=1.5)
        ax.plot([x_akhir+0.1, x_akhir+0.1], [-half_B, half_B], 'k-', linewidth=1)
        
        # C. Teks Keterangan
        ax.text(x_bibir + L_drop/2, 0, f"Jatuhan\n{i+1}", ha='center', va='center', fontsize=8, color='blue')
        ax.text(x_tumbuk + L_kolam/2, 0, f"Kolam Olak\n{i+1}", ha='center', va='center', fontsize=8, color='green')
        
        # D. Panah Arah Aliran (Simbolis)
        ax.arrow(x_bibir, 0, L_drop * 0.8, 0, head_width=0.1, head_length=0.2, fc='cyan', ec='cyan', alpha=0.6)

        # Update X untuk trap berikutnya (tambah sedikit jarak transisi/ambang)
        curr_x = x_akhir + 0.5 
        
        # Gambar dinding transisi antar trap
        x_trans = [x_akhir, curr_x]
        ax.plot(x_trans, [half_B, half_B], 'k-', linewidth=2)
        ax.plot(x_trans, [-half_B, -half_B], 'k-', linewidth=2)
        ax.plot(x_trans, [half_B + t_dinding, half_B + t_dinding], 'k-', linewidth=2)
        ax.plot(x_trans, [-half_B - t_dinding, -half_B - t_dinding], 'k-', linewidth=2)
        ax.fill_between(x_trans, half_B, half_B + t_dinding, color=color_wall, alpha=0.5)
        ax.fill_between(x_trans, -half_B - t_dinding, -half_B, color=color_wall, alpha=0.5)

    # --- 3. SALURAN HILIR ---
    x_hilir_end = curr_x + 3
    x_range_hilir = [curr_x, x_hilir_end]
    
    ax.plot(x_range_hilir, [half_B, half_B], 'k-', linewidth=2)
    ax.plot(x_range_hilir, [-half_B, -half_B], 'k-', linewidth=2)
    ax.plot(x_range_hilir, [half_B + t_dinding, half_B + t_dinding], 'k-', linewidth=2)
    ax.plot(x_range_hilir, [-half_B - t_dinding, -half_B - t_dinding], 'k-', linewidth=2)
    ax.fill_between(x_range_hilir, half_B, half_B + t_dinding, color=color_wall, alpha=0.5)
    ax.fill_between(x_range_hilir, -half_B - t_dinding, -half_B, color=color_wall, alpha=0.5)
    
    # Label Dimensi Lebar
    ax.annotate(f"B = {B}m", xy=(x_hilir_end-1, 0), xytext=(x_hilir_end-1, half_B + 0.5), 
                arrowprops=dict(arrowstyle='->'), ha='center')

    # Formatting Plot
    ax.set_title("Denah Situasi Bangunan Terjun (Tampak Atas)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Jarak Memanjang (m)")
    ax.set_ylabel("Lebar Saluran (m)")
    
    # PENTING: Equal aspect ratio agar bentuknya tidak gepeng
    ax.axis('equal') 
    ax.grid(True, linestyle='--', alpha=0.5)
    
    return fig