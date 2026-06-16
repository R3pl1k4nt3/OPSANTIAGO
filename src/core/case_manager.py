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
        stolen_object = random.choice(self.all_items["stolen_objects"])  # {"id": ..., "name": ...}
        weapon = random.choice(self.all_items["weapons"])

        # 2. Generar una ruta aleatoria (ej. Madrid -> Sevilla -> Zaragoza)
        route = random.sample(self.all_cities, num_cities)
        
        # 3. Inicializar el estado del caso
        self.current_case = {
            "suspect": suspect,
            "stolen_object": stolen_object,
            "weapon": weapon,
            "route": route,
            "current_city_index": 0,
            "remaining_hours": start_hours,
            "warrant_issued_for": None,
            "is_active": True,
            "won": False,
            "clues_found": 0,
            "city_minigames_used": [],
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

    def get_available_minigames(self):
        all_types = ["safe", "word", "sudoku", "trivia"]
        used = self.current_case.get("city_minigames_used", [])
        available = [t for t in all_types if t not in used]
        return available if available else all_types

    def register_minigame_used(self, minigame_type):
        self.current_case["city_minigames_used"].append(minigame_type)

    def register_clue_found(self):
        self.current_case["clues_found"] = self.current_case.get("clues_found", 0) + 1

    def get_difficulty_params(self):
        clues = self.current_case.get("clues_found", 0)
        if clues < 2:
            return {"safe_digits": 3, "word_len": 5, "sudoku_empty": 25, "trivia_d": 1, "label": "Fácil"}
        elif clues < 4:
            return {"safe_digits": 4, "word_len": 5, "sudoku_empty": 35, "trivia_d": 1, "label": "Normal"}
        elif clues < 7:
            return {"safe_digits": 5, "word_len": 6, "sudoku_empty": 45, "trivia_d": 2, "label": "Difícil"}
        else:
            return {"safe_digits": 6, "word_len": 7, "sudoku_empty": 52, "trivia_d": 3, "label": "Experto"}

    def travel_to(self, city_id):
        self.consume_time(8)
        next_correct_city = self.get_next_city()
        if next_correct_city and next_correct_city["id"] == city_id:
            self.current_case["current_city_index"] += 1
            self.current_case["city_minigames_used"] = []  # reset per city
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

    def _get_witness_intro(self, place_name):
        """Returns a witness persona appropriate for the investigation location."""
        place_lower = place_name.lower()
        if any(w in place_lower for w in ["museo", "prado", "escultura", "arte", "botín"]):
            return random.choice(["El conservador de sala", "Una restauradora", "Un guía turístico"])
        if any(w in place_lower for w in ["catedral", "iglesia", "sinagoga", "basílica", "templo", "capilla"]):
            return random.choice(["El sacristán", "Una turista devota", "El guarda del templo"])
        if any(w in place_lower for w in ["playa", "malvarrosa", "canteras", "sardinero"]):
            return random.choice(["Un socorrista", "La dueña del chiringuito", "Un bañista"])
        if any(w in place_lower for w in ["mercado", "abastos", "laurel"]):
            return random.choice(["Un pescadero", "La encargada del puesto", "Un camarero del bar"])
        if any(w in place_lower for w in ["palacio", "alcázar", "castillo", "ciudadela"]):
            return random.choice(["Un guardia de seguridad", "La guía oficial del recinto", "Un fotógrafo"])
        if any(w in place_lower for w in ["parque", "retiro", "verde", "jardín"]):
            return random.choice(["Un guardia del parque", "Una corredora habitual", "El quiosquero"])
        if any(w in place_lower for w in ["teatro", "campoamor", "ópera"]):
            return random.choice(["Un tramoyista", "La acomodadora", "Un músico de la orquesta"])
        if any(w in place_lower for w in ["rambla", "plaza", "obradoiro", "castillo", "virgen blanca"]):
            return random.choice(["Un vendedor ambulante", "Un artista callejero", "Una vecina del barrio"])
        return random.choice(["Un testigo", "Una persona del lugar", "Un viandante"])

    def generate_clue(self, location_type):
        next_city = self.get_next_city()
        suspect = self.current_case["suspect"]
        witness = self._get_witness_intro(location_type)

        if next_city:
            place_ref = random.choice(next_city['places'])

            if random.random() < 0.7:
                if random.random() < 0.5:
                    destination_clues = [
                        f"{witness} recuerda haberle oído mencionar que tenía «asuntos pendientes» en {next_city['name']}.",
                        f"Según {witness.lower()}, preguntó cómo llegar a {place_ref}.",
                        f"{witness} vio cómo compraba una guía turística de {next_city['region']}.",
                        f"«Habló de {next_city['name']} como si ya hubiese estado antes», cuenta {witness.lower()}.",
                        f"{witness} oyó que buscaba alojamiento cerca de {place_ref}.",
                        f"«Llevaba un billete de tren con destino a {next_city['region']}», afirma {witness.lower()}.",
                        f"{witness} recuerda que consultó el mapa y señaló {next_city['name']} con el dedo.",
                    ]
                    return {"type": "text", "content": random.choice(destination_clues)}
                else:
                    city_img_name = f"{next_city['id']}.jpg"
                    for ext in [".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG"]:
                        img_path = os.path.join(self.assets_dir, "images", "cities", f"{next_city['id']}{ext}")
                        if os.path.exists(img_path):
                            city_img_name = f"{next_city['id']}{ext}"
                            break
                    image_clues = [
                        f"{witness} encontró esta fotografía en el suelo, justo donde estuvo sentado.",
                        f"«Me enseñó esta imagen y me preguntó si sabía cómo llegar», relata {witness.lower()}.",
                        f"{witness} vio que tenía esta foto guardada en la pantalla del teléfono.",
                    ]
                    return {
                        "type": "image",
                        "content": random.choice(image_clues),
                        "image_path": f"images/cities/{city_img_name}"
                    }
            else:
                trait_clues = [
                    f"{witness} se fijó en su llamativo pelo {suspect['hair']}.",
                    f"«Llevaba {suspect['clothing']} y no pasaba desapercibido», dice {witness.lower()}.",
                    f"{witness} recuerda que hablaba con entusiasmo sobre el {suspect['hobby']}.",
                    f"«Pidió {suspect['food']} y lo devoró en segundos», cuenta {witness.lower()}.",
                    f"{witness} no pudo evitar fijarse en su {suspect['feature']}.",
                    f"«Se marchó en {suspect['vehicle']}; lo vi arrancar desde aquí mismo», afirma {witness.lower()}.",
                ]
                return {"type": "text", "content": random.choice(trait_clues)}
        else:
            arrest_lines = [
                "¡ESTÁ AQUÍ! ¡Le veo intentando mezclarse con la multitud!",
                "¡Ahí está! ¡Está saliendo por la puerta trasera!",
                "¡El sospechoso está en el edificio! ¡No hay salida!",
            ]
            return {"type": "arrest", "content": random.choice(arrest_lines)}
