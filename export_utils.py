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

def generate_dxf(n_terjun, H_total, H_drop, L_drop, L_kolam_inter, L_kolam_final, y1, y2, hs, yc):
    """
    Update: Support Mode Hemat (Kolam Intermediate vs Final)
    """
    # Setup Drawing
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Layers
    doc.layers.add("STRUKTUR", color=7) 
    doc.layers.add("MUKA_AIR", color=5) 

    curr_x = 0.0
    curr_y_floor = float(H_total)

    # --- 1. GAMBAR HULU ---
    msp.add_lwpolyline([(-2, curr_y_floor), (curr_x, curr_y_floor)], dxfattribs={'layer': 'STRUKTUR'})
    msp.add_lwpolyline([(-2, curr_y_floor+yc), (curr_x, curr_y_floor+yc)], dxfattribs={'layer': 'MUKA_AIR'})

    # --- 2. LOOP TRAP TERJUN ---
    for i in range(n_terjun):
        # Tentukan panjang kolam (Tengah vs Akhir)
        if i == n_terjun - 1:
            L_kolam_curr = L_kolam_final
            is_final = True
        else:
            L_kolam_curr = L_kolam_inter
            is_final = False

        x_bibir = curr_x
        y_bibir = curr_y_floor
        y_lantai_bawah = y_bibir - H_drop
        x_tumbuk = x_bibir + L_drop
        x_akhir_kolam = x_tumbuk + L_kolam_curr
        
        # Ambang (End Sill) hanya di trap akhir jika mode hemat
        # atau bisa diatur kecil. Di sini kita set sesuai logika potongan.
        y_ambang_atas = y_lantai_bawah + (hs if is_final else 0)

        # Gambar Beton
        points_beton = [
            (x_bibir, y_bibir),
            (x_bibir, y_lantai_bawah),
            (x_akhir_kolam, y_lantai_bawah),
            (x_akhir_kolam, y_ambang_atas)
        ]
        msp.add_lwpolyline(points_beton, dxfattribs={'layer': 'STRUKTUR'})

        # Gambar Air (Sederhana)
        target_y = y2 if is_final else y1 # Visualisasi air di lantai
        points_air = [
            (x_bibir, y_bibir + yc),      
            (x_tumbuk, y_lantai_bawah + y1), 
            (x_akhir_kolam, y_lantai_bawah + target_y) 
        ]
        msp.add_lwpolyline(points_air, dxfattribs={'layer': 'MUKA_AIR'})
        
        # Teks Label
        label = f"Trap {i+1}"
        msp.add_text(label, height=0.2, dxfattribs={'layer': 'STRUKTUR'}).set_placement(
            ((x_bibir + x_akhir_kolam)/2, y_lantai_bawah - 0.5),
            align=TextEntityAlignment.CENTER
        )

        # Update Next Coordinates
        curr_x = x_akhir_kolam + 0.5
        curr_y_floor = y_ambang_atas
        
        # Lantai transisi
        msp.add_line((x_akhir_kolam, y_ambang_atas), (curr_x, curr_y_floor), dxfattribs={'layer': 'STRUKTUR'})

    # --- 3. GAMBAR HILIR ---
    msp.add_lwpolyline([(curr_x, curr_y_floor), (curr_x + 5, curr_y_floor)], dxfattribs={'layer': 'STRUKTUR'})
    msp.add_lwpolyline([(curr_x, curr_y_floor+yc), (curr_x + 5, curr_y_floor+yc)], dxfattribs={'layer': 'MUKA_AIR'})

    output = io.StringIO()
    doc.write(output)
    return output.getvalue().encode('utf-8')
