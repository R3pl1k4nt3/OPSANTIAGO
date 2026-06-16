import flet as ft
import random

class SudokuGame(ft.Column):
    def __init__(self, empty_cells=40, on_win=None, on_lose=None):
        super().__init__()
        self.empty_cells = empty_cells
        self.on_win = on_win
        self.on_lose = on_lose
        
        # Base valid Sudoku grid
        base_grid = [
            [1,2,3, 4,5,6, 7,8,9],
            [4,5,6, 7,8,9, 1,2,3],
            [7,8,9, 1,2,3, 4,5,6],
            
            [2,3,1, 5,6,4, 8,9,7],
            [5,6,4, 8,9,7, 2,3,1],
            [8,9,7, 2,3,1, 5,6,4],
            
            [3,1,2, 6,4,5, 9,7,8],
            [6,4,5, 9,7,8, 3,1,2],
            [9,7,8, 3,1,2, 6,4,5]
        ]
        
        self.solution = self.shuffle_sudoku(base_grid)
        self.puzzle = self.hide_cells(self.solution, empty_cells)
        
        self.inputs = []
        
        board_col = ft.Column(spacing=2)
        
        for r in range(9):
            row_controls = []
            row_inputs = []
            for c in range(9):
                val = self.puzzle[r][c]
                if val != 0:
                    # Clue cell (readonly)
                    tf = ft.TextField(
                        value=str(val), 
                        read_only=True, 
                        width=35, 
                        height=35, 
                        text_align=ft.TextAlign.CENTER,
                        content_padding=5,
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_200)
                    )
                else:
                    # Empty cell (editable)
                    tf = ft.TextField(
                        value="", 
                        width=35, 
                        height=35, 
                        text_align=ft.TextAlign.CENTER,
                        content_padding=5,
                        keyboard_type=ft.KeyboardType.NUMBER,
                        max_length=1
                    )
                row_inputs.append(tf)
                row_controls.append(tf)
                
                # Add vertical separators for 3x3 blocks
                if c % 3 == 2 and c != 8:
                    row_controls.append(ft.Container(width=2, bgcolor=ft.colors.WHITE24))
                    
            self.inputs.append(row_inputs)
            board_col.controls.append(ft.Row(row_controls, spacing=2, alignment=ft.MainAxisAlignment.CENTER))
            
            # Add horizontal separators for 3x3 blocks
            if r % 3 == 2 and r != 8:
                board_col.controls.append(ft.Container(height=2, bgcolor=ft.colors.WHITE24))
                
        self.message = ft.Text("")
        
        self.controls = [
            ft.Text("Rompecabezas Sudoku", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Completa la cuadrícula de 9x9. No se pueden repetir números.", size=12),
            board_col,
            self.message,
            ft.Row([
                ft.ElevatedButton("Comprobar", on_click=self.check_solution),
                ft.ElevatedButton("Rendirse", color=ft.colors.RED, on_click=self.give_up)
            ], alignment=ft.MainAxisAlignment.CENTER)
        ]

    def shuffle_sudoku(self, grid):
        # A simple way to generate a new valid sudoku is to permute a base grid
        # 1. Swap numbers (e.g. swap all 1s and 5s)
        nums = list(range(1, 10))
        random.shuffle(nums)
        mapping = {i+1: nums[i] for i in range(9)}
        
        new_grid = [[mapping[val] for val in row] for row in grid]
        
        # 2. Swap rows within the same 3x3 band
        for band in range(3):
            r1, r2 = random.sample(range(3), 2)
            new_grid[band*3 + r1], new_grid[band*3 + r2] = new_grid[band*3 + r2], new_grid[band*3 + r1]
            
        # 3. Swap columns within the same 3x3 band
        for band in range(3):
            c1, c2 = random.sample(range(3), 2)
            for r in range(9):
                new_grid[r][band*3 + c1], new_grid[r][band*3 + c2] = new_grid[r][band*3 + c2], new_grid[r][band*3 + c1]
                
        return new_grid

    def hide_cells(self, grid, num_empty):
        puzzle = [row[:] for row in grid]
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        
        for r, c in cells[:num_empty]:
            puzzle[r][c] = 0
            
        return puzzle

    def check_solution(self, e):
        # Verify if all inputs match the solution
        is_correct = True
        is_full = True
        
        for r in range(9):
            for c in range(9):
                val = self.inputs[r][c].value
                if not val:
                    is_full = False
                    continue
                if not val.isdigit() or int(val) != self.solution[r][c]:
                    is_correct = False
                    self.inputs[r][c].border_color = ft.colors.RED
                else:
                    self.inputs[r][c].border_color = ft.colors.GREEN if self.puzzle[r][c] == 0 else None
                    
        self.update()
        
        if is_correct and is_full:
            self.message.value = "¡SUDOKU RESUELTO!"
            self.message.color = ft.colors.GREEN
            self.update()
            if self.on_win:
                self.on_win()
        elif not is_full:
            self.message.value = "Faltan casillas por rellenar."
            self.message.color = ft.colors.YELLOW
            self.update()
        else:
            self.message.value = "Hay errores en la cuadrícula."
            self.message.color = ft.colors.RED
            self.update()

    def give_up(self, e):
        if self.on_lose:
            self.on_lose()
