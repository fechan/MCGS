"""
    Scans a Minecraft .mca Anvil region file for blocks in TRACKED_ORES
    then puts them in a new temporary layer in QGIS
    This is the fast version that doesn't requite anvil-parser and can
    scan all elevations without slowdown

    Requires overviewernbt.py, distributed with MCGS
    You have to add it to your PATH though! (See line 12)
    Tested in QGIS 3.12 with saves from Minecraft 1.15.2 and 1.16
"""
import sys 
sys.path.append("/path/to/directory/containing/overviewernbt/") # IMPORTANT: Add the path of overviewernbt.py here!
import overviewernbt
from qgis.PyQt.QtCore import QVariant

TRACKED_ORES = ["minecraft:diamond_ore"]  # list ores you want to track here by their FULL ID

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

# create layer
layer = QgsVectorLayer("Point", "ores", "memory")
pr = layer.dataProvider()

# add fields
pr.addAttributes([QgsField("type", QVariant.String),
                    QgsField("x",  QVariant.Int),
                    QgsField("y",  QVariant.Int),
                    QgsField("z",  QVariant.Int)])
layer.updateFields() # tell the vector layer to fetch changes from the provider

def scan_section(section, tracked_ores):
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

    #coordinates of the chunk at its lowest (x,y,z)
    chunk_x = chunk[1]['Level']['xPos']*16
    chunk_y = 16*section['Y']
    chunk_z = chunk[1]['Level']['zPos']*16

    #first find where in the palette our desired blocks appear
    palette_indexes = [index for index, block in enumerate(palette) if block["Name"] in tracked_ores]
    #then, find the index of blocks which exist in the above palette index list
    blocks = [(index, palette[block]) for index, block in enumerate(states) if block in palette_indexes]

    coordinates = [(index_to_coordinates(index, chunk_x, chunk_y, chunk_z), block_data) for index, block_data in blocks]
    return coordinates

region = overviewernbt.load_region(QFileDialog.getOpenFileName()[0])
print("Ore plot started!")

coordinates = []
for chunkx in range(32):
    for chunkz in range(32):
        chunk = region.load_chunk(chunkx, chunkz)
        if chunk == None:
            print("Chunk", chunkx, chunkz, "cannot be loaded!")
        else:
            for section in chunk[1]['Level']['Sections']:
                if "Palette" in section:
                    if not set(TRACKED_ORES).isdisjoint([block['Name'] for block in section['Palette']]): #only scan section if palette has a tracked ore
                        coordinates += scan_section(section, TRACKED_ORES)

for block in coordinates:
    ore_x, ore_y, ore_z = block[0]
    ore_data = block[1]

    point = QgsFeature()
    point.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(ore_x, ore_z)))
    point.setAttributes([str(ore_data), ore_x, ore_y, ore_z])
    pr.addFeatures([point])

# update layer's extent when new features have been added
# because change of extent in provider is not propagated to the layer
layer.updateExtents()

# add the layer to the project canvas
registry = QgsProject.instance()
registry.addMapLayer(layer)