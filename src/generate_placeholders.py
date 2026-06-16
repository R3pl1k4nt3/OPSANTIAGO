import os
from PIL import Image, ImageDraw, ImageFont
import json

def create_placeholder(text, filename, width=600, height=400, bg_color=(50, 50, 50), text_color=(255, 255, 255)):
    # Create a new image with solid background
    img = Image.new('RGB', (width, height), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Use a basic default font (Pillow's default bitmap font)
    # This is small, but ensures it runs anywhere without needing system fonts.
    try:
        # Try to load a generic TTF if available in most linux distros
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
    except:
        font = ImageFont.load_default()
        
    # Get text bounding box to center it
    bbox = d.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    d.text((x, y), text, fill=text_color, font=font)
    img.save(filename)
    print(f"Generado: {filename}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cities_file = os.path.join(base_dir, "data", "cities.json")
    suspects_file = os.path.join(base_dir, "data", "suspects.json")
    cities_dir = os.path.join(base_dir, "assets", "images", "cities")
    suspects_dir = os.path.join(base_dir, "assets", "images", "suspects")
    
    os.makedirs(cities_dir, exist_ok=True)
    os.makedirs(suspects_dir, exist_ok=True)
    
    if os.path.exists(cities_file):
        with open(cities_file, "r", encoding="utf-8") as f:
            cities = json.load(f)
            
        print(f"Generando {len(cities)} placeholders de ciudades...")
        for city in cities:
            out_path = os.path.join(cities_dir, f"{city['id']}.jpg")
            create_placeholder(f"FOTO: {city['name']}", out_path)

    if os.path.exists(suspects_file):
        with open(suspects_file, "r", encoding="utf-8") as f:
            suspects = json.load(f)
            
        print(f"Generando {len(suspects)} placeholders de sospechosos...")
        for suspect in suspects:
            out_path = os.path.join(suspects_dir, f"{suspect['id']}.png")
            create_placeholder(f"SOSP: {suspect['name']}", out_path, width=512, height=512, bg_color=(80, 20, 20))
            
    print("¡Generación completada!")
    print("Recuerda que estas imágenes son solo marcadores de posición temporales (Placeholders).")
    print("Sustitúyelas por las fotos reales de monumentos cuando las tengas preparadas.")
