import random

class RouletteGame:
    RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    def __init__(self):
        self.last_results = []
    
    def spin(self):
        result = random.randint(0, 36)
        self.last_results.append(result)
        if len(self.last_results) > 10:
            self.last_results.pop(0)
        return result
    
    def get_color(self, number):
        if number == 0:
            return 'green'
        elif number in self.RED_NUMBERS:
            return 'red'
        else:
            return 'black'
    
    def calculate_payout(self, bet_type, bet_value, winning_number, bet_amount):
        winning_color = self.get_color(winning_number)
        
        if bet_type == 'straight':
            if int(bet_value) == winning_number:
                return (True, bet_amount * 36, 36)
        
        elif bet_type == 'color':
            if bet_value == winning_color:
                return (True, bet_amount * 2, 2)
        
        elif bet_type == 'even_odd':
            if winning_number == 0:
                return (False, 0, 0)
            is_even = winning_number % 2 == 0
            if (bet_value == 'even' and is_even) or (bet_value == 'odd' and not is_even):
                return (True, bet_amount * 2, 2)
        
        elif bet_type == 'low_high':
            if winning_number == 0:
                return (False, 0, 0)
            if (bet_value == 'low' and 1 <= winning_number <= 18) or \
               (bet_value == 'high' and 19 <= winning_number <= 36):
                return (True, bet_amount * 2, 2)
        
        elif bet_type == 'dozen':
            if winning_number == 0:
                return (False, 0, 0)
            dozen = (winning_number - 1) // 12 + 1
            if int(bet_value) == dozen:
                return (True, bet_amount * 3, 3)
        
        elif bet_type == 'column':
            if winning_number == 0:
                return (False, 0, 0)
            column = ((winning_number - 1) % 3) + 1
            if int(bet_value) == column:
                return (True, bet_amount * 3, 3)
        
        return (False, 0, 0)
    
    def get_last_results(self, count=10):
        return self.last_results[-count:]

