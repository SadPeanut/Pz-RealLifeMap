from PIL import Image
import numpy as np
import os

# Couleurs originales normalisées de la palette
PALETTE_ORIG = {
    'dark_grass': (90, 100, 35),
    'medium_grass': (117, 117, 47),
    'light_grass': (145, 135, 60),
}

# Couleurs végétales souhaitées
VEGETATION_COLORS = {
    'light_grass': (0, 255, 0),
    'medium_grass': (64, 0, 0),
    'dark_grass': (127, 0, 0)
}

# Fonction pour associer une couleur à la classe végétale
def classify_vegetation_color(rgb):
    r, g, b = rgb
    for key, ref_rgb in PALETTE_ORIG.items():
        if all(abs(c1 - c2) < 10 for c1, c2 in zip((r, g, b), ref_rgb)):
            return VEGETATION_COLORS[key]
    return (0, 0, 0)  # non végétal → noir

# Dossiers
input_dir = "cartes_cellules"
output_dir = "cartes_vegetation"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(input_dir):
    if filename.endswith(".png"):
        path = os.path.join(input_dir, filename)
        img = Image.open(path).convert("RGB")
        img_array = np.array(img)

        # Création d'une nouvelle image vide
        new_img_array = np.zeros_like(img_array)

        # Application du filtre végétation
        for y in range(img_array.shape[0]):
            for x in range(img_array.shape[1]):
                pixel = tuple(img_array[y, x])
                new_img_array[y, x] = classify_vegetation_color(pixel)

        # Sauvegarde de l'image végétale
        new_img = Image.fromarray(new_img_array)
        base_name, _ = os.path.splitext(filename)
        new_img.save(os.path.join(output_dir, f"{base_name}_veg.png"))


print(f"Génération des cartes végétales terminée dans le dossier '{output_dir}'.")
