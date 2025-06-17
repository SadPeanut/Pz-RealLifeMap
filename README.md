# Project Zomboid - Real Life Map Generator

This project provides a simple tool to generate simplified maps and vegetation maps from real life terrain with OpenStreetMap data using Project Zomboid official color mapping palette.

<img src="https://imgur.com/T9irx4x" width="3000">
<img src="https://imgur.com/9H934XB" width="3000">
<img src="https://imgur.com/ijmUu84" width="3000">
<img src="https://imgur.com/2uxU0nR" width="3000">

![ ](https://imgur.com/gallery/project-zomboid-map-generator-tvvTRQe#T9irx4x)
![ ](https://imgur.com/gallery/project-zomboid-map-generator-tvvTRQe#9H934XB)
![ ](https://imgur.com/gallery/project-zomboid-map-generator-tvvTRQe#ijmUu84)
![ ](https://imgur.com/gallery/project-zomboid-map-generator-tvvTRQe#2uxU0nR)

## Installation

1. Clone this repository or download the files.

2. Install the required dependencies (preferably in a virtual environment):

```bash
pip install -r requirements.txt
```

**Contents of `requirements.txt`:**

```
osmnx
matplotlib
pillow
numpy
shapely
pyproj
rtree
geopandas
```
Tkinter is usually included with Python by default.

## Usage

Run the application with:

```bash
python map_generator.py
```

### In the GUI:

* Enter the **latitude** and **longitude** of the map center.

* Choose the **number of cells** per side (e.g., 2 for a 2x2 grid).

* Adjust the percentage size of the **download area** for OpenStreetMap objects. The larger the size, the lower the risk of missing objects due to truncation, but it also increases the resource usage.

* Adjust the **road width scale** to make roads more or less visible on the generated maps.

* Click **"Generate Maps + Vegetation"** to download data and create both the simplified map grid and vegetation maps in one operation.

## Output

The tool generates several types of output:

### Complete Maps (Full Resolution)
* `complete_map.png` — Full resolution simplified map of the entire downloaded area
* `complete_vegetation_map.png` — Full resolution vegetation map of the entire downloaded area

These complete maps are useful for:
- Verifying that all data was correctly downloaded and rendered
- Getting an overview of the entire area before it's split into cells
- Debugging any issues with the generation process

### Map Tiles (Cell Grid)
* `map_cells/` — Contains simplified map tiles in a grid format (e.g., `0,0.png`, `0,1.png`, etc.)
* `map_vegetation/` — Contains corresponding vegetation map tiles

Each cell is 300x300 pixels and represents a 300x300 meter area in the real world.

## Workflow

1. **Data Download**: Downloads OpenStreetMap data for roads, natural features, landuse, water bodies, etc.
2. **Map Rendering**: Creates a complete simplified map using Project Zomboid's color palette
3. **Vegetation Processing**: Generates a vegetation classification map from the simplified map
4. **Cell Division**: Splits both complete maps into individual tiles for use in map editors

## About

This project uses [OSMnx](https://osmnx.readthedocs.io/) to download OpenStreetMap data.

OpenStreetMap data is made available under the Open Database License (ODbL). You are free to copy, distribute, transmit and adapt the data, as long as you credit OpenStreetMap and its contributors. If you alter or build upon the data, you may distribute the result only under the same license.

Please make sure your usage complies with OpenStreetMap's usage policy, especially if using this tool at scale or in an automated fashion.

If you use OSMnx in your work, please cite the [paper](https://onlinelibrary.wiley.com/doi/10.1111/gean.70009):

Boeing, G. (2025). Modeling and Analyzing Urban Networks and Amenities with OSMnx. Geographical Analysis, published online ahead of print.

Developed by [SadPeanut](https://github.com/SadPeanut).
