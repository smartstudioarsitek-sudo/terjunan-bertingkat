import matplotlib.pyplot as plt
import numpy as np

def gambar_potongan_bertingkat(n_terjun, H_total, H_drop, L_drop, L_kolam, y1, y2, hs, yc):
    """
    Fungsi untuk visualisasi potongan memanjang bangunan terjun BERTINGKAT.
    Menggambar n_terjun trap secara berurutan.
    """
    fig, ax = plt.subplots(figsize=(14, 8)) # Ukuran gambar diperbesar sedikit

    # --- INISIALISASI KOORDINAT AWAL ---
    # Kita mulai dari hulu paling atas (x=0) dengan elevasi dasar H_total
    curr_x = 0.0
    curr_y_floor = float(H_total)

    # --- GAMBAR SALURAN HULU (SEBELUM TERJUN PERTAMA) ---
    # Gambar sedikit saluran pengarah sepanjang 2m di hulu
    ax.plot([-2, curr_x], [curr_y_floor, curr_y_floor], 'k-', linewidth=3) # Lantai
    ax.plot([-2, curr_x], [curr_y_floor + yc, curr_y_floor + yc], 'b-', linewidth=1) # Muka air
    ax.fill_between([-2, curr_x], [curr_y_floor, curr_y_floor], [curr_y_floor + yc, curr_y_floor + yc], color='cyan', alpha=0.3)
    
    # Label H_total di kiri
    ax.annotate(f"H Total = {H_total}m", xy=(-2.2, H_total/2), rotation=90, va='center')

    # --- LOOPING MENGGAMBAR SETIAP TRAP TERJUN ---
    for i in range(n_terjun):
        # -- 1. Definisi Titik Penting pada Trap Ini --
        x_bibir = curr_x
        y_bibir = curr_y_floor
        y_lantai_bawah = y_bibir - H_drop
        x_tumbuk = x_bibir + L_drop
        x_akhir_kolam = x_tumbuk + L_kolam
        y_ambang_atas = y_lantai_bawah + hs

        # -- 2. Gambar Struktur Beton (Garis Hitam Tebal) --
        # Dinding vertikal terjun
        ax.plot([x_bibir, x_bibir], [y_bibir, y_lantai_bawah], 'k-', linewidth=3)
        # Lantai kolam olak datar
        ax.plot([x_bibir, x_akhir_kolam], [y_lantai_bawah, y_lantai_bawah], 'k-', linewidth=3)
        # Ambang akhir (End Sill) vertikal
        ax.plot([x_akhir_kolam, x_akhir_kolam], [y_lantai_bawah, y_ambang_atas], 'k-', linewidth=3)

        # -- 3. Gambar Profil Muka Air (Garis Biru & Arsiran) --
        
        # a. Lintasan Jatuhan Air (Trajectory) - Parabola
        x_traj = np.linspace(x_bibir, x_tumbuk, 20)
        # Rumus parabola relatif terhadap posisi bibir terjun
        # y_relatif = H_awal - (Delta_H * (x_relatif / L_total)^2)
        y_traj = (y_bibir + yc) - ((H_drop + yc - y1) * ((x_traj - x_bibir) / L_drop)**2)
        
        ax.plot(x_traj, y_traj, 'b-', linewidth=1.5)
        # Arsiran jatuhan (harus hati-hati dengan batas bawahnya)
        # Kita arsir dari y_traj sampai level lantai bawah (y_lantai_bawah)
        # Tapi hanya untuk x > x_bibir agar tidak bocor ke belakang dinding
        ax.fill_between(x_traj, y_lantai_bawah, y_traj, where=(x_traj>=x_bibir), color='cyan', alpha=0.3, interpolate=True)

        # b. Loncatan Hidrolis (Hydraulic Jump) - Kurva Naik
        x_jump = np.linspace(x_tumbuk, x_akhir_kolam, 20)
        # Interpolasi smooth dari y1 ke y2 relatif terhadap lantai bawah
        y_jump_rel = y1 + (y2 - y1) * ((x_jump - x_tumbuk) / L_kolam)**0.5
        y_jump = y_lantai_bawah + y_jump_rel
        
        ax.plot(x_jump, y_jump, 'b-', linewidth=1.5)
        # Arsiran kolam olak
        ax.fill_between(x_jump, y_lantai_bawah, y_jump, color='cyan', alpha=0.3)
        
        # c. Air di atas Ambang (Transisi ke trap berikutnya)
        # Asumsikan air kembali tenang setinggi yc di atas ambang untuk trap berikutnya
        ax.plot([x_akhir_kolam, x_akhir_kolam + 0.5], [y_ambang_atas + yc, y_ambang_atas + yc], 'b-', linewidth=1)
        ax.fill_between([x_akhir_kolam, x_akhir_kolam + 0.5], [y_ambang_atas, y_ambang_atas], [y_ambang_atas + yc, y_ambang_atas + yc], color='cyan', alpha=0.3)

        # -- 4. Annotasi Per Trap --
        # Label nomor terjun di tengah kolam
        ax.text((x_bibir + x_akhir_kolam)/2, y_lantai_bawah - 0.5, f"Terjun Ke-{i+1}", ha='center', fontweight='bold', fontsize=9)
        # Dimensi H trap (hanya di trap pertama agar tidak ramai)
        if i == 0:
             ax.annotate(f"H={H_drop}m", xy=(x_bibir-0.2, (y_bibir+y_lantai_bawah)/2), rotation=90, va='center', fontsize=8)

        # -- 5. UPDATE KOORDINAT UNTUK TRAP BERIKUTNYA --
        # Titik mulai (x) berikutnya adalah akhir dari kolam ini (+ sedikit jarak transisi)
        curr_x = x_akhir_kolam + 0.5 
        # Elevasi lantai (y) berikutnya adalah setinggi ambang (end sill) trap ini
        curr_y_floor = y_ambang_atas
        # Gambar sedikit lantai transisi antar trap
        ax.plot([x_akhir_kolam, curr_x], [curr_y_floor, curr_y_floor], 'k-', linewidth=3)


    # --- GAMBAR SALURAN HILIR AKHIR ---
    # Setelah loop selesai, gambar saluran pembuang di hilir paling akhir
    ax.plot([curr_x, curr_x + 3], [curr_y_floor, curr_y_floor], 'k-', linewidth=3, label='Struktur Beton')
    # Asumsi air hilir kembali normal (subkritis y2 atau yc, kita pakai y2 untuk visualisasi aman)
    # Tapi karena di atas ambang kita pakai yc, konsisten pakai yc saja sebagai depth aliran berikutnya.
    final_depth = yc 
    ax.plot([curr_x, curr_x + 3], [curr_y_floor + final_depth, curr_y_floor + final_depth], 'b--', linewidth=1, label='Muka Air')
    ax.fill_between([curr_x, curr_x + 3], [curr_y_floor, curr_y_floor], [curr_y_floor + final_depth, curr_y_floor + final_depth], color='cyan', alpha=0.3)


    # --- FORMATTING PLOT ---
    ax.set_title("Profil Memanjang Bangunan Terjun Bertingkat", fontsize=14, fontweight='bold')
    ax.set_xlabel("Jarak Horizontal (m)", fontsize=12)
    ax.set_ylabel("Elevasi Relatif (m)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right')
    
    # SANGAT PENTING: Agar skala visual sumbu X dan Y sama (tidak gepeng)
    ax.axis('equal') 
    
    # Tambahkan sedikit margin agar tidak terlalu mepet pinggir
    plt.tight_layout()
    
    return fig
