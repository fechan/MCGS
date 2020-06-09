import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
import math;

import overviewernbt

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

region = overviewernbt.load_region(filedialog.askopenfile(mode='rb'))
for chunkx in range(32):
    for chunkz in range(32):
        try:
            chunk = region.load_chunk(chunkx, chunkz)
            palette = chunk[1]['Level']['Sections'][1]['Palette']
            states = unstream(math.ceil(math.log2(len(palette))), 64, chunk[1]['Level']['Sections'][1]['BlockStates'])
            for y in range(16):
                for x in range(16):
                    for z in range(16):
                        block_index = y*16*16 + z*16 + x
                        if palette[states[block_index]]['Name'] == "minecraft:obsidian":
                            print(chunk[1]['Level']['xPos']*16+x, y, chunk[1]['Level']['zPos']*16+z, palette[states[block_index]])
        except Exception as e:
            if str(e) == "Unexistent chunk":
                print("Can't load chunk at", chunkx, chunkz)