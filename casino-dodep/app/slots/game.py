import random
from enum import Enum

class SlotSymbol(Enum):
    # symbol + multiplier + name
    CHERRY = ("🍒", 2, "вишенка")
    LEMON = ("🍋", 3, "лимон")
    ORANGE = ("🍊", 4, "апельсин")
    PLUM = ("🍑", 5, "слива")
    GRAPES = ("🍇", 7, "виноград")
    WATERMELON = ("🍉", 10, "арбуз")
    SEVEN = ("7️⃣", 20, "блатная семерка")
    DOGEP = ("🐕", 50, "золотая собака") 
    GOLDEN_MAKAKA = ("🐵", 100, "золотая макака")

class SlotGame:
    def __init__(self):
        self.reels = 3 
        self.rows = 3 
        self.balance = 0
        self.bet_amount = 0
        self.symbols = self._initialize_symbols()
        self.paylines = self._initialize_paylines()
        self.last_spin = None
        self.last_win = 0
        
    def _initialize_symbols(self):
        return [
            (SlotSymbol.CHERRY, 15),
            (SlotSymbol.LEMON, 14),
            (SlotSymbol.ORANGE, 13),
            (SlotSymbol.PLUM, 12),
            (SlotSymbol.GRAPES, 10),
            (SlotSymbol.WATERMELON, 8),
            (SlotSymbol.SEVEN, 5),
            (SlotSymbol.DOGEP, 2),
            (SlotSymbol.GOLDEN_MAKAKA, 1)
        ]
    
    def _initialize_paylines(self):
        return [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(2, 0), (1, 1), (0, 2)]
        ]
    
    def spin_reels(self):
        grid = []
        for row in range(self.rows):
            reel_row = []
            for reel in range(self.reels):
                symbols, weights = zip(*self.symbols)
                symbol = random.choices(symbols, weights=weights)[0]
                reel_row.append(symbol)
            grid.append(reel_row)
        return grid
    
    def calculate_win(self, grid, bet_amount):
        total_win = 0
        winning_lines = []
        
        for line_num, payline in enumerate(self.paylines):
            line_symbols = [grid[row][col] for row, col in payline]
            
            first_symbol = line_symbols[0]
            if all(symbol == first_symbol for symbol in line_symbols):
                win_multiplier = first_symbol.value[1]
                line_win = bet_amount * win_multiplier
                total_win += line_win

                line_names = ['Верхний ряд', 'Средний ряд', 'Нижний ряд', 'Диагональ ↘', 'Диагональ ↗']
                
                winning_lines.append({
                    'line_number': line_num,
                    'line_name': line_names[line_num],
                    'symbol': first_symbol.value[0],
                    'symbol_name': first_symbol.value[2],
                    'multiplier': win_multiplier,
                    'win_amount': line_win,
                    'positions': payline
                })
        
        return total_win, winning_lines
    
    def play(self, bet_amount):
        self.bet_amount = bet_amount
        grid = self.spin_reels()
        win_amount, winning_lines = self.calculate_win(grid, bet_amount)
        
        result = {
            'grid': [[symbol.value[0] for symbol in row] for row in grid],
            'grid_symbols': [[symbol.value[2] for symbol in row] for row in grid],
            'bet_amount': bet_amount,
            'win_amount': win_amount,
            'winning_lines': winning_lines,
            'net_result': win_amount - bet_amount,
            'is_win': win_amount > 0,
            'is_jackpot': any(line.get('symbol_name') == 'золотая макака' for line in winning_lines)
        }
        
        self.last_spin = result
        self.last_win = win_amount
        
        return result
