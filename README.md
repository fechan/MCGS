# MCGS
![MCGS Logo](https://user-images.githubusercontent.com/56131910/116846288-d31be280-ab9c-11eb-9b4f-669b33a0ecfb.png)

Minecraft Geological Survey - Tools for mapping and analyzing Minecraft maps
Featured in "Visualizing player engagement with virtual spaces using GIS" (SIGBOVIK 2020, page 273)

**About 1.16:** The BlockStates format that is used in Minecraft 1.16 was created in 20w17a and is different from previous versions. All the "fast" versions support 1.16, but the non-fast versions are dependent on the anvil_parser library. I don't know if or when they'll support the new format.

MCGS contains the following files:
* `overviewernbt.py` - The `nbt.py` file from Minecraft Overviewer renamed to prevent name conflicts with anvil-parser. Required by some MCGS scripts.
* `extract_heightmaps.py` - (Requires overviewernbt.py) Extracts heightmaps for a region file, either as many individual ESRI ASCII grids per chunk or one GeoTIFF for the whole region
* `plot_inhabitedtime.py` - (Requires overviewernbt.py) Extracts a region's chunk InhabitedTime as an ESRI ASCII grid
* `print_diamond_ores.py` - (Requires anvil-parser Python library) Prints the locations of a target block to the console
* `print_diamond_ores_fast.py` - (Requires overviewernbt.py) Fast version of the above that can scan all elevations with minimal slowdown.
* `ore_plot_qgis.py` - (Requires anvil-parser Python library) Run from the QGIS Python console and it will plot the locations of desired blocks in a new point layer
* `ore_plot_qgis_fast.py` - (Requires overviewernbt.py) Fast version of the above that can scan all elevations with minimal slowdown.
