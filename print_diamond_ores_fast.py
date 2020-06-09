import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
import math;

import overviewernbt

SEARCH_BLOCK = "minecraft:diamond_ore" #the block name you want to print the positions of

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

#Main stuff
def scan_section(section, search_block):
    palette = section['Palette']
    palette_bit_size = math.ceil(math.log2(len(palette))) #number of bits needed to store highest palette index
    states = unstream(4 if palette_bit_size <= 4 else palette_bit_size, 64, section['BlockStates']) #block indeces are AT LEAST 4 bits

    #coordinates of the chunk at its lowest (x,y,z)
    chunk_x = chunk[1]['Level']['xPos']*16
    chunk_y = 16*section['Y']
    chunk_z = chunk[1]['Level']['zPos']*16

    for y in range(16):
        for x in range(16):
            for z in range(16):
                block_index = y*16*16 + z*16 + x
                if palette[states[block_index]]['Name'] == search_block:
                    print(chunk_x + x, chunk_y + y, chunk_z + z, palette[states[block_index]])

region = overviewernbt.load_region(filedialog.askopenfilename())
for chunkx in range(32):
    for chunkz in range(32):
        chunk = region.load_chunk(chunkx, chunkz)
        if chunk == None:
            print("Chunk", chunkx, chunkz, "cannot be loaded!")
        else:
            for section in chunk[1]['Level']['Sections']:
                if "Palette" in section:
                    if SEARCH_BLOCK in [block['Name'] for block in section['Palette']]: #only scan section if desired block is in its palette
                        scan_section(section, SEARCH_BLOCK)