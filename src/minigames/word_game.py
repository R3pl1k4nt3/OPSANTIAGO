import flet as ft
import random

class WordGame(ft.Column):
    def __init__(self, word_list, word_length=5, max_attempts=6, on_win=None, on_lose=None):
        super().__init__()
        self.word_length = word_length
        self.word_list = [w.upper() for w in word_list if len(w) == word_length]
        if not self.word_list:
            # Fallback en caso de que no haya palabras de esa longitud (usará PISTA como parche)
            self.word_list = ["P" * word_length]

        self.max_attempts = max_attempts
        self.on_win = on_win
        self.on_lose = on_lose
        
        self.secret_word = random.choice(self.word_list)
        self.attempts = 0
        
        self.history = ft.ListView(expand=True, spacing=5, height=200)
        self.input_field = ft.TextField(
            label=f"Escribe una palabra de {word_length} letras", 
            max_length=word_length, 
            capitalization=ft.TextCapitalization.CHARACTERS,
            on_submit=self.check_word
        )
        
        self.submit_btn = ft.ElevatedButton("Comprobar Palabra", on_click=self.check_word)
        
        self.controls = [
            ft.Text("Descifrador de Comunicaciones", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Adivina la palabra clave de {word_length} letras. Tienes {max_attempts} intentos."),
            ft.Text("🟩 Letra y posición correctas\n🟨 Letra correcta, posición incorrecta\n⬛ Letra incorrecta", italic=True, size=12),
            self.history,
            self.input_field,
            self.submit_btn
        ]

    def check_word(self, e):
        guess = self.input_field.value.upper()
        if len(guess) != self.word_length:
            return
            
        self.attempts += 1
        
        secret_chars = list(self.secret_word)
        guess_chars = list(guess)
        
        result_colors = ["#555555"] * self.word_length

        # Primero buscamos las coincidencias exactas (Verde)
        for i in range(self.word_length):
            if guess_chars[i] == secret_chars[i]:
                result_colors[i] = "#4CAF50"
                secret_chars[i] = None
                guess_chars[i] = None

        # Luego buscamos letras correctas en posiciones incorrectas (Amarillo)
        for i in range(self.word_length):
            if guess_chars[i] is not None and guess_chars[i] in secret_chars:
                result_colors[i] = "#FFC107"
                secret_chars[secret_chars.index(guess_chars[i])] = None

        # Crear los spans visuales para el historial
        spans = []
        for i in range(self.word_length):
            spans.append(ft.TextSpan(guess[i] + " ", style=ft.TextStyle(color=result_colors[i], weight=ft.FontWeight.BOLD, size=18)))
            
        self.history.controls.append(ft.Text(spans=spans))
        
        self.input_field.value = ""
        self.update()
        
        if guess == self.secret_word:
            self.submit_btn.disabled = True
            self.input_field.disabled = True
            self.history.controls.append(ft.Text("¡DESCIFRADO CON ÉXITO!", color=ft.colors.GREEN, weight=ft.FontWeight.BOLD))
            self.update()
            if self.on_win:
                self.on_win()
        elif self.attempts >= self.max_attempts:
            self.submit_btn.disabled = True
            self.input_field.disabled = True
            self.history.controls.append(ft.Text(f"¡COMUNICACIÓN PERDIDA! La palabra era {self.secret_word}", color=ft.colors.RED))
            self.update()
            if self.on_lose:
                self.on_lose()
