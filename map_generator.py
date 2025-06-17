import os
import tkinter as tk
from tkinter.messagebox import showerror
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import numpy as np
import osmnx as ox  # Import complet, on utilise ox.*

# ========== PALETTES ==========
PALETTE = {
    'dark_grass': (90/255, 100/255, 35/255),
    'medium_grass': (117/255, 117/255, 47/255),
    'light_grass': (145/255, 135/255, 60/255),
    'sand': (210/255, 200/255, 160/255),
    'water': (0/255, 138/255, 255/255),
    'dark_asphalt': (100/255, 100/255, 100/255),
    'medium_asphalt': (120/255, 120/255, 120/255),
    'light_asphalt': (165/255, 160/255, 140/255),
    'gravel_dirt': (140/255, 70/255, 15/255),
    'dirt': (120/255, 70/255, 20/255),
}

PALETTE_ORIG = {
    'dark_grass': (90, 100, 35),
    'medium_grass': (117, 117, 47),
    'light_grass': (145, 135, 60),
}

VEGETATION_COLORS = {
    'light_grass': (0, 255, 0),
    'medium_grass': (64, 0, 0),
    'dark_grass': (127, 0, 0),
}

# ========== UTILS ==========
def get_natural_color(natural_value):
    if natural_value is None:
        return None
    nv = str(natural_value).lower()
    if nv in ['tree', 'wood', 'shrubbery', 'tree_row']:
        return PALETTE['dark_grass']
    elif nv in ['grassland', 'heath', 'scrub']:
        return PALETTE['light_grass']
    elif nv in ['fell', 'tundra']:
        return PALETTE['medium_grass']
    elif nv in ['sand', 'beach']:
        return PALETTE['sand']
    elif nv in ['water', 'wetland', 'bay', 'coastline']:
        return PALETTE['water']
    else:
        return None

def get_landuse_color(landuse_value):
    if landuse_value:
        return PALETTE['light_grass']
    return None

def get_road_color(highway, surface=None):
    if isinstance(highway, list): highway = highway[0]
    if isinstance(surface, list): surface = surface[0]
    if highway in ['motorway', 'primary', 'trunk']:
        return PALETTE['dark_asphalt']
    elif highway in ['secondary', 'tertiary', 'residential', 'service', 'unclassified']:
        return PALETTE['medium_asphalt']
    elif highway in ['path', 'track', 'bridleway', 'cycleway', 'footway']:
        if surface == 'sand':
            return PALETTE['sand']
        elif surface in ['gravel', 'dirt', 'earth']:
            return PALETTE['gravel_dirt']
        else:
            return PALETTE['dirt']
    return PALETTE['medium_asphalt']

def get_road_width_m(highway):
    if isinstance(highway, list): highway = highway[0]
    return {
        'motorway': 20,
        'primary': 15,
        'trunk': 15,
        'secondary': 10,
        'tertiary': 8,
        'residential': 7,
        'service': 7,
        'unclassified': 7,
        'path': 2,
        'track': 2,
        'bridleway': 2,
        'cycleway': 2,
        'footway': 2
    }.get(highway, 8)

