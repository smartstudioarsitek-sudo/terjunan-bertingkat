import pandas as pd
import io
import ezdxf
from ezdxf.enums import TextEntityAlignment

def generate_excel(input_data, hasil_hidrolis, hasil_stabil):
    """
    Membuat file Excel dengan multiple sheets
    """
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    # Sheet 1: Input
    df_input = pd.DataFrame(list(input_data.items()), columns=["Parameter Input", "Nilai"])
    df_input.to_excel(writer, sheet_name='Input Data', index=False)

    # Sheet 2: Hidrolis
    df_hidro = pd.DataFrame(list(hasil_hidrolis.items()), columns=["Parameter Hidrolis", "Nilai"])
    df_hidro.to_excel(writer, sheet_name='Analisa Hidrolis', index=False)

    # Sheet 3: Stabilitas
    df_stabil = pd.DataFrame(list(hasil_stabil.items()), columns=["Cek Stabilitas", "Nilai"])
    df_stabil.to_excel(writer, sheet_name='Stabilitas', index=False)

    writer.close()
    return output.getvalue()

def generate_dxf_potongan(n_terjun, H_total, H_drop, L_drop, L_kolam_inter, L_kolam_final, y1, y2, hs, yc):
    """
    Membuat DXF Potongan Memanjang (Long Section)
    """
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    doc.layers.add("STRUKTUR", color=7) 
    doc.layers.add("MUKA_AIR", color=5) 

    curr_x = 0.0
    curr_y_floor = float(H_total)

    # HULU
    msp.add_lwpolyline([(-2, curr_y_floor), (curr_x, curr_y_floor)], dxfattribs={'layer': 'STRUKTUR'})
    msp.add_lwpolyline([(-2, curr_y_floor+yc), (curr_x, curr_y_floor+yc)], dxfattribs={'layer': 'MUKA_AIR'})

    # LOOP TRAP
    for i in range(n_terjun):
        # Cek Mode Hemat (Lantai Tengah vs Akhir)
        is_final = (i == n_terjun - 1)
        L_kolam_curr = L_kolam_final if is_final else L_kolam_inter

        x_bibir = curr_x
        y_bibir = curr_y_floor
        y_lantai_bawah = y_bibir - H_drop
        x_tumbuk = x_bibir + L_drop
        x_akhir_kolam = x_tumbuk + L_kolam_curr
        y_ambang_atas = y_lantai_bawah + (hs if is_final else 0)

        # Gambar Struktur
        points_beton = [(x_bibir, y_bibir), (x_bibir, y_lantai_bawah), (x_akhir_kolam, y_lantai_bawah), (x_akhir_kolam, y_ambang_atas)]
        msp.add_lwpolyline(points_beton, dxfattribs={'layer': 'STRUKTUR'})

        # Gambar Air
        target_y = y2 if is_final else y1
        points_air = [(x_bibir, y_bibir + yc), (x_tumbuk, y_lantai_bawah + y1), (x_akhir_kolam, y_lantai_bawah + target_y)]
        msp.add_lwpolyline(points_air, dxfattribs={'layer': 'MUKA_AIR'})
        
        # Label
        label = f"Trap {i+1}"
        msp.add_text(label, height=0.2, dxfattribs={'layer': 'STRUKTUR'}).set_placement(
            ((x_bibir + x_akhir_kolam)/2, y_lantai_bawah - 0.5), align=TextEntityAlignment.CENTER)

        # Update Next
        curr_x = x_akhir_kolam + 0.5
        curr_y_floor = y_ambang_atas
        msp.add_line((x_akhir_kolam, y_ambang_atas), (curr_x, curr_y_floor), dxfattribs={'layer': 'STRUKTUR'})

    # HILIR
    msp.add_lwpolyline([(curr_x, curr_y_floor), (curr_x + 5, curr_y_floor)], dxfattribs={'layer': 'STRUKTUR'})
    msp.add_lwpolyline([(curr_x, curr_y_floor+yc), (curr_x + 5, curr_y_floor+yc)], dxfattribs={'layer': 'MUKA_AIR'})

    output = io.StringIO()
    doc.write(output)
    return output.getvalue().encode('utf-8')

