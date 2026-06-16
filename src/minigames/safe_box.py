import flet as ft
import random


class SafeBoxGame(ft.Column):
    def __init__(self, difficulty_digits=3, max_attempts=6, on_win=None, on_lose=None):
        super().__init__()
        self.difficulty_digits = difficulty_digits
        self.max_attempts = max_attempts
        self.on_win = on_win
        self.on_lose = on_lose

        self.secret_code = [str(random.randint(0, 9)) for _ in range(difficulty_digits)]
        self.attempts = 0

        self.history = ft.Column(spacing=4)
        self.inputs = [
            ft.TextField(
                width=52, height=52,
                text_align=ft.TextAlign.CENTER,
                max_length=1,
                keyboard_type=ft.KeyboardType.NUMBER,
                text_style=ft.TextStyle(size=22, weight=ft.FontWeight.BOLD),
                content_padding=ft.padding.all(4),
            )
            for _ in range(difficulty_digits)
        ]

        self.status_text = ft.Text("", size=13, color=ft.colors.GREY_400)
        self.submit_btn = ft.ElevatedButton(
            "Abrir caja",
            icon=ft.icons.LOCK_OPEN,
            on_click=self.check_code,
        )

        self.controls = [
            ft.Text("Mecanismo de Caja Fuerte", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(
                f"Descifra el código de {difficulty_digits} dígitos. Tienes {max_attempts} intentos.",
                size=13,
            ),
            ft.Row([
                ft.Container(width=16, height=16, bgcolor="#4CAF50", border_radius=3),
                ft.Text("Dígito correcto en su posición", size=12),
                ft.Container(width=16, height=16, bgcolor="#FFC107", border_radius=3),
                ft.Text("Dígito existe pero en otra posición", size=12),
            ], spacing=8, wrap=True),
            ft.Divider(),
            self.history,
            ft.Row(self.inputs, alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            self.status_text,
            self.submit_btn,
        ]

    def check_code(self, e):
        guess = [inp.value for inp in self.inputs]
        if any(not v or not v.isdigit() for v in guess):
            self.status_text.value = "Rellena todos los dígitos."
            self.update()
            return

        self.attempts += 1
        secret_copy = list(self.secret_code)
        guess_copy = list(guess)

        colors = ["#555555"] * self.difficulty_digits

        # Exact matches → green
        for i in range(self.difficulty_digits):
            if guess_copy[i] == secret_copy[i]:
                colors[i] = "#4CAF50"
                secret_copy[i] = None
                guess_copy[i] = None

        # Right digit wrong position → yellow
        for i in range(self.difficulty_digits):
            if guess_copy[i] is not None and guess_copy[i] in secret_copy:
                colors[i] = "#FFC107"
                secret_copy[secret_copy.index(guess_copy[i])] = None

        # Build visual row for history
        cells = []
        for i in range(self.difficulty_digits):
            cells.append(
                ft.Container(
                    content=ft.Text(
                        guess[i],
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color="white" if colors[i] != "#FFC107" else "#1a1a1a",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=40, height=40,
                    bgcolor=colors[i],
                    border_radius=6,
                    alignment=ft.alignment.center,
                )
            )

        correct_pos = sum(1 for c in colors if c == "#4CAF50")
        row_label = ft.Text(f"#{self.attempts}", size=12, color=ft.colors.GREY_500, width=28)
        self.history.controls.append(
            ft.Row([row_label] + cells, spacing=6, alignment=ft.MainAxisAlignment.CENTER)
        )

        for inp in self.inputs:
            inp.value = ""
        self.status_text.value = ""
        self.update()

        if correct_pos == self.difficulty_digits:
            self.submit_btn.disabled = True
            self.history.controls.append(
                ft.Text("¡CAJA ABIERTA!", color="#4CAF50", weight=ft.FontWeight.BOLD, size=15)
            )
            self.update()
            if self.on_win:
                self.on_win()
        elif self.attempts >= self.max_attempts:
            self.submit_btn.disabled = True
            self.history.controls.append(
                ft.Text(
                    f"BLOQUEADA. El código era: {''.join(self.secret_code)}",
                    color="#F44336", weight=ft.FontWeight.BOLD, size=13,
                )
            )
            self.update()
            if self.on_lose:
                self.on_lose()
