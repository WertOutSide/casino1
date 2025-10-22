from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from .game import BlackjackGame, DeckAPI
from models import db, User, DefaultGame, GameType
from flask_login import login_required, current_user
import pickle
from sqlalchemy.orm.exc import NoResultFound

blackjack_bp = Blueprint('bj', __name__)

GAME_TYPE = GameType.BLACKJACK

def get_game_instance():
    try:
        saved_game = DefaultGame.query.filter_by(user_id=current_user.id, game_id=GAME_TYPE).one()
        game = pickle.loads(saved_game.game_state)
        if game.game_over:
            game = BlackjackGame(current_user.id, total_games=current_user.total_blackjack_games)
    except NoResultFound:
        game = BlackjackGame(current_user.id, total_games=current_user.total_blackjack_games)
    except Exception as e:
        print(f"Error loading game state: {e}")
        game = BlackjackGame(current_user.id, total_games=current_user.total_blackjack_games)

    return game

def save_game_instance(game):
    game_state_pickle = pickle.dumps(game)
    try:
        saved_game = DefaultGame.query.filter_by(user_id=current_user.id, game_id=GAME_TYPE).one()
        saved_game.game_state = game_state_pickle
    except NoResultFound:
        new_game = DefaultGame(
            user_id=current_user.id,
            game_id=GAME_TYPE,
            game_state=game_state_pickle
        )
        db.session.add(new_game)

    db.session.commit()

def clear_game_instance():
    DefaultGame.query.filter_by(user_id=current_user.id, game_id=GAME_TYPE).delete()
    db.session.commit()

@blackjack_bp.route('/api/start', methods=['POST'])
@login_required
def start_game_api():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet', 10))

        if bet_amount <= 0:
            return jsonify({'error': 'Ставка должна быть больше нуля'}), 400
        
        if current_user.balance < bet_amount:
            return jsonify({'error': 'Недостаточно денег'}), 400

        game = get_game_instance()

        result = game.start_game(bet_amount, current_user.total_blackjack_games)

        if result.get('game_over') is False and len(game.player_hand) == 2:
            current_user.balance -= bet_amount
            current_user.total_bets += bet_amount
            current_user.total_blackjack_games += 1

        save_game_instance(game)
        db.session.commit()

        result['new_balance'] = current_user.balance
        return jsonify({'success': True, 'game_state': result})

    except Exception as e:
        clear_game_instance()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@blackjack_bp.route('/api/hit', methods=['POST'])
@login_required
def hit_api():
    try:
        data = request.get_json()
        card_position = int(data.get('card_position', 0))
        
        game = get_game_instance()
        
        if game.game_over:
            return jsonify({'error': 'Игра окончена'}), 400
            
        result = game.hit(card_position)
        
        if result.get('game_over') and result.get('payout_multiplier') is None:
            current_user.total_spins += 1
            
        save_game_instance(game)
        db.session.commit()
        
        result['new_balance'] = current_user.balance
        return jsonify({'success': True, 'game_state': result})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@blackjack_bp.route('/api/stand', methods=['POST'])
@login_required
def stand_api():
    try:
        game = get_game_instance()
        
        if game.game_over:
            return jsonify({'error': 'Игра окончена'}), 400
            
        result = game.stand()
        
        payout_multiplier = result.get('payout_multiplier', 0)
        winnings = game.bet_amount * payout_multiplier
        
        current_user.balance += winnings
        current_user.total_spins += 1
        current_user.total_wins += 1 if payout_multiplier > 1 else 0
        current_user.biggest_win = winnings if winnings > current_user.biggest_win else current_user.biggest_win
        
        save_game_instance(game)
        db.session.commit()
        
        result['new_balance'] = current_user.balance
        return jsonify({'success': True, 'game_state': result})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@blackjack_bp.route('/api/state', methods=['GET'])
@login_required
def get_state_api():
    try:
        game = get_game_instance()
        result = game.get_state()
        result['new_balance'] = current_user.balance
        return jsonify({'success': True, 'game_state': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blackjack_bp.route('/')
@login_required
def index():
    return render_template('index_blackjack.html')

@blackjack_bp.route('/blackjack')
@login_required
def blackjack():
    return render_template('blackjack.html')

@blackjack_bp.route('/new_game')
@login_required
def new_game():
    clear_game_instance()
    return redirect(url_for('bj.blackjack'))

