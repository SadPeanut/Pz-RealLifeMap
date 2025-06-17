import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image
import os

# Palette RGB normalisée (0..1)
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
    'dark_pothole': (110/255, 100/255, 100/255),
    'light_pothole': (130/255, 120/255, 120/255)
}

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
    if landuse_value is None or landuse_value == '' or str(landuse_value).lower() == 'nan':
        return None
    return PALETTE['light_grass']

def get_road_color(highway, surface=None):
    if isinstance(highway, list):
        highway = highway[0]
    if isinstance(surface, list):
        surface = surface[0]

    if highway in ['motorway', 'primary', 'trunk']:
        return PALETTE['dark_asphalt']
    elif highway in ['secondary', 'tertiary']:
        return PALETTE['medium_asphalt']
    elif highway in ['residential', 'service', 'unclassified']:
        return PALETTE['medium_asphalt']
    elif highway in ['path', 'track', 'bridleway', 'cycleway', 'footway']:
        if surface == 'sand':
            return PALETTE['sand']
        elif surface in ['gravel', 'dirt', 'earth']:
            return PALETTE['gravel_dirt']
        else:
            return PALETTE['dirt']
    else:
        return PALETTE['medium_asphalt']

def get_road_width_m(highway):
    if isinstance(highway, list):
        highway = highway[0]
    if highway == 'motorway':
        return 20
    elif highway == 'primary':
        return 15
    elif highway == 'trunk':
        return 15
    elif highway == 'secondary':
        return 10
    elif highway == 'tertiary':
        return 8
    elif highway in ['residential', 'service', 'unclassified']:
        return 7
    elif highway in ['path', 'track', 'bridleway', 'cycleway', 'footway']:
        return 2
    else:
        return 8

