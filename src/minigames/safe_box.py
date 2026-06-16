import flet as ft
import random

class SafeBoxGame(ft.Column):
    def __init__(self, difficulty_digits=4, max_attempts=5, on_win=None, on_lose=None):
        super().__init__()
        self.difficulty_digits = difficulty_digits
        self.max_attempts = max_attempts
        self.on_win = on_win
        self.on_lose = on_lose
        
        self.secret_code = [str(random.randint(0, 9)) for _ in range(difficulty_digits)]
        self.attempts = 0
        
        self.history = ft.ListView(expand=True, spacing=5, height=150)
        self.inputs = [
            ft.TextField(width=50, text_align=ft.TextAlign.CENTER, max_length=1, keyboard_type=ft.KeyboardType.NUMBER) 
            for _ in range(difficulty_digits)
        ]
        
        self.submit_btn = ft.ElevatedButton("Intentar Abrir", on_click=self.check_code)
        
        self.controls = [
            ft.Text("Mecanismo de la Caja Fuerte", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Adivina el código de {difficulty_digits} dígitos. Tienes {max_attempts} intentos."),
            ft.Text("🟢 Verde: Correcto en posición. 🟡 Amarillo: Número existe pero en otra posición.", italic=True, size=12),
            self.history,
            ft.Row(self.inputs, alignment=ft.MainAxisAlignment.CENTER),
            self.submit_btn
        ]

    def check_code(self, e):
        guess = [inp.value for inp in self.inputs]
        if any(not val.isdigit() for val in guess):
            return # Must fill all with digits
            
        self.attempts += 1
        
        correct_pos = 0
        correct_num = 0
        
        secret_copy = list(self.secret_code)
        guess_copy = list(guess)
        
        # Check exact matches (Verde)
        for i in range(self.difficulty_digits):
            if guess_copy[i] == secret_copy[i]:
                correct_pos += 1
                secret_copy[i] = None
                guess_copy[i] = None
                
        # Check correct numbers in wrong positions (Amarillo)
        for i in range(self.difficulty_digits):
            if guess_copy[i] is not None and guess_copy[i] in secret_copy:
                correct_num += 1
                secret_copy[secret_copy.index(guess_copy[i])] = None
                
        # Add to history
        guess_str = "".join(guess)
        result_text = f"Intento {self.attempts}: {guess_str} -> 🟢 {correct_pos}  |  🟡 {correct_num}"
        self.history.controls.append(ft.Text(result_text))
        
        # Clear inputs
        for inp in self.inputs:
            inp.value = ""
        self.update()
        
        if correct_pos == self.difficulty_digits:
            self.submit_btn.disabled = True
            self.history.controls.append(ft.Text("¡CAJA FUERTE ABIERTA!", color=ft.colors.GREEN, weight=ft.FontWeight.BOLD))
            self.update()
            if self.on_win:
                self.on_win()
        elif self.attempts >= self.max_attempts:
            self.submit_btn.disabled = True
            self.history.controls.append(ft.Text(f"¡MECANISMO BLOQUEADO! El código era {''.join(self.secret_code)}", color=ft.colors.RED))
            self.update()
            if self.on_lose:
                self.on_lose()