# ========== SIMPLIFIED MAP GENERATION ==========
def generate_map_grid(lat, lon, nb_cells, road_width_scale, margin_factor, status_label):
    try:
        status_label.config(text="Downloading OSM data... Please wait.", fg="orange")
        print("Step 1: Downloading OSM data...")
        root.update()

        cell_size_m = 300
        cell_px = 300
        total_zone_m = cell_size_m * nb_cells
        margin = total_zone_m * margin_factor
        dist = total_zone_m / 2 + margin

        G = ox.graph_from_point((lat, lon), dist=dist, network_type='all')
        gdf_edges = ox.graph_to_gdfs(G, nodes=False)

        status_label.config(text="Downloading map features...", fg="orange")
        print("Step 2: Downloading map features...")
        root.update()

        tags = {
            'natural': True, 'landuse': True, 'leisure': True,
            'tourism': True, 'amenity': True, 'building': True,
            'waterway': True
        }
        gdf_features = ox.features_from_point((lat, lon), tags=tags, dist=dist)

        status_label.config(text="Projecting geometries...", fg="orange")
        print("Step 3: Projecting geometries...")
        root.update()

        utm_crs = ox.projection.project_gdf(gdf_features).crs
        gdf_features_utm = gdf_features.to_crs(utm_crs)
        gdf_edges_utm = gdf_edges.to_crs(utm_crs)

        center_x = gdf_features_utm.geometry.centroid.x.mean()
        center_y = gdf_features_utm.geometry.centroid.y.mean()

        total_map_px = cell_px * nb_cells
        width_eff = total_zone_m + 2 * margin
        height_eff = total_zone_m + 2 * margin
        meters_per_pixel = ((width_eff / total_map_px) + (height_eff / total_map_px)) / 2

        dpi = 100
        fig, ax = plt.subplots(figsize=(total_map_px/dpi, total_map_px/dpi), dpi=dpi)
        fig.subplots_adjust(0, 0, 1, 1)

        xmin = center_x - total_zone_m / 2
        xmax = center_x + total_zone_m / 2
        ymin = center_y - total_zone_m / 2
        ymax = center_y + total_zone_m / 2

        ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, 
                               facecolor=PALETTE['light_grass'], edgecolor='none', zorder=0))

        status_label.config(text="Drawing roads and features...", fg="orange")
        print("Step 4: Drawing roads and features...")
        root.update()

        layer = gdf_features_utm[gdf_features_utm.geometry.type.isin(['Polygon', 'MultiPolygon'])].copy()
        if not layer.empty:
            for col, func in [('natural', get_natural_color), ('landuse', get_landuse_color)]:
                if col in layer.columns:
                    colors = layer[col].apply(func)
                    mask = colors.notna()
                    if mask.any():
                        layer[mask].plot(ax=ax, color=colors[mask], linewidth=0, zorder=2)

        for _, row in gdf_edges_utm.iterrows():
            highway = row.get('highway')
            if not highway: continue
            surface = row.get('surface')
            color = get_road_color(highway, surface)
            width_m = get_road_width_m(highway)
            lw = max((width_m / meters_per_pixel) * 0.01 * road_width_scale, 0.1)
            x, y = row.geometry.xy
            ax.plot(x, y, color=color, linewidth=lw, solid_capstyle='round', zorder=9)

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_axis_off()
        ax.set_aspect('equal')

        status_label.config(text="Saving temporary map image...", fg="orange")
        print("Step 5: Saving map image...")
        root.update()

        temp_filename = "map_temp.png"
        plt.savefig(temp_filename, dpi=dpi, pad_inches=0)
        plt.close()

        status_label.config(text="Slicing map into cells...", fg="orange")
        print("Step 6: Slicing map into cells...")
        root.update()

        output_dir = "map_cells"
        os.makedirs(output_dir, exist_ok=True)

        img = Image.open(temp_filename)
        img_array = np.array(img)

        for row in range(nb_cells):
            for col in range(nb_cells):
                y_start, y_end = row * cell_px, (row + 1) * cell_px
                x_start, x_end = col * cell_px, (col + 1) * cell_px
                cell_img = img_array[y_start:y_end, x_start:x_end]
                Image.fromarray(cell_img).save(f"{output_dir}/{col},{row}.png")

        os.remove(temp_filename)

        status_label.config(text=f"{nb_cells}x{nb_cells} grid generated in '{output_dir}'.", fg="#004d00")
        print(f"Map grid generation completed: {nb_cells}x{nb_cells} tiles saved in '{output_dir}'.")

    except Exception as e:
        showerror("Error", f"Map generation error: {e}")
        status_label.config(text="Error during map generation.", fg="red")
        print(f"ERROR during map generation: {e}")

