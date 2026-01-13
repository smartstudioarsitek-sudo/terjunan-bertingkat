import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def gambar_3d_terjun(n_terjun, B, H_total, H_drop, L_drop, L_kolam_inter, L_kolam_final, mode_hemat):
    """
    Membuat Visualisasi 3D Isometrik Sederhana menggunakan Matplotlib
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    curr_x = 0
    curr_z = H_total
    half_B = B / 2
    
    # Warna
    color_beton = 'gray'
    color_air = 'cyan'
    alpha_beton = 0.6
    alpha_air = 0.4

    def plot_box(x_range, y_range, z_range, color, alpha):
        """Helper menggambar balok (lantai/air)"""
        xx, yy = np.meshgrid(x_range, y_range)
        # Atas
        ax.plot_surface(xx, yy, np.full_like(xx, z_range[1]), color=color, alpha=alpha, shade=True)
        # Bawah (opsional, tertutup)
        # Samping dinding (Visualisasi dinding saluran)
        # Kiri
        ax.plot_surface(np.meshgrid(x_range, [y_range[0], y_range[0]])[0], 
                        np.meshgrid(x_range, [y_range[0], y_range[0]])[1], 
                        np.array([[z_range[0], z_range[0]], [z_range[1], z_range[1]]]), color=color, alpha=alpha)
        # Kanan
        ax.plot_surface(np.meshgrid(x_range, [y_range[1], y_range[1]])[0], 
                        np.meshgrid(x_range, [y_range[1], y_range[1]])[1], 
                        np.array([[z_range[0], z_range[0]], [z_range[1], z_range[1]]]), color=color, alpha=alpha)

    # 1. HULU
    plot_box([-2, 0], [-half_B, half_B], [curr_z-0.5, curr_z], color_beton, alpha_beton) # Lantai
    plot_box([-2, 0], [-half_B, half_B], [curr_z, curr_z+0.5], color_air, alpha_air)    # Air
    
    # 2. LOOP TRAP
    for i in range(n_terjun):
        is_final = (i == n_terjun - 1)
        L_kolam_curr = L_kolam_final if is_final else L_kolam_inter
        
        # Koordinat Trap
        x_bibir = curr_x
        z_bibir = curr_z
        z_lantai_bawah = z_bibir - H_drop
        x_akhir = x_bibir + L_drop + L_kolam_curr
        
        # A. Dinding Terjun (Vertical Drop)
        # Polygon vertikal menutup drop
        y_verts = np.array([-half_B, half_B, half_B, -half_B])
        z_verts = np.array([z_bibir, z_bibir, z_lantai_bawah, z_lantai_bawah])
        x_verts = np.array([x_bibir, x_bibir, x_bibir, x_bibir])
        verts = [list(zip(x_verts, y_verts, z_verts))]
        ax.add_collection3d(Poly3DCollection(verts, facecolors=color_beton, alpha=alpha_beton, edgecolors='k'))
        
        # B. Lantai Datar Trap
        plot_box([x_bibir, x_akhir], [-half_B, half_B], [z_lantai_bawah-0.5, z_lantai_bawah], color_beton, alpha_beton)
        
        # C. Air di Trap (Sederhana: Prisma)
        # Air turun miring dari bibir ke kolam
        x_air = [x_bibir, x_bibir + L_drop, x_akhir]
        z_air_surface = [z_bibir + 0.3, z_lantai_bawah + 0.5, z_lantai_bawah + 0.5] # Asumsi tinggi air rata2
        
        # Gambar air manual pakai plot_trisurf atau lines agar ringan
        # Sisi Kiri Air
        ax.plot(x_air, [-half_B]*3, z_air_surface, color='blue', linewidth=1)
        # Sisi Kanan Air
        ax.plot(x_air, [half_B]*3, z_air_surface, color='blue', linewidth=1)
        # Permukaan (Wireframe sederhana)
        for k in range(len(x_air)-1):
            plot_box([x_air[k], x_air[k+1]], [-half_B, half_B], 
                     [z_lantai_bawah, (z_air_surface[k]+z_air_surface[k+1])/2], color_air, 0.2)

        # Update Next
        curr_x = x_akhir
        curr_z = z_lantai_bawah
        
        # Label Trap
        ax.text(x_bibir, -half_B - 1, z_bibir, f"Trap {i+1}", fontsize=8)

    # 3. HILIR FINAL
    plot_box([curr_x, curr_x+3], [-half_B, half_B], [curr_z-0.5, curr_z], color_beton, alpha_beton)
    plot_box([curr_x, curr_x+3], [-half_B, half_B], [curr_z, curr_z+0.5], color_air, alpha_air)

    # Setting Tampilan
    ax.set_xlabel('Panjang (m)')
    ax.set_ylabel('Lebar (m)')
    ax.set_zlabel('Elevasi (m)')
    ax.set_title("Visualisasi 3D Isometrik Bangunan Terjun")
    
    # Skala axis agar proporsional
    # Matplotlib 3D aspect ratio agak tricky, kita set box aspect
    max_range = np.array([curr_x+3, B, H_total]).max()
    ax.set_box_aspect((curr_x/max_range*2, B/max_range*2, H_total/max_range*2))
    
    ax.view_init(elev=30, azim=-45) # Sudut pandang isometrik standar
    
    return fig