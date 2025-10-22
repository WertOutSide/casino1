from flask import Blueprint, request, jsonify
from utils.flask_helper import render_template
from .game import RouletteGame
from models import db, User, DefaultGame, GameType
from flask_login import login_required, current_user
import pickle

roulette_bp = Blueprint('roulette', __name__)

@roulette_bp.route('/')
@login_required
def play():
    return render_template('roulette.html')

@roulette_bp.route('/spin', methods=['POST'])
@login_required
def spin():
    try:
        bets = request.json.get('bets', [])
        
        if not bets:
            return jsonify({'error': 'Нет активных ставок'}), 400
        
        total_bet = sum(bet['amount'] for bet in bets)
        
        if total_bet < 0:
            return jsonify({'error': 'Ставка должна быть больше нуля'}), 400
        
        if current_user.balance < total_bet:
            return jsonify({'error': 'Недостаточно денег'}), 400
        
        current_user.balance -= total_bet

        saved_game = DefaultGame.query.filter_by(user_id=current_user.id, game_id=GameType.ROULETTE).first()

        if not saved_game:
            game = RouletteGame()
        else:
            game = pickle.loads(saved_game.game_state)
        
        winning_number = game.spin()
        winning_color = game.get_color(winning_number)
        
        total_payout = 0
        bet_results = []
        
        for bet in bets:
            is_win, payout, multiplier = game.calculate_payout(
                bet['type'],
                bet['value'],
                winning_number,
                bet['amount']
            )
            
            bet_results.append({
                'type': bet['type'],
                'value': bet['value'],
                'amount': bet['amount'],
                'is_win': is_win,
                'payout': payout,
                'multiplier': multiplier
            })
            
            total_payout += payout

        if not saved_game:
            saved_game = pickle.dumps(game)
            new_game = DefaultGame(
                user_id=current_user.id,
                game_id=GameType.ROULETTE,
                game_state=saved_game
                )
            db.session.add(new_game)
        else:
            saved_game.game_state = pickle.dumps(game)

        
        current_user.total_bets += total_bet
        current_user.balance += total_payout
        current_user.total_spins += 1
        current_user.total_wins += 1 if is_win else 0
        current_user.biggest_win = payout if payout > current_user.biggest_win else current_user.biggest_win

        
        db.session.commit()
        
        response = {
            'success': True,
            'winning_number': winning_number,
            'winning_color': winning_color,
            'total_bet': total_bet,
            'total_payout': total_payout,
            'net_result': total_payout - total_bet,
            'bet_results': bet_results,
            'new_balance': current_user.balance,
            'last_results': game.get_last_results()
        }
        
        return jsonify(response)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@roulette_bp.route('/history')
@login_required
def get_history():
    saved_game = DefaultGame.query.filter_by(user_id=current_user.id, game_id=GameType.ROULETTE).first()
    if saved_game:
        game = pickle.loads(saved_game.game_state)
        return jsonify({
            'history': game.get_last_results()
        })
    return jsonify({'history': []})

