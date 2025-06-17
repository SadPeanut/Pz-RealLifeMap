# Project Zomboid - Real Life Map Generator

This project provides a simple tool to generate simplified maps and vegetation map from real life terrain with OpenStreetMap data using Project Zomboid official color mapping palette.



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

* Adjust the percentage size of the **download area** for OpenStreetMap objects. The larger the size, the lower the risk of missing objects due to truncation, but it also increases the ressource usage.

* Click **"Generate Simplified Maps"** to download data and create the simplified map grid.

* Then click **"Generate Vegetation Maps"** to produce vegetation versions of these maps.

For debugging purpose, you can look at the temporary full resolution map in the root folder. Here you can see if the generation has any problems before placing cells in Worlded.

## Output

Generated images are saved automatically in two folders:

* `map_cells/` — contains simplified map tiles.
* `map_vegetation/` — contains the vegetation maps.



## About

This is a

This project uses [OSMnx](https://osmnx.readthedocs.io/)  to download OpenStreetMap data.

OpenStreetMap data is made available under the Open Database License (ODbL). You are free to copy, distribute, transmit and adapt the data, as long as you credit OpenStreetMap and its contributors. If you alter or build upon the data, you may distribute the result only under the same license.

Please make sure your usage complies with OpenStreetMap's usage policy, especially if using this tool at scale or in an automated fashion.

If you use OSMnx in your work, please cite the [paper](https://onlinelibrary.wiley.com/doi/10.1111/gean.70009):

Boeing, G. (2025). Modeling and Analyzing Urban Networks and Amenities with OSMnx. Geographical Analysis, published online ahead of print.

Developed by [SadPeanut](https://github.com/SadPeanut).