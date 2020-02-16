import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()

import anvil

region = anvil.Region.from_file(filedialog.askopenfilename())
for chunkx in range(32):
    for chunkz in range(32):
        try:
            chunk = anvil.Chunk.from_region(region, chunkx, chunkz)
            for y in range(16):
                for x in range(16):
                    for z in range(16):
                        block = chunk.get_block(x, y, z)
                        if block.id == "diamond_ore":
                            print(block.id, "at", chunk.x.value*16+x, y, chunk.z.value*16+z)
        except Exception as e:
            if str(e) == "Unexistent chunk":
                print("Can't load chunk at", chunkx, chunkz)