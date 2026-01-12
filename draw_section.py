import matplotlib.pyplot as plt

def gambar_potongan(y1, y2, L, hs):
    fig, ax = plt.subplots(figsize=(10,4))

    ax.plot([0, L], [0, 0], lw=3)           # lantai
    ax.plot([0, L], [y2, y2], '--')         # muka air
    ax.plot([L, L], [0, hs], lw=3)          # end sill

    ax.text(L/2, y2+0.05, "y₂", ha='center')
    ax.text(-0.3, y1, "y₁", ha='center')

    ax.set_title("Potongan Kolam Olak USBR")
    ax.set_xlabel("Panjang (m)")
    ax.set_ylabel("Tinggi (m)")
    ax.grid(True)

    return fig
