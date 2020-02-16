"""
    Scans a Minecraft .mca Anvil region file for blocks in TRACKED_ORES
    then puts them in a new temporary layer in QGIS

    Requires anvil-parser Python library
    Tested in QGIS 3.8 with saves from Minecraft 1.14.4 and anvil-parser 0.1.1
"""

import anvil
from qgis.PyQt.QtCore import QVariant

TRACKED_ORES = ["diamond_ore"]  # list ores you want to track here by their namespaced ID
MAX_HEIGHT = 16                 # maximum height in map to search for blocks, up to 256. Big values are slower.

# create layer
layer = QgsVectorLayer("Point", "ores", "memory")
pr = layer.dataProvider()

# add fields
pr.addAttributes([QgsField("type", QVariant.String),
                    QgsField("x",  QVariant.Int),
                    QgsField("y",  QVariant.Int),
                    QgsField("z",  QVariant.Int)])
layer.updateFields() # tell the vector layer to fetch changes from the provider

region = anvil.Region.from_file(QFileDialog.getOpenFileName()[0])
for chunkx in range(32):
    for chunkz in range(32):
        try:
            chunk = anvil.Chunk.from_region(region, chunkx, chunkz)
            for y in range(MAX_HEIGHT):
                for x in range(16):
                    for z in range(16):
                        block = chunk.get_block(x, y, z)
                        if block.id in TRACKED_ORES:
                            ore_x = chunk.x.value * 16 + x
                            ore_z = chunk.z.value * 16 + z
                            point = QgsFeature()
                            point.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(ore_x, ore_z)))
                            point.setAttributes([block.id, ore_x, y, ore_z])
                            pr.addFeatures([point])
                            print(block.id, "at", chunk.x.value*16+x, y, chunk.z.value*16+z)
        except Exception as e:
            if str(e) == "Unexistent chunk":
                print("Can't load chunk at", chunkx, chunkz)

# update layer's extent when new features have been added
# because change of extent in provider is not propagated to the layer
layer.updateExtents()

# add the layer to the project canvas
registry = QgsProject.instance()
registry.addMapLayer(layer)