from flask import Blueprint, request, jsonify, session
from utils.flask_helper import render_template
from .game import SlotGame
from models import db, User, DefaultGame, GameType
from flask_login import login_required, current_user
import pickle

slots_bp = Blueprint('slots', __name__)

@slots_bp.route('/')
@login_required
def play():
    return render_template('slots.html')

@slots_bp.route('/spin', methods=['POST'])
@login_required
def spin():
    try:
        bet_amount = float(request.json.get('bet', 10))
        
        if bet_amount <= 0:
            return jsonify({'error': 'Ставка должна быть больше нуля'}), 400
        
        if current_user.balance < bet_amount:
            return jsonify({'error': 'Недостаточно денег'}), 400
        
        current_user.balance -= bet_amount
        
        saved_game = DefaultGame.query.filter_by(user_id=current_user.id, game_id=GameType.SLOTS).first()

        if not saved_game:
            game = SlotGame()
        else:
            game = pickle.loads(saved_game.game_state)

        result = game.play(bet_amount)

        current_user.total_bets += bet_amount
        current_user.balance += result['win_amount']
        current_user.total_spins += 1
        current_user.total_wins += 1 if result['is_win'] else 0
        current_user.biggest_win = result['win_amount'] if result['win_amount'] > current_user.biggest_win else current_user.biggest_win

        if not saved_game:
            saved_game = pickle.dumps(game)
            new_game = DefaultGame(
                user_id=current_user.id,
                game_id=GameType.SLOTS,
                game_state=saved_game
                )
            db.session.add(new_game)
        else:
            saved_game.game_state = pickle.dumps(game)

        db.session.commit()
        
        response = {
            'success': True,
            'grid': result['grid'],
            'grid_symbols': result['grid_symbols'],
            'bet_amount': result['bet_amount'],
            'win_amount': result['win_amount'],
            'net_result': result['net_result'],
            'is_win': result['is_win'],
            'is_jackpot': result['is_jackpot'],
            'winning_lines': result['winning_lines'],
            'new_balance': current_user.balance
        }
        
        return jsonify(response)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