# ========== VEGETATION MAPS ==========
def classify_vegetation_color(rgb):
    r, g, b = rgb
    for key, ref_rgb in PALETTE_ORIG.items():
        if all(abs(c1 - c2) < 10 for c1, c2 in zip((r, g, b), ref_rgb)):
            return VEGETATION_COLORS[key]
    return (0, 0, 0)

def generate_vegetation_maps(status_label):
    try:
        status_label.config(text="Starting vegetation map generation...", fg="orange")
        print("Vegetation: start processing images.")
        input_dir = "map_cells"
        output_dir = "map_vegetation"
        os.makedirs(output_dir, exist_ok=True)

        filenames = [f for f in os.listdir(input_dir) if f.endswith(".png")]
        total_files = len(filenames)
        print(f"Vegetation: found {total_files} files to process.")

        for idx, filename in enumerate(filenames, 1):
            status_label.config(text=f"Processing {filename} ({idx}/{total_files})...", fg="orange")
            print(f"Vegetation: processing {filename} ({idx}/{total_files})")
            root.update()

            path = os.path.join(input_dir, filename)
            img = Image.open(path).convert("RGB")
            img_array = np.array(img)
            new_array = np.zeros_like(img_array)

            for y in range(img_array.shape[0]):
                for x in range(img_array.shape[1]):
                    new_array[y, x] = classify_vegetation_color(tuple(img_array[y, x]))

            base, _ = os.path.splitext(filename)
            Image.fromarray(new_array).save(os.path.join(output_dir, f"{base}_veg.png"))

        status_label.config(text=f"Vegetation maps generated in '{output_dir}'.", fg="#004d00")
        print(f"Vegetation: generation completed, saved in '{output_dir}'.")

    except Exception as e:
        showerror("Error", f"Vegetation generation error: {e}")
        status_label.config(text="Error during vegetation generation.", fg="red")
        print(f"ERROR during vegetation generation: {e}")

# ========== GUI ==========
root = tk.Tk()
root.title("OSM + Vegetation Map Generator")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

def add_entry(label_text, default_value, row, tooltip=None):
    tk.Label(frame, text=label_text).grid(row=row, column=0, sticky='e')
    entry = tk.Entry(frame, width=25)
    entry.insert(0, str(default_value))
    entry.grid(row=row, column=1)
    if tooltip:
        def on_enter(event): status_label.config(text=tooltip)
        def on_leave(event): status_label.config(text="")
        entry.bind("<Enter>", on_enter)
        entry.bind("<Leave>", on_leave)
    return entry

lat_entry = add_entry("Latitude:", 47.8173, 0, "Latitude of the map center point.")
lon_entry = add_entry("Longitude:", -3.6325, 1, "Longitude of the map center point.")
cells_entry = add_entry("Number of cells (NxN):", 2, 2,
                       "Number of cells per side (e.g., 2 means 4 map tiles).")
margin_entry = add_entry("Calculation area (%):", 0.5, 3,
                         "Total map calculation as a percentage.\n"
                         "Higher calculation area reduces chance of missing objects \n but increases resource usage.")
width_entry = add_entry("Road width scale:", 100, 4,
                        "Scale factor for road widths on the generated maps.")

def on_generate_maps():
    try:
        lat = float(lat_entry.get())
        lon = float(lon_entry.get())
        n = int(cells_entry.get())
        margin = float(margin_entry.get())
        width_scale = float(width_entry.get())
        if n < 1:
            raise ValueError("Number of cells must be ≥ 1")
        generate_map_grid(lat, lon, n, width_scale, margin, status_label)
    except Exception as e:
        showerror("Error", f"Invalid parameter: {e}")
        status_label.config(text="Parameter error.", fg="red")

def on_generate_vegetation():
    generate_vegetation_maps(status_label)

tk.Button(frame, text="Generate Simplified Maps", command=on_generate_maps).grid(row=5, column=0, columnspan=2, pady=5)
tk.Button(frame, text="Generate Vegetation Maps", command=on_generate_vegetation).grid(row=6, column=0, columnspan=2, pady=5)

status_label = tk.Label(root, text="", fg="green")
status_label.pack(pady=5)

root.mainloop()
