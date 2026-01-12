import pandas as pd
import io
import ezdxf
from ezdxf.enums import TextEntityAlignment

def generate_excel(input_data, hasil_hidrolis, hasil_stabil):
    """
    Membuat file Excel dengan multiple sheets: Input, Hidrolis, Stabilitas
    """
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    # --- SHEET 1: INPUT DATA ---
    df_input = pd.DataFrame(list(input_data.items()), columns=["Parameter Input", "Nilai"])
    df_input.to_excel(writer, sheet_name='Input Data', index=False)

    # --- SHEET 2: ANALISA HIDROLIS ---
    df_hidro = pd.DataFrame(list(hasil_hidrolis.items()), columns=["Parameter Hidrolis", "Nilai"])
    df_hidro.to_excel(writer, sheet_name='Analisa Hidrolis', index=False)

    # --- SHEET 3: STABILITAS STRUKTUR ---
    df_stabil = pd.DataFrame(list(hasil_stabil.items()), columns=["Cek Stabilitas", "Nilai"])
    df_stabil.to_excel(writer, sheet_name='Stabilitas', index=False)

    writer.close()
    return output.getvalue()

def generate_dxf(n_terjun, H_total, H_drop, L_drop, L_kolam, y1, y2, hs, yc):
    """
    Membuat file DXF (CAD) sederhana untuk potongan memanjang
    """
    # Setup Drawing
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Setup Layers
    doc.layers.add("STRUKTUR", color=7) # Putih/Hitam
    doc.layers.add("MUKA_AIR", color=5) # Biru

    # Koordinat Awal
    curr_x = 0.0
    curr_y_floor = float(H_total)

    # --- 1. GAMBAR HULU ---
    msp.add_lwpolyline([(-2, curr_y_floor), (curr_x, curr_y_floor)], dxfattribs={'layer': 'STRUKTUR'})
    msp.add_lwpolyline([(-2, curr_y_floor+yc), (curr_x, curr_y_floor+yc)], dxfattribs={'layer': 'MUKA_AIR'})

    # --- 2. LOOP TRAP TERJUN ---
    for i in range(n_terjun):
        x_bibir = curr_x
        y_bibir = curr_y_floor
        y_lantai_bawah = y_bibir - H_drop
        x_tumbuk = x_bibir + L_drop
        x_akhir_kolam = x_tumbuk + L_kolam
        y_ambang_atas = y_lantai_bawah + hs

        # Gambar Beton (Struktur)
        points_beton = [
            (x_bibir, y_bibir),
            (x_bibir, y_lantai_bawah),
            (x_akhir_kolam, y_lantai_bawah),
            (x_akhir_kolam, y_ambang_atas)
        ]
        msp.add_lwpolyline(points_beton, dxfattribs={'layer': 'STRUKTUR'})

        # Gambar Air (Sederhana - Garis Lurus antar titik kunci)
        points_air = [
            (x_bibir, y_bibir + yc),      # Atas bibir
            (x_tumbuk, y_lantai_bawah + y1), # Titik tumbuk
            (x_akhir_kolam, y_lantai_bawah + y2) # Akhir kolam
        ]
        msp.add_lwpolyline(points_air, dxfattribs={'layer': 'MUKA_AIR'})
        
        # Teks Label
        msp.add_text(f"Terjun {i+1}", height=0.2, dxfattribs={'layer': 'STRUKTUR'}).set_placement(
            ((x_bibir + x_akhir_kolam)/2, y_lantai_bawah - 0.5),
            align=TextEntityAlignment.CENTER
        )

        # Update untuk trap berikutnya
        curr_x = x_akhir_kolam + 0.5
        curr_y_floor = y_ambang_atas
        
        # Lantai transisi
        msp.add_line((x_akhir_kolam, y_ambang_atas), (curr_x, curr_y_floor), dxfattribs={'layer': 'STRUKTUR'})

    # --- 3. GAMBAR HILIR ---
    msp.add_lwpolyline([(curr_x, curr_y_floor), (curr_x + 5, curr_y_floor)], dxfattribs={'layer': 'STRUKTUR'})
    msp.add_lwpolyline([(curr_x, curr_y_floor+yc), (curr_x + 5, curr_y_floor+yc)], dxfattribs={'layer': 'MUKA_AIR'})

    # Output ke Memory Buffer
    output = io.StringIO()
    doc.write(output)
    return output.getvalue().encode('utf-8')