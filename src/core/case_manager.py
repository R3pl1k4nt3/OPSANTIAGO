import random
import os

class CaseManager:
    def __init__(self, cities_data, suspects_data, items_data, assets_dir):
        self.all_cities = cities_data
        self.all_suspects = suspects_data
        self.all_items = items_data
        self.assets_dir = assets_dir
        self.current_case = None

    def generate_case(self, num_cities=4, start_hours=120):
        if len(self.all_cities) < num_cities:
            raise ValueError("No hay suficientes ciudades en la base de datos para generar una ruta.")

        # 1. Seleccionar un sospechoso al azar
        suspect = random.choice(self.all_suspects)
        
        # 1.5 Seleccionar botín y arma
        stolen_object = random.choice(self.all_items["stolen_objects"])
        weapon = random.choice(self.all_items["weapons"])

        # 2. Generar una ruta aleatoria (ej. Madrid -> Sevilla -> Zaragoza)
        route = random.sample(self.all_cities, num_cities)
        
        # 3. Inicializar el estado del caso
        self.current_case = {
            "suspect": suspect,
            "stolen_object": stolen_object,
            "weapon": weapon,
            "route": route,         # La lista de ciudades en orden
            "current_city_index": 0, # Empieza en la primera ciudad de la ruta
            "remaining_hours": start_hours,
            "warrant_issued_for": None,
            "is_active": True,
            "won": False
        }
        return self.current_case

    def get_current_city(self):
        if not self.current_case:
            return None
        return self.current_case["route"][self.current_case["current_city_index"]]

    def get_next_city(self):
        # Retorna la siguiente ciudad en la ruta, si existe
        idx = self.current_case["current_city_index"] + 1
        if idx < len(self.current_case["route"]):
            return self.current_case["route"][idx]
        return None

    def travel_to(self, city_id):
        # Al viajar consumimos tiempo
        self.consume_time(8) # 8 horas de viaje por defecto
        
        next_correct_city = self.get_next_city()
        
        # Si la ciudad elegida es la correcta en la ruta
        if next_correct_city and next_correct_city["id"] == city_id:
            self.current_case["current_city_index"] += 1
            return True, "Has seguido el rastro correctamente."
        else:
            return False, "Has perdido el rastro. El sospechoso no está por aquí."

    def consume_time(self, hours):
        if self.current_case:
            self.current_case["remaining_hours"] -= hours
            if self.current_case["remaining_hours"] <= 0:
                self.current_case["is_active"] = False
                self.current_case["remaining_hours"] = 0

    def issue_warrant(self, suspect_id):
        if self.current_case:
            self.current_case["warrant_issued_for"] = suspect_id

    def generate_clue(self, location_type):
        next_city = self.get_next_city()
        suspect = self.current_case["suspect"]
        
        if next_city:
            # 70% probabilidad de pista sobre el destino, 30% sobre el sospechoso
            if random.random() < 0.7:
                if random.random() < 0.5:
                    clues = [
                        f"Me dijo que quería ir a ver {next_city['places'][0]}.",
                        f"Llevaba un billete hacia {next_city['region']}.",
                        f"Mencionó que le encantaba la ciudad de {next_city['name']}."
                    ]
                    return {"type": "text", "content": random.choice(clues)}
                else:
                    # Determinar la extensión correcta de la imagen (jpg, png, jpeg)
                    city_img_name = f"{next_city['id']}.jpg"
                    for ext in [".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG"]:
                        img_path = os.path.join(self.assets_dir, "images", "cities", f"{next_city['id']}{ext}")
                        if os.path.exists(img_path):
                            city_img_name = f"{next_city['id']}{ext}"
                            break
                            
                    return {
                        "type": "image",
                        "content": "Me enseñó esta fotografía y me preguntó cómo llegar a este lugar...",
                        "image_path": f"images/cities/{city_img_name}"
                    }
            else:
                traits = [
                    f"Me fijé en que tenía el pelo {suspect['hair']}.",
                    f"Iba vestido con {suspect['clothing']}.",
                    f"Hablaba sin parar sobre su afición: {suspect['hobby']}.",
                    f"Estaba comiendo {suspect['food']} compulsivamente.",
                    f"Me llamó la atención su {suspect['feature']}."
                ]
                return {"type": "text", "content": random.choice(traits)}
        else:
            # Es la última ciudad de la ruta, aquí se atrapa al sospechoso
            return {"type": "arrest", "content": "¡ESTÁ AQUÍ! ¡Le veo corriendo por el callejón!"}
