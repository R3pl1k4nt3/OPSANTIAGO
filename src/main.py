import flet as ft
import json
import os
import sys

# Añadir src al path para poder importar módulos internos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.case_manager import CaseManager
from minigames.safe_box import SafeBoxGame
from minigames.word_game import WordGame

def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cities_path = os.path.join(base_dir, "data", "cities.json")
    suspects_path = os.path.join(base_dir, "data", "suspects.json")
    words_path = os.path.join(base_dir, "data", "words.json")
    
    with open(cities_path, "r", encoding="utf-8") as f:
        cities = json.load(f)
        
    with open(suspects_path, "r", encoding="utf-8") as f:
        suspects = json.load(f)
        
    with open(words_path, "r", encoding="utf-8") as f:
        words = json.load(f)
        
    return cities, suspects, words

import random

def main(page: ft.Page):
    page.title = "Operación Santiago"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    cities, suspects, word_list = load_data()
    game_manager = CaseManager(cities, suspects)

    def start_game(e):
        page.clean()
        page.add(
            ft.Text(f"Bienvenido Teniente Santiago. Hay {len(cities)} ciudades en la base de datos.", size=20),
            ft.ElevatedButton("Acceder a base de datos SIGO", on_click=show_sigo),
            ft.ElevatedButton("Recibir Nuevo Caso", on_click=start_new_case, color=ft.colors.RED_200)
        )
        page.update()

    def start_new_case(e):
        game_manager.generate_case()
        show_city_screen()

    def show_city_screen():
        page.clean()
        current_city = game_manager.get_current_city()
        case_info = game_manager.current_case
        
        if not case_info['is_active']:
            page.add(
                ft.Text("¡CASO PERDIDO!", size=40, color=ft.colors.RED, weight=ft.FontWeight.BOLD),
                ft.Text("Te has quedado sin tiempo. El sospechoso ha escapado.", size=20),
                ft.ElevatedButton("Volver a Comandancia", on_click=start_game)
            )
            page.update()
            return

        page.add(
            ft.Row(
                [
                    ft.Text(f"⏳ Tiempo restante: {case_info['remaining_hours']} horas", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.YELLOW),
                ], alignment=ft.MainAxisAlignment.END
            ),
            ft.Text(f"Ubicación Actual: {current_city['name']}", size=30, weight=ft.FontWeight.BOLD),
            ft.Text(f"Región: {current_city['region']}", italic=True),
            ft.Text(current_city['description'], size=16),
            ft.Divider(),
            ft.Text("Acciones:", weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("Investigar la ciudad", icon=ft.icons.SEARCH, on_click=lambda e: show_investigate_screen()),
                ft.ElevatedButton("Viajar", icon=ft.icons.AIRPLANEMODE_ACTIVE, on_click=lambda e: show_travel_screen()),
                ft.ElevatedButton("Conectar a SIGO", icon=ft.icons.COMPUTER, on_click=show_sigo)
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
        page.update()

    def show_investigate_screen():
        page.clean()
        current_city = game_manager.get_current_city()
        page.add(
            ft.Text(f"Investigando en {current_city['name']}", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("¿A dónde quieres ir? (Consume 2 horas)", size=18)
        )
        for place in current_city['places']:
            page.add(ft.ElevatedButton(f"Visitar {place}", on_click=lambda e, p=place: investigate_place(p)))
            
        page.add(
            ft.Divider(),
            ft.ElevatedButton("Volver", on_click=lambda e: show_city_screen())
        )
        page.update()

    def show_travel_screen():
        page.clean()
        page.add(
            ft.Text("Aeropuerto / Estación", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Elige tu próximo destino (Consume 8 horas)", size=18)
        )
        
        current_city = game_manager.get_current_city()
        next_city = game_manager.get_next_city()
        
        options = random.sample([c for c in cities if c['id'] != current_city['id']], 3)
        if next_city and next_city not in options:
            options[0] = next_city
        random.shuffle(options)
        
        for opt in options:
            page.add(ft.ElevatedButton(f"Viajar a {opt['name']}", on_click=lambda e, cid=opt['id']: handle_travel(cid)))
            
        page.add(
            ft.Divider(),
            ft.ElevatedButton("Cancelar", on_click=lambda e: show_city_screen())
        )
        page.update()

    def handle_travel(city_id):
        success, message = game_manager.travel_to(city_id)
        
        def close_travel_dialog(e):
            page.dialog.open = False
            show_city_screen()
            
        page.dialog = ft.AlertDialog(
            title=ft.Text("Informe de Viaje"),
            content=ft.Text(message),
            on_dismiss=close_travel_dialog
        )
        page.dialog.open = True
        page.update()

    def investigate_place(place_name):
        game_manager.consume_time(2) # Investigar cuesta 2 horas de entrada
        
        def on_win():
            clue_data = game_manager.generate_clue(place_name)
            
            clue_content = []
            clue_content.append(ft.Text(f'"{clue_data["content"]}"\n\n(Se han consumido 2 horas)'))
            
            if clue_data["type"] == "image":
                clue_content.append(ft.Image(src=clue_data["image_path"], width=300, height=200, fit=ft.ImageFit.CONTAIN))
            
            page.dialog.title = ft.Text(f"Testigo en {place_name} (¡ÉXITO!)")
            page.dialog.content = ft.Column(clue_content, tight=True)
            page.update()

        def on_lose():
            page.dialog.title = ft.Text(f"Testigo en {place_name} (FALLO)")
            page.dialog.content = ft.Text("No has logrado superar el mecanismo. El testigo se ha asustado y no te dirá nada.\n\n(Se han consumido 2 horas)")
            page.update()

        # Elegir minijuego al azar
        if random.random() < 0.5:
            minigame = SafeBoxGame(difficulty_digits=4, max_attempts=5, on_win=on_win, on_lose=on_lose)
        else:
            minigame = WordGame(word_list=word_list, max_attempts=6, on_win=on_win, on_lose=on_lose)
        
        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Investigando {place_name}..."),
            content=minigame,
            on_dismiss=lambda e: show_city_screen()
        )
        page.dialog.open = True
        page.update()

    def show_sigo(e):
        page.clean()
        suspect_list = ft.ListView(expand=True, spacing=10)
        for s in suspects:
            suspect_list.controls.append(
                ft.ListTile(
                    title=ft.Text(s["name"]),
                    subtitle=ft.Text(f"Pelo: {s['hair']}, Vehículo: {s['vehicle']}, Afición: {s['hobby']}, Rasgo: {s['feature']}"),
                    leading=ft.Icon(ft.icons.PERSON)
                )
            )
        
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: show_city_screen() if game_manager.current_case and game_manager.current_case["is_active"] else start_game(e))

        page.add(
            ft.Text("Base de Datos SIGO", size=24, weight=ft.FontWeight.BOLD),
            suspect_list,
            volver_btn
        )
        page.update()

    # Initial Screen
    page.add(
        ft.Text("OPERACIÓN SANTIAGO", size=40, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_200),
        ft.Text("Cargando...", italic=True),
        ft.ElevatedButton("Comenzar Investigación", on_click=start_game)
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="../assets", view=ft.AppView.WEB_BROWSER, port=8550)