def generate_dxf_denah(n_terjun, B, L_drop, L_kolam_inter, L_kolam_final, t_dinding=0.30):
    """
    Membuat DXF Denah Situasi (Plan View) - BARU!
    """
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Layers
    doc.layers.add("DINDING", color=7)      # Putih/Hitam
    doc.layers.add("AS_SALURAN", color=1)   # Merah
    doc.layers.add("TEKS", color=3)         # Hijau

    half_B = B / 2.0
    curr_x = 0.0

    # 1. HULU
    # Dinding Kiri & Kanan
    msp.add_lwpolyline([(-2, half_B), (0, half_B)], dxfattribs={'layer': 'DINDING'})
    msp.add_lwpolyline([(-2, -half_B), (0, -half_B)], dxfattribs={'layer': 'DINDING'})
    # Dinding Luar
    msp.add_lwpolyline([(-2, half_B + t_dinding), (0, half_B + t_dinding)], dxfattribs={'layer': 'DINDING'})
    msp.add_lwpolyline([(-2, -half_B - t_dinding), (0, -half_B - t_dinding)], dxfattribs={'layer': 'DINDING'})
    # Garis As
    msp.add_line((-2, 0), (0, 0), dxfattribs={'layer': 'AS_SALURAN', 'linetype': 'DASHDOT'})

    # 2. LOOP TRAP
    for i in range(n_terjun):
        is_final = (i == n_terjun - 1)
        L_kolam_curr = L_kolam_final if is_final else L_kolam_inter

        x_bibir = curr_x
        x_tumbuk = x_bibir + L_drop
        x_akhir = x_tumbuk + L_kolam_curr
        
        # Gambar Dinding Sepanjang Trap
        x_points = [x_bibir, x_akhir]
        msp.add_lwpolyline([(x_bibir, half_B), (x_akhir, half_B)], dxfattribs={'layer': 'DINDING'})
        msp.add_lwpolyline([(x_bibir, -half_B), (x_akhir, -half_B)], dxfattribs={'layer': 'DINDING'})
        msp.add_lwpolyline([(x_bibir, half_B + t_dinding), (x_akhir, half_B + t_dinding)], dxfattribs={'layer': 'DINDING'})
        msp.add_lwpolyline([(x_bibir, -half_B - t_dinding), (x_akhir, -half_B - t_dinding)], dxfattribs={'layer': 'DINDING'})
        
        # Garis Bibir & Ambang (Garis Melintang)
        msp.add_line((x_bibir, -half_B), (x_bibir, half_B), dxfattribs={'layer': 'DINDING'}) # Bibir
        msp.add_line((x_akhir, -half_B), (x_akhir, half_B), dxfattribs={'layer': 'DINDING'}) # Ambang

        # Garis As
        msp.add_line((x_bibir, 0), (x_akhir, 0), dxfattribs={'layer': 'AS_SALURAN'})

        # Teks
        msp.add_text(f"Trap {i+1}", height=0.25, dxfattribs={'layer': 'TEKS'}).set_placement(
            (x_bibir + L_drop/2, 0), align=TextEntityAlignment.CENTER)
        
        label_lantai = "Kolam" if is_final else "Lantai"
        msp.add_text(label_lantai, height=0.2, dxfattribs={'layer': 'TEKS'}).set_placement(
            (x_tumbuk + L_kolam_curr/2, 0), align=TextEntityAlignment.CENTER)

        # Transisi ke trap berikutnya
        curr_x = x_akhir + 0.5
        # Dinding Transisi
        msp.add_lwpolyline([(x_akhir, half_B), (curr_x, half_B)], dxfattribs={'layer': 'DINDING'})
        msp.add_lwpolyline([(x_akhir, -half_B), (curr_x, -half_B)], dxfattribs={'layer': 'DINDING'})
        msp.add_lwpolyline([(x_akhir, half_B+t_dinding), (curr_x, half_B+t_dinding)], dxfattribs={'layer': 'DINDING'})
        msp.add_lwpolyline([(x_akhir, -half_B-t_dinding), (curr_x, -half_B-t_dinding)], dxfattribs={'layer': 'DINDING'})
        msp.add_line((x_akhir, 0), (curr_x, 0), dxfattribs={'layer': 'AS_SALURAN'})

    # 3. HILIR AKHIR
    x_end = curr_x + 3
    msp.add_lwpolyline([(curr_x, half_B), (x_end, half_B)], dxfattribs={'layer': 'DINDING'})
    msp.add_lwpolyline([(curr_x, -half_B), (x_end, -half_B)], dxfattribs={'layer': 'DINDING'})
    msp.add_lwpolyline([(curr_x, half_B+t_dinding), (x_end, half_B+t_dinding)], dxfattribs={'layer': 'DINDING'})
    msp.add_lwpolyline([(curr_x, -half_B-t_dinding), (x_end, -half_B-t_dinding)], dxfattribs={'layer': 'DINDING'})
    msp.add_line((curr_x, 0), (x_end, 0), dxfattribs={'layer': 'AS_SALURAN'})

    output = io.StringIO()
    doc.write(output)
    return output.getvalue().encode('utf-8')
