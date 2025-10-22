import random
import hashlib
import json
from datetime import datetime
from models import db, User, Bjackgame
class DeckAPI:
    @staticmethod
    def generate_deck(user_id, total_games=0):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        seed = int(hashlib.md5(str(user_id).encode()).hexdigest()[:8], 16) + total_games + 1
        random.seed(seed)
        
        deck = [f'{rank} of {suit}' for suit in suits for rank in ranks]
        
        for _ in range(3):
            random.shuffle(deck)
        
        return deck
    
    @staticmethod
    def calculate_score(hand):
        score = 0
        aces = 0
        
        for card in hand:
            rank = card.split()[0]
            
            if rank in ['Q', 'K', 'J']:
                score += 10
            elif rank == 'A' and aces == 0:
                score += 11  
                aces += 1
            elif rank == 'A' and aces != 0:
                score += (11 * aces) % 10
            else:
                score += int(rank)
        
        return score
    
    @staticmethod
    def deal_card(deck, hand, position=0):
        # position for massasignement
        if 0 <= position < len(deck):
            card = deck.pop(position)
        else:
            card = deck.pop(0)
        hand.append(card)
        return card

class BlackjackGame:
    def __init__(self, user_id, bet_amount=100, total_bets=0):
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.deck = DeckAPI.generate_deck(user_id, total_bets)
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0
        self.game_over = False
        self.message = ""
        
    def deal_initial(self):
        self.player_hand = [self.deck.pop(0), self.deck.pop(0)]
        self.dealer_hand = [self.deck.pop(0), self.deck.pop(0)]
        
    def hit(self, card_position=0):
        if not self.game_over:
            DeckAPI.deal_card(self.deck, self.player_hand, card_position)
            self.player_score = DeckAPI.calculate_score(self.player_hand)
            
            if self.player_score > 21:
                self.game_over = True
                self.message = "You lose"
                return False
            return True
        return False
    
    def stand(self):
        if not self.game_over:
            self.game_over = True
            self.dealer_score = DeckAPI.calculate_score(self.dealer_hand)
            
            while self.dealer_score < 17:
                DeckAPI.deal_card(self.deck, self.dealer_hand)
                self.dealer_score = DeckAPI.calculate_score(self.dealer_hand)
            
            if len(self.dealer_hand) == 2 and self.dealer_score == 21:
                self.message = "Dealer Blackjack - You lose."
                return -1
            
            if self.dealer_score > 21:
                self.message = "You win"
                return 1
            elif self.dealer_score > self.player_score:
                self.message = "Dealer wins"
                return -1
            elif self.dealer_score < self.player_score:
                self.message = "You win"
                return 1
            else:
                self.message = "Tie"
                return 0
        return 0


def get_user_balance(user_id):
    user = User.query.get(user_id)
    return user.balance if user else 0

def update_user_balance(user_id, new_balance):
    user = User.query.get(user_id)
    if user:
        user.balance = new_balance
        db.session.commit()

def save_game_state(game):
    game_state_data = {
        'player_score': game.player_score,
        'dealer_score': game.dealer_score,
        'game_over': game.game_over,
        'message': game.message
    }
    
    user = User.query.get(game.user_id)
    if user:
        user.total_blackjack_games += 1
    
    new_game = Bjackgame(
        user_id=game.user_id,
        deck=json.dumps(game.deck),
        player_hand=json.dumps(game.player_hand),
        dealer_hand=json.dumps(game.dealer_hand),
        bet=game.bet_amount,
        game_state=json.dumps(game_state_data),
        created_at=datetime.now().isoformat()
    )
    
    db.session.add(new_game)
    db.session.commit()

def load_game_state(user_id):
    game_data = Bjackgame.query.filter_by(user_id=user_id).order_by(Bjackgame.id.desc()).first()
    
    if not game_data:
        return None
    

    game = BlackjackGame(user_id, game_data.bet)
    game.deck = json.loads(game_data.deck)
    game.player_hand = json.loads(game_data.player_hand)
    game.dealer_hand = json.loads(game_data.dealer_hand)
    
    state = json.loads(game_data.game_state)
    game.player_score = state['player_score']
    game.dealer_score = state['dealer_score']
    game.game_over = state['game_over']
    game.message = state['message']
    
    return game