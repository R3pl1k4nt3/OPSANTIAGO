import flet as ft
import json
import os
import sys

# Añadir src al path para poder importar módulos internos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.case_manager import CaseManager
from minigames.safe_box import SafeBoxGame
from minigames.word_game import WordGame
from minigames.sudoku_game import SudokuGame
from minigames.trivia_game import TriviaGame

def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cities_path = os.path.join(base_dir, "data", "cities.json")
    suspects_path = os.path.join(base_dir, "data", "suspects.json")
    words_path = os.path.join(base_dir, "data", "words.json")
    items_path = os.path.join(base_dir, "data", "items.json")
    
    with open(cities_path, "r", encoding="utf-8") as f:
        cities = json.load(f)
        
    with open(suspects_path, "r", encoding="utf-8") as f:
        suspects = json.load(f)
        
    with open(words_path, "r", encoding="utf-8") as f:
        words = json.load(f)
        
    with open(items_path, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    return cities, suspects, words, items

import random

def main(page: ft.Page):
    page.title = "Operación Santiago"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    cities, suspects, word_list, items_data = load_data()

    trivia_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "trivia.json")
    with open(trivia_path, "r", encoding="utf-8") as f:
        trivia_list = json.load(f)

    assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    game_manager = CaseManager(cities, suspects, items_data, assets_dir)

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
            if case_info.get("won"):
                page.add(
                    ft.Text("¡CASO RESUELTO!", size=40, color=ft.colors.GREEN, weight=ft.FontWeight.BOLD),
                    ft.Text("¡Has capturado al ladrón y recuperado el botín a tiempo!", size=20),
                    ft.ElevatedButton("Volver a Comandancia", on_click=start_game)
                )
            else:
                page.add(
                    ft.Text("¡CASO PERDIDO!", size=40, color=ft.colors.RED, weight=ft.FontWeight.BOLD),
                    ft.Text("El sospechoso ha escapado.", size=20),
                    ft.ElevatedButton("Volver a Comandancia", on_click=start_game)
                )
            page.update()
            return

        warrant_text = "Ninguna"
        if case_info.get('warrant_issued_for'):
            w_suspect = next(s for s in suspects if s["id"] == case_info['warrant_issued_for'])
            warrant_text = w_suspect["name"]

        page.add(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column([
                            ft.Text("DATOS DEL CASO:", weight=ft.FontWeight.BOLD, size=12, color=ft.colors.GREY_400),
                            ft.Text(f"Botín: {case_info['stolen_object']['name']}", size=14),
                            ft.Text(f"Arma: {case_info['weapon']['name']}", size=14),
                        ]),
                        ft.Container(expand=True),
                        ft.Column([
                            ft.Text(f"⏳ {case_info['remaining_hours']}h", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.YELLOW),
                            ft.Text(f"Orden: {warrant_text}", size=12, color=ft.colors.CYAN),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END)
                    ]
                ),
                padding=10,
                bgcolor=ft.colors.WHITE10,
                border_radius=10
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
        game_manager.consume_time(2)
        diff = game_manager.get_difficulty_params()
        available = game_manager.get_available_minigames()

        MINIGAME_LABELS = {
            "safe":   ("🔐", "Caja Fuerte",    "Mastermind numérico"),
            "word":   ("🔤", "Descifrador",    "Tipo Wordle"),
            "sudoku": ("🔢", "Sudoku",          "Puzzle de números"),
            "trivia": ("❓", "Interrogatorio", "Pregunta sobre España"),
        }

        def launch_minigame(game_choice):
            page.dialog.open = False
            page.update()

            game_manager.register_minigame_used(game_choice)

            def on_win():
                game_manager.register_clue_found()
                clue_data = game_manager.generate_clue(place_name)

                if clue_data["type"] == "arrest":
                    case_info = game_manager.current_case
                    suspect_id = case_info["suspect"]["id"]
                    warrant_id = case_info.get("warrant_issued_for")
                    if warrant_id == suspect_id:
                        case_info["won"] = True
                        case_info["is_active"] = False
                        result_dlg.title = ft.Text("¡MISIÓN CUMPLIDA!", color="#4CAF50")
                        result_dlg.content = ft.Text(
                            f"{clue_data['content']}\n\nCon tu Orden de Arresto válida, la policía ha atrapado a "
                            f"{case_info['suspect']['name']} y recuperado {case_info['stolen_object']['name']}."
                        )
                    else:
                        case_info["won"] = False
                        case_info["is_active"] = False
                        reason = "No tenías ninguna Orden de Arresto emitida." if not warrant_id else "La orden era para la persona equivocada."
                        result_dlg.title = ft.Text("¡SOSPECHOSO EN FUGA!", color="#F44336")
                        result_dlg.content = ft.Text(f"{clue_data['content']}\n\n{reason}")
                    result_dlg.open = True
                    page.update()
                    return

                clue_content = [ft.Text(f'"{clue_data["content"]}"', italic=True)]
                if clue_data["type"] == "image":
                    clue_content.append(ft.Image(src=clue_data["image_path"], width=300, height=200, fit=ft.ImageFit.CONTAIN))
                nueva_diff = game_manager.get_difficulty_params()
                clue_content.append(ft.Text(f"Dificultad actual: {nueva_diff['label']}", size=11, color=ft.colors.GREY_400))

                result_dlg.title = ft.Text(f"Pista obtenida en {place_name}", color="#4CAF50")
                result_dlg.content = ft.Column(clue_content, tight=True, spacing=8)
                result_dlg.open = True
                page.update()

            def on_lose():
                result_dlg.title = ft.Text(f"Sin pista en {place_name}", color="#F44336")
                result_dlg.content = ft.Text("El testigo se negó a hablar. Se han consumido 2 horas.")
                result_dlg.open = True
                page.update()

            if game_choice == "safe":
                minigame = SafeBoxGame(difficulty_digits=diff["safe_digits"], max_attempts=6, on_win=on_win, on_lose=on_lose)
            elif game_choice == "word":
                minigame = WordGame(word_list=word_list, word_length=diff["word_len"], max_attempts=6, on_win=on_win, on_lose=on_lose)
            elif game_choice == "sudoku":
                minigame = SudokuGame(empty_cells=diff["sudoku_empty"], on_win=on_win, on_lose=on_lose)
            else:
                minigame = TriviaGame(trivia_list=trivia_list, difficulty=diff["trivia_d"], on_win=on_win, on_lose=on_lose)

            result_dlg = ft.AlertDialog(
                modal=True,
                on_dismiss=lambda e: show_city_screen()
            )
            page.overlay.append(result_dlg)

            game_dlg = ft.AlertDialog(
                title=ft.Text(f"Investigando {place_name}  •  {diff['label']}"),
                content=minigame,
                modal=True,
                on_dismiss=lambda e: show_city_screen()
            )
            page.dialog = game_dlg
            page.dialog.open = True
            page.update()

        # Diálogo de elección de minijuego
        choice_buttons = []
        for key in available:
            icon, name, desc = MINIGAME_LABELS[key]
            choice_buttons.append(
                ft.ElevatedButton(
                    f"{icon}  {name}  —  {desc}",
                    on_click=lambda e, k=key: launch_minigame(k),
                    width=360,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                )
            )

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"¿Qué desafío aceptas en {place_name}?"),
            content=ft.Column(
                [ft.Text(f"Dificultad: {diff['label']}  •  2 horas ya consumidas", size=12, color=ft.colors.GREY_400)]
                + choice_buttons,
                tight=True, spacing=10,
            ),
            on_dismiss=lambda e: show_city_screen(),
        )
        page.dialog.open = True
        page.update()

    def show_sigo(e):
        page.clean()
        
        def handle_warrant(suspect_id):
            game_manager.issue_warrant(suspect_id)
            show_sigo(None) # Refrescar la pantalla
            
        suspect_list = ft.ListView(expand=True, spacing=10)
        for s in suspects:
            # Construir la descripción de los atributos
            attrs = f"Sexo: {s['gender']} | Pelo: {s['hair']} | Ropa: {s['clothing']}\n"
            attrs += f"Vehículo: {s['vehicle']} | Afición: {s['hobby']}\n"
            attrs += f"Comida: {s['food']} | Rasgo: {s['feature']}"
            
            # Botón de orden de arresto
            warrant_btn = ft.ElevatedButton("Emitir Orden", on_click=lambda e, sid=s["id"]: handle_warrant(sid))
            
            # Deshabilitar u ocultar el botón si no hay caso activo o si ya está emitida para él
            if not game_manager.current_case or not game_manager.current_case["is_active"]:
                warrant_btn.visible = False
            elif game_manager.current_case.get("warrant_issued_for") == s["id"]:
                warrant_btn.text = "Orden Emitida"
                warrant_btn.disabled = True
                warrant_btn.color = ft.colors.GREEN_400
                
            suspect_list.controls.append(
                ft.ListTile(
                    title=ft.Text(s["name"], weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(attrs, size=12),
                    leading=ft.Image(src=f"images/suspects/{s['id']}.png", width=60, height=60, fit=ft.ImageFit.COVER, border_radius=5),
                    trailing=warrant_btn
                )
            )
        
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: show_city_screen() if game_manager.current_case and game_manager.current_case["is_active"] else start_game(e))

        warrant_text = "Ninguna"
        if game_manager.current_case and game_manager.current_case.get('warrant_issued_for'):
            w_suspect = next(s for s in suspects if s["id"] == game_manager.current_case['warrant_issued_for'])
            warrant_text = w_suspect["name"]

        page.add(
            ft.Text("Base de Datos SIGO", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Orden de Arresto Actual: {warrant_text}", color=ft.colors.CYAN),
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
