import flet as ft
import random


class TriviaGame(ft.Column):
    def __init__(self, trivia_list, difficulty=1, on_win=None, on_lose=None):
        super().__init__()
        self.on_win = on_win
        self.on_lose = on_lose

        filtered = [q for q in trivia_list if q.get("d", 1) == difficulty] or trivia_list
        question_data = random.choice(filtered)
        self.correct = question_data["a"]

        options = [question_data["a"]] + question_data["w"]
        random.shuffle(options)

        self.feedback = ft.Text("", size=14)
        self.buttons = []

        for opt in options:
            btn = ft.ElevatedButton(
                opt,
                on_click=lambda e, chosen=opt: self.check_answer(chosen),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                width=380,
            )
            self.buttons.append(btn)

        self.controls = [
            ft.Text("Interrogatorio al testigo", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Responde correctamente para obtener la pista.", size=13, italic=True, color=ft.colors.GREY_400),
            ft.Divider(),
            ft.Text(question_data["q"], size=16, weight=ft.FontWeight.W_500),
            ft.Column(self.buttons, spacing=8),
            self.feedback,
        ]

    def check_answer(self, chosen):
        for btn in self.buttons:
            btn.disabled = True

        if chosen == self.correct:
            self.feedback.value = f"✓ Correcto: {self.correct}"
            self.feedback.color = "#4CAF50"
            self.update()
            if self.on_win:
                self.on_win()
        else:
            self.feedback.value = f"✗ Incorrecto. La respuesta era: {self.correct}"
            self.feedback.color = "#F44336"
            self.update()
            if self.on_lose:
                self.on_lose()
