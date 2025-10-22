import random
import hashlib
import json
from models import db, User, Bjackgame

class DeckAPI:
    
    @staticmethod
    def generate_deck(user_id, total_games=0):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        seed = int(hashlib.md5(str(user_id).encode()).hexdigest()[:8], 16) + total_games + 1
        random.seed(seed)
        
        deck = [f'{rank} {suit}' for suit in suits for rank in ranks]
        
        for _ in range(3):
            random.shuffle(deck)
        
        return deck
    
    @staticmethod
    def calculate_score(hand):
        score = 0
        aces = 0
        
        for card_str in hand:
            rank = card_str.split()[0]
            
            if rank in ['Q', 'K', 'J']:
                score += 10
            elif rank == 'A':
                aces += 1
                score += 11
            else:
                score += int(rank)
        
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
            
        return score

class BlackjackGame:
    def __init__(self, user_id, total_games=0):
        self.user_id = user_id
        self.deck = DeckAPI.generate_deck(user_id, total_games)
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0
        self.game_over = False
        self.message = ""
        self.bet_amount = 0

    def _deal_card(self, hand, position=0):
        if 0 <= position < len(self.deck):
            card = self.deck.pop(position)
        else:
            card = self.deck.pop(0)
        hand.append(card)
        return card

    def start_game(self, bet_amount, total_games):
        self.bet_amount = bet_amount
        self.deck = DeckAPI.generate_deck(self.user_id, total_games=total_games)
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.message = ""
        
        self._deal_card(self.player_hand)
        self._deal_card(self.dealer_hand)
        self._deal_card(self.player_hand)
        self._deal_card(self.dealer_hand)
        
        self.player_score = DeckAPI.calculate_score(self.player_hand)
        self.dealer_score = DeckAPI.calculate_score(self.dealer_hand)
        
        if self.player_score == 21:
            self.stand()
        
        return self.get_state()

    def hit(self, card_position=0):
        if self.game_over:
            return self.get_state()
            
        self._deal_card(self.player_hand, card_position)
        self.player_score = DeckAPI.calculate_score(self.player_hand)
        
        if self.player_score > 21:
            self.game_over = True
            self.message = "Перебор! Вы проиграли."
            
        return self.get_state()

    def stand(self):
        if self.game_over:
            return self.get_state()
            
        self.game_over = True
        
        while self.dealer_score < 17:
            self._deal_card(self.dealer_hand)
            self.dealer_score = DeckAPI.calculate_score(self.dealer_hand)
        
        payout_multiplier = 0
        if self.player_score > 21:
            payout_multiplier = 0.0
        elif self.dealer_score > 21:
            self.message = "Дилер перебрал. Вы выиграли!"
            payout_multiplier = 2.0
        elif self.player_score == 21 and len(self.player_hand) == 2 and len(self.dealer_hand) > 2:
             self.message = "Блэкджек! Вы выиграли!"
             payout_multiplier = 2.5 
        elif self.player_score > self.dealer_score:
            self.message = "Вы выиграли!"
            payout_multiplier = 2.0
        elif self.player_score < self.dealer_score:
            self.message = "Дилер выиграл. Вы проиграли."
            payout_multiplier = 0.0
        else:
            self.message = "Ничья. Ставка возвращена."
            payout_multiplier = 1.0
            
        return self.get_state(payout_multiplier)

    def get_state(self, payout_multiplier=None):
        dealer_hand_display = self.dealer_hand
        dealer_score_display = self.dealer_score
        
        if not self.game_over and len(self.dealer_hand) > 1:
            dealer_hand_display = [self.dealer_hand[0], '???']
            dealer_score_display = DeckAPI.calculate_score([self.dealer_hand[0]])
            
        return {
            'player_hand': self.player_hand,
            'dealer_hand': dealer_hand_display,
            'player_score': self.player_score,
            'dealer_score': dealer_score_display,
            'game_over': self.game_over,
            'message': self.message,
            'bet_amount': self.bet_amount,
            'payout_multiplier': payout_multiplier,
        }

