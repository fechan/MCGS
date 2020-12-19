import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
import math;

import overviewernbt

SEARCH_BLOCK = "minecraft:diamond_ore" #the block name you want to print the positions of

NETHER_BLOCKSTATES_DATAVERSION = 2529 #minimum DataVersion using the 1.16 BlockStates format (20w17a)

#Utility functions
def unstream(bits_per_value, word_size, data):
    """Converts data in an NBT long array into a list of ints, used before the introduction of the
    new BlockStates format introduced in 20w17a"""
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
    n = 4096
    result = [0] * n
    shorts_per_long = 64 // bits_per_value
    mask = (1 << bits_per_value) - 1

    for i in range(shorts_per_long):
        j = (n + shorts_per_long - 1 - i) // shorts_per_long
        result[i::shorts_per_long] = [(b >> (bits_per_value * i)) & mask for b in data[:j]]
    
    return result

def index_to_coordinates(index, chunk_x, chunk_y, chunk_z):
    """Converts an index in the BlockStates array to its corresponding coordinates in the world.

    The hex magic works because each chunk section is 16*16*16 blocks, so the hexidecimal digits
    in the index represent the block's (y,x,z) in that order. It's similar to bitwise flags"""
    return (
        (index & 0x00f) + chunk_x,
        (index & 0xf00) // 256 + chunk_y,
        (index & 0x0f0) // 16 + chunk_z
        )

#Main stuff
def scan_section(section, search_block):
    palette = section['Palette']
    palette_bit_size = math.ceil(math.log2(len(palette))) #number of bits needed to store highest palette index
    palette_bit_size = 4 if palette_bit_size <= 4 else palette_bit_size #block indeces are AT LEAST 4 bits
    if chunk[1]['DataVersion'] < NETHER_BLOCKSTATES_DATAVERSION:
        states = unstream(palette_bit_size, 64, section['BlockStates']) 
    else:
        states = nether_unstream(palette_bit_size, section['BlockStates'])

    #coordinates of the chunk at its lowest (x,y,z)
    chunk_x = chunk[1]['Level']['xPos']*16
    chunk_y = 16*section['Y']
    chunk_z = chunk[1]['Level']['zPos']*16

    #first find where in the palette our desired block appears
    palette_indexes = [index for index, block in enumerate(palette) if block["Name"] == search_block]
    #then, find the index of blocks which exist in the above palette index list
    states_indexes = [index for index, block in enumerate(states) if block in palette_indexes]

    coordinates = [index_to_coordinates(index, chunk_x, chunk_y, chunk_z) for index in states_indexes]
    return coordinates

region = overviewernbt.load_region("/home/compupro/.local/share/multimc/instances/1.16/.minecraft/saves/Building Creative/region/r.0.0.mca")
coordinates = []
for chunkx in range(32):
    for chunkz in range(32):
        chunk = region.load_chunk(chunkx, chunkz)
        if chunk == None:
            print("Chunk", chunkx, chunkz, "cannot be loaded!")
        else:
            for section in chunk[1]['Level']['Sections']:
                if "Palette" in section:
                    if SEARCH_BLOCK in [block['Name'] for block in section['Palette']]: #only scan section if desired block is in its palette
                        coordinates += scan_section(section, SEARCH_BLOCK)
for block in coordinates:
    print(block)