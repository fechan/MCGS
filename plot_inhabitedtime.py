import nbt

import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()

region = nbt.load_region(filedialog.askopenfile(mode='rb'))
plot_name = input("Name of inhabitedtime plot: (inhabitedtime_plot.asc is default) ")
if not plot_name:
    plot_name = "inhabitedtime_plot.asc"
mirror = input("Mirror chunks vertically? (North is down, but coordinates match Minecraft) (y/n, y is default): ").upper() != "N"

xllcorner = 0
yllcorner = 0
asc_data = ""
z_order = reversed(range(32)) if mirror else range(32)
for chunkz in z_order:
    for chunkx in range(32):
        chunk = region.load_chunk(chunkx, chunkz)
        if chunkx == 0 and chunkz == 0:
            xllcorner = chunk[1]['Level']['xPos']*16
            yllcorner = (1 if mirror else -1)*chunk[1]['Level']['zPos']*16 - (0 if mirror else (32*16))
        try:
            inhabitedtime = chunk[1]['Level']['InhabitedTime']
            asc_data += str(inhabitedtime)
        except:
            asc_data += "-1"
        asc_data += " " 

asc_header = f"""ncols 32
nrows 32
xllcorner {xllcorner}
yllcorner {yllcorner}
cellsize 16
nodata_value -1
"""
with open(plot_name, 'w') as asc_file:
        asc_file.write(asc_header + asc_data)
        asc_file.close()