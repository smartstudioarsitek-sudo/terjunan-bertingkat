import matplotlib.pyplot as plt
import numpy as np

def gambar_potongan_bertingkat(n_terjun, H_total, H_drop, L_drop, L_kolam_inter, L_kolam_final, y1, y2, hs, yc):
    """
    Update: Menerima 10 Argumen (termasuk L_kolam_inter & L_kolam_final)
    agar bisa menggambar kolam tengah yang pendek dan kolam akhir yang panjang.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    curr_x = 0.0
    curr_y_floor = float(H_total)

    # --- 1. GAMBAR HULU ---
    ax.plot([-2, curr_x], [curr_y_floor, curr_y_floor], 'k-', linewidth=3)
    ax.plot([-2, curr_x], [curr_y_floor + yc, curr_y_floor + yc], 'b-', linewidth=1)
    ax.fill_between([-2, curr_x], [curr_y_floor, curr_y_floor], [curr_y_floor + yc, curr_y_floor + yc], color='cyan', alpha=0.3)
    ax.annotate(f"H Total = {H_total}m", xy=(-2.2, H_total/2), rotation=90, va='center')

    # --- 2. LOOP SETIAP TRAP ---
    for i in range(n_terjun):
        # LOGIKA KUNCI: Pilih panjang kolam berdasarkan posisi trap
        if i == n_terjun - 1:
            # Jika trap terakhir (paling bawah) -> Pakai Kolam Panjang (Final)
            L_kolam_curr = L_kolam_final
            is_final = True
        else:
            # Jika trap tengah -> Pakai Kolam Pendek (Intermediate)
            L_kolam_curr = L_kolam_inter
            is_final = False

        # Koordinat
        x_bibir = curr_x
        y_bibir = curr_y_floor
        y_lantai_bawah = y_bibir - H_drop
        x_tumbuk = x_bibir + L_drop
        x_akhir_kolam = x_tumbuk + L_kolam_curr
        
        # Ambang (End Sill) biasanya hanya signifikan di kolam akhir
        y_ambang_atas = y_lantai_bawah + (hs if is_final else 0)

        # Gambar Struktur Beton
        ax.plot([x_bibir, x_bibir], [y_bibir, y_lantai_bawah], 'k-', linewidth=3) # Dinding Tegak
        ax.plot([x_bibir, x_akhir_kolam], [y_lantai_bawah, y_lantai_bawah], 'k-', linewidth=3) # Lantai Datar
        ax.plot([x_akhir_kolam, x_akhir_kolam], [y_lantai_bawah, y_ambang_atas], 'k-', linewidth=3) # Ambang

        # Gambar Air Jatuh (Parabola)
        x_traj = np.linspace(x_bibir, x_tumbuk, 20)
        y_traj = (y_bibir + yc) - ((H_drop + yc - y1) * ((x_traj - x_bibir) / L_drop)**2)
        ax.plot(x_traj, y_traj, 'b-', linewidth=1.5)
        ax.fill_between(x_traj, y_lantai_bawah, y_traj, where=(x_traj>=x_bibir), color='cyan', alpha=0.3, interpolate=True)

        # Gambar Air di Lantai (Loncatan)
        x_jump = np.linspace(x_tumbuk, x_akhir_kolam, 20)
        target_y = y2 if is_final else y1 # Jika pendek, air dianggap masih deras
        y_jump_rel = y1 + (target_y - y1) * ((x_jump - x_tumbuk) / L_kolam_curr)**0.5
        y_jump = y_lantai_bawah + y_jump_rel
        
        ax.plot(x_jump, y_jump, 'b-', linewidth=1.5)
        ax.fill_between(x_jump, y_lantai_bawah, y_jump, color='cyan', alpha=0.3)

        # Teks Keterangan
        label_trap = f"Trap {i+1}"
        if not is_final: label_trap += " (Pendek)"
        ax.text((x_bibir + x_akhir_kolam)/2, y_lantai_bawah - 0.5, label_trap, ha='center', fontsize=9)
        
        # Dimensi Panjang
        ax.annotate(f"L={round(L_drop+L_kolam_curr,1)}m", xy=((x_bibir+x_akhir_kolam)/2, y_lantai_bawah-1), ha='center', fontsize=8, color='red')

        # Update untuk loop berikutnya
        curr_x = x_akhir_kolam + 0.5 
        curr_y_floor = y_ambang_atas
        
        # Lantai transisi kecil antar trap
        ax.plot([x_akhir_kolam, curr_x], [curr_y_floor, curr_y_floor], 'k-', linewidth=3)

    # --- 3. GAMBAR HILIR AKHIR ---
    ax.plot([curr_x, curr_x + 3], [curr_y_floor, curr_y_floor], 'k-', linewidth=3)
    ax.plot([curr_x, curr_x + 3], [curr_y_floor + yc, curr_y_floor + yc], 'b--', linewidth=1)
    ax.fill_between([curr_x, curr_x + 3], [curr_y_floor, curr_y_floor], [curr_y_floor + yc, curr_y_floor + yc], color='cyan', alpha=0.3)

    ax.set_title("Profil Memanjang (Mode Hemat: Kolam Pendek di Tengah)", fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.axis('equal') 
    plt.tight_layout()
    
    return fig
