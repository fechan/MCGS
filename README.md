# MCGS
Minecraft Geological Survey - Tools for mapping and analyzing Minecraft maps
Featured in "Visualizing player engagement with virtual spaces using GIS" (SIGBOVIK 2020, page 273)

MCGS contains the following files:
* `overviewernbt.py` - The `nbt.py` file from Minecraft Overviewer renamed to prevent name conflicts with anvil-parser. Required by some MCGS scripts.
* `extract_heightmaps.py` - (Requires overviewernbt.py) Extracts heightmaps for a region file, either as many individual ESRI ASCII grids per chunk or one GeoTIFF for the whole region
* `plot_inhabitedtime.py` - (Requires overviewernbt.py) Extracts a region's chunk InhabitedTime as an ESRI ASCII grid
* `print_diamond_ores.py` - (Requires anvil-parser Python library) Prints the locations of a target block to the console
* `print_diamond_ores_fast.py` - (Requires overviewernbt.py) Fast version of the above that can scan all elevations with minimal slowdown.
* `ore_plot_qgis.py` - (Requires anvil-parser Python library) Run from the QGIS Python console and it will plot the locations of desired blocks in a new point layer
* `ore_plot_qgis_fast.py` - (Requires overviewernbt.py) Fast version of the above that can scan all elevations with minimal slowdown.