def generate_map_grid(lat, lon, nb_cellules, road_width_scale, margin_factor, status_label, root):
    try:
        status_label.config(text="Téléchargement des données... Patientez.")
        root.update()

        # Paramètres de base
        zone_cellule = 300  # 300m par cellule
        cellule_px = 300    # 300px par cellule
        
        # Calcul de la zone totale
        zone_totale = zone_cellule * nb_cellules
        margin = zone_totale * margin_factor
        dist = zone_totale / 2 + margin

        # Téléchargement des données pour toute la zone
        G = ox.graph_from_point((lat, lon), dist=dist, network_type='all')
        gdf_edges = ox.graph_to_gdfs(G, nodes=False)

        tags = {
            'natural': True,
            'landuse': True,
            'leisure': True,
            'tourism': True,
            'amenity': True,
            'building': True,
            'waterway': True
        }
        gdf_features = ox.features_from_point((lat, lon), tags=tags, dist=dist)

        utm_crs = ox.projection.project_gdf(gdf_features).crs
        gdf_features_utm = gdf_features.to_crs(utm_crs)
        gdf_edges_utm = gdf_edges.to_crs(utm_crs)

        # Centre de la zone
        center_x = gdf_features_utm.geometry.centroid.x.mean()
        center_y = gdf_features_utm.geometry.centroid.y.mean()

        # Dimensions de la carte totale
        carte_totale_px = cellule_px * nb_cellules
        largeur_eff = zone_totale + 2 * margin
        hauteur_eff = zone_totale + 2 * margin

        m_per_pixel_x = largeur_eff / carte_totale_px
        m_per_pixel_y = hauteur_eff / carte_totale_px
        m_per_pixel = (m_per_pixel_x + m_per_pixel_y) / 2

        # Génération de la carte complète
        dpi = 100
        fig_width = carte_totale_px / dpi
        fig_height = carte_totale_px / dpi
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

        # Limites de la carte complète
        xmin = center_x - zone_totale/2
        xmax = center_x + zone_totale/2
        ymin = center_y - zone_totale/2
        ymax = center_y + zone_totale/2

        # Fond de carte
        ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, 
                              facecolor=PALETTE['light_grass'], edgecolor='none', zorder=0, antialiased=False))

        # Rendu des couches géographiques
        layer = gdf_features_utm[gdf_features_utm.geometry.type.isin(['Polygon', 'MultiPolygon'])].copy()

        if not layer.empty:
            colors = layer['natural'].apply(get_natural_color)
            mask = colors.notna()
            if mask.any():
                layer_to_plot = layer[mask]
                layer_to_plot.plot(ax=ax, color=colors[mask], linewidth=0, antialiased=False, zorder=2)

        if not layer.empty:
            if 'landuse' in layer.columns:
                landuse_colors = layer['landuse'].apply(get_landuse_color)
                landuse_mask = landuse_colors.notna()
                if landuse_mask.any():
                    landuse_layer_to_plot = layer[landuse_mask]
                    landuse_layer_to_plot.plot(ax=ax, color=landuse_colors[landuse_mask], linewidth=0, antialiased=False, zorder=3)

        if not layer.empty:
            sand_colors = layer['natural'].apply(lambda x: PALETTE['sand'] if x and str(x).lower() in ['sand', 'beach'] else None)
            sand_mask = sand_colors.notna()
            if sand_mask.any():
                sand_layer = layer[sand_mask]
                sand_layer.plot(ax=ax, color=sand_colors[sand_mask], linewidth=0, antialiased=False, zorder=5)

        if not layer.empty:
            water_colors = layer['natural'].apply(lambda x: PALETTE['water'] if x and str(x).lower() in ['water', 'wetland', 'bay', 'coastline'] else None)
            water_mask = water_colors.notna()
            if water_mask.any():
                water_layer = layer[water_mask]
                water_layer.plot(ax=ax, color=water_colors[water_mask], linewidth=0, antialiased=False, zorder=15)

        # Rendu des routes
        for _, row in gdf_edges_utm.iterrows():
            highway = row.get('highway')
            surface = row.get('surface')
            if highway is None:
                continue
            color = get_road_color(highway, surface)
            width_m = get_road_width_m(highway)
            linewidth_pt = max((width_m / m_per_pixel) * 0.01 * road_width_scale, 0.1)
            x, y = row.geometry.xy
            ax.plot(x, y, color=color, linewidth=linewidth_pt, solid_capstyle='round', zorder=9, antialiased=False)

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_axis_off()
        ax.set_aspect('equal')

        # Sauvegarde de la carte complète temporaire
        temp_filename = "carte_complete_temp.png"
        plt.savefig(temp_filename, dpi=dpi, pad_inches=0)
        plt.close()

        status_label.config(text="Découpage en cellules...")
        root.update()

        # Découpage en cellules
        img = Image.open(temp_filename)
        img_array = np.array(img)

        # Création du dossier de sortie
        output_dir = "cartes_cellules"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Découpage et sauvegarde des cellules
        for row in range(nb_cellules):
            for col in range(nb_cellules):
                # Calcul des coordonnées de découpage
                y_start = row * cellule_px
                y_end = (row + 1) * cellule_px
                x_start = col * cellule_px
                x_end = (col + 1) * cellule_px
                
                # Extraction de la cellule
                cellule = img_array[y_start:y_end, x_start:x_end]
                
                # Création de l'image de la cellule
                cellule_img = Image.fromarray(cellule)
                
                # Nom du fichier avec coordonnées
                filename = f"{output_dir}/{col},{row}.png"
                cellule_img.save(filename)

        # Suppression du fichier temporaire
        os.remove(temp_filename)

        status_label.config(text=f"Grille de {nb_cellules}x{nb_cellules} cartes générée dans le dossier '{output_dir}'.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
        status_label.config(text="Erreur lors de la génération.")

root = tk.Tk()
root.title("Générateur de grille de cartes OSM")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

def add_label_entry(row, label_text, default_val, tooltip_text=None):
    tk.Label(frame, text=label_text).grid(row=row, column=0, sticky='e')
    entry = tk.Entry(frame, width=25)
    entry.grid(row=row, column=1)
    entry.insert(0, str(default_val))
    if tooltip_text:
        def on_enter(e): status_label.config(text=tooltip_text)
        def on_leave(e): status_label.config(text="")
        entry.bind("<Enter>", on_enter)
        entry.bind("<Leave>", on_leave)
    return entry

DEFAULTS = {
    'lat': 47.81726751510532,
    'lon': -3.632532891029882,
    'nb_cellules': 2,
    'margin_factor': 0.5,
    'road_width_scale': 100,
}

row_idx = 0
lat_entry = add_label_entry(row_idx, "Latitude (°):", DEFAULTS['lat'])
row_idx += 1
lon_entry = add_label_entry(row_idx, "Longitude (°):", DEFAULTS['lon'])
row_idx += 1
nb_cellules_entry = add_label_entry(row_idx, "Nombre de cellules (NxN):", DEFAULTS['nb_cellules'], 
                                   "Nombre de cellules par côté (ex: 2 = grille 2x2 = 4 cartes)")
row_idx += 1
margin_factor_entry = add_label_entry(row_idx, "Facteur de marge :", DEFAULTS['margin_factor'])
row_idx += 1
road_width_scale_entry = add_label_entry(row_idx, "Échelle largeur route:", DEFAULTS['road_width_scale'])
row_idx += 1

def on_generate():
    try:
        lat = float(lat_entry.get())
        lon = float(lon_entry.get())
        nb_cellules = int(nb_cellules_entry.get())
        margin_factor = float(margin_factor_entry.get())
        road_width_scale = float(road_width_scale_entry.get())

        if nb_cellules < 1:
            raise ValueError("Le nombre de cellules doit être au moins 1")

        status_label.config(text="")
        generate_map_grid(lat, lon, nb_cellules, road_width_scale, margin_factor, status_label, root)
    except Exception as e:
        messagebox.showerror("Erreur", f"Entrée invalide : {e}")
        status_label.config(text="Erreur dans les paramètres.")

generate_button = tk.Button(frame, text="Générer la grille de cartes", command=on_generate)
generate_button.grid(row=row_idx, column=0, columnspan=2, pady=10)

status_label = tk.Label(root, text="", fg="orange")
status_label.pack()

root.mainloop()