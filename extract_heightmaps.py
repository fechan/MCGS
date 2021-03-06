"""
Loads a Minecraft .mca region file and outputs the heightmap of each chunk as an ESRI ASCII grid if
able. This script can merge them into one big GeoTIFF if gdal_merge.py is provided.

Requires nbt.py from Minecraft Overviewer renamed as overviewernbt.py to prevent name collision
(provided with MCGS)
Tested on .mca files compatible with Minecraft 1.15.2 and gdal_merge.py on Arch Linux.
"""

import overviewernbt
import os, sys, subprocess
from shutil import rmtree
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()

NETHER_BLOCKSTATES_DATAVERSION = 2529 #minimum DataVersion using the 1.16 BlockStates format (20w17a)

#Utility functions
def unstream(bits_per_value, word_size, data):
    """Converts data in an NBT long array into a list of ints"""
    bl = 0
    v = 0
    decoded = []
    for i in range(len(data)):
        for n in range(word_size):
            bit = (data[i] >> n) & 0x01
            v = (bit << bl) | v
            bl += 1
            if bl >= bits_per_value:
                decoded.append(v)
                v = 0
                bl = 0
    return decoded

def nether_unstream(bits_per_value, data):
    """Converts data in an NBT long array into a list of ints, used after the introduction of the
    new BlockStates format introduced in 20w17a and used in the 1.16 Nether Update (the one with 0s
    padding each LONG if the size (bits) isn't a multiple of 64).
    
    Adapted from Minecraft Overviewer's overviewer_core/world.py, but doesn't depend on numpy"""
    n = 256
    result = [0] * n
    shorts_per_long = 64 // bits_per_value
    mask = (1 << bits_per_value) - 1

    for i in range(shorts_per_long):
        j = (n + shorts_per_long - 1 - i) // shorts_per_long
        result[i::shorts_per_long] = [(b >> (bits_per_value * i)) & mask for b in data[:j]]
    
    return result

def mirror_vertical(row_size, data):
    """Vertically mirrors a 1D list representation of a chunk with a width of row_size"""
    data = [data[x:x+row_size] for x in range(0, len(data), row_size)]  #split into rows
    data = data[::-1]                                                   #reverse row order
    return [block for row in data for block in row]                     #flatten

#Set up and ask parameters
region = overviewernbt.load_region(filedialog.askopenfile(mode='rb'))
print("There are several heightmaps that can be exported:")
print("MOTION_BLOCKING")
print("MOTION_BLOCKING_NO_LEAVES")
print("OCEAN_FLOOR")
print("OCEAN_FLOOR_WG")
print("WORLD_SURFACE")
print("WORLD_SURFACE_WG")
heightmap_key = input("Which one do you want to export? (OCEAN_FLOOR is default) ")
if not heightmap_key:
    heightmap_key = "OCEAN_FLOOR"
folder_name = input("Name of folder to store chunk rasters in: (WILL BE OVERWRITTEN!) (chunk_rasters is default) ")
if not folder_name:
    folder_name = "chunk_rasters"
try:
    os.mkdir(folder_name)
except FileExistsError:
    print(f"Info: {folder_name} exists! Deleting.")
    rmtree(folder_name)
    os.mkdir(folder_name)
mirror = input("Mirror chunks vertically? (North is down, but coordinates match Minecraft) (y/n, y is default): ").upper() != "N" 
merge = input("Merge chunk rasters? (Uses gdal_merge.py) (y/n, y is default): ").upper() != "N"
if merge:
    gdal_path = input("Path to gdal_merge.py? (/usr/bin/gdal_merge.py is default) ")
    if not gdal_path:
        gdal_path = "/usr/bin/gdal_merge.py"
    merged_filename = input("Name of merged file? (chunks_merged.tif is default) ")
    if not merged_filename:
        merged_filename = "chunks_merged.tif"

#Start exporting rasters
print("Trying to export chunk rasters...")
for chunkx, chunkz in region.get_chunks():
    chunk = region.load_chunk(chunkx, chunkz)
    try:
        heightmap = chunk[1]['Level']['Heightmaps'][heightmap_key]
    except KeyError:
        print(f"No compatible heightmap found for chunk {chunkx}, {chunkz}")
        continue
    if chunk[1]['DataVersion'] < NETHER_BLOCKSTATES_DATAVERSION:
        decoded = unstream(9, 64, heightmap)
    else:
        decoded = nether_unstream(9, heightmap)
    if mirror:
        decoded = mirror_vertical(16, decoded)

    asc_data = f"""ncols 16
nrows 16
xllcorner {chunk[1]['Level']['xPos']*16}
yllcorner {(1 if mirror else -1)*chunk[1]['Level']['zPos']*16 - (0 if mirror else 16)}
cellsize 1
nodata_value 0
"""
    asc_data += ' '.join(str(v) for v in decoded)
    with open(os.path.join(folder_name, f"chunk_{chunk[1]['Level']['xPos']}_{chunk[1]['Level']['zPos']}.asc"), 'w') as asc_file:
        asc_file.write(asc_data)
        asc_file.close()
print("Chunk raster export complete!")

#Merge rasters if requested
if merge:
    try:
        os.remove(merged_filename)
    except FileNotFoundError:
        pass
    print("Trying to merge chunk rasters...")
    merge_command = ["python", gdal_path, "-o", merged_filename]
    merge_command.extend([os.path.join(folder_name, file) for file in os.listdir(folder_name)])
    subprocess.call(merge_command)