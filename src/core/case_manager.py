import random

class CaseManager:
    def __init__(self, cities_data, suspects_data):
        self.all_cities = cities_data
        self.all_suspects = suspects_data
        self.current_case = None

    def generate_case(self, num_cities=4, start_hours=120):
        if len(self.all_cities) < num_cities:
            raise ValueError("No hay suficientes ciudades en la base de datos para generar una ruta.")

        # 1. Seleccionar un sospechoso al azar
        suspect = random.choice(self.all_suspects)

        # 2. Generar una ruta aleatoria (ej. Madrid -> Sevilla -> Zaragoza)
        route = random.sample(self.all_cities, num_cities)
        
        # 3. Inicializar el estado del caso
        self.current_case = {
            "suspect": suspect,
            "route": route,         # La lista de ciudades en orden
            "current_city_index": 0, # Empieza en la primera ciudad de la ruta
            "remaining_hours": start_hours,
            "warrant_issued_for": None,
            "is_active": True
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

    def generate_clue(self, location_type):
        # Devuelve un diccionario con el tipo de pista ('text' o 'image') y su contenido
        next_city = self.get_next_city()
        suspect = self.current_case["suspect"]
        
        if next_city:
            # 50% de probabilidad de ser una pista de imagen (foto de la ciudad) o texto
            if random.random() < 0.5:
                # Pista de texto
                clues = [
                    f"Me dijo que quería ir a ver {next_city['places'][0]}.",
                    f"Llevaba un billete hacia {next_city['region']}.",
                    f"Mencionó que le encantaba la comida de {next_city['name']}."
                ]
                return {"type": "text", "content": random.choice(clues)}
            else:
                # Pista de imagen
                return {
                    "type": "image",
                    "content": "Me enseñó esta fotografía y me preguntó cómo llegar a este lugar...",
                    # Apuntamos a una imagen que debería existir en assets/images/cities/
                    # Flet la cargará si existe, si no mostrará un icono de error por defecto
                    "image_path": f"images/cities/{next_city['id']}.jpg"
                }
        else:
            # Si no hay siguiente ciudad, da una pista física sobre el sospechoso
            clues = [
                f"Me fijé en que tenía el pelo {suspect['hair']}.",
                f"Hablaba sobre su afición al {suspect['hobby']}.",
                f"Conducía un {suspect['vehicle']}."
            ]
            return {"type": "text", "content": random.choice(clues)}
