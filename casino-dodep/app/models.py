from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(80))
    balance = db.Column(db.Float, default=100.0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    items_for_sale = db.relationship('Item', backref='seller', lazy=True)
    inventory = db.relationship('Inventory', backref='user', lazy=True)
    game = db.relationship('DefaultGame', backref='game', lazy=True)

    total_bets = db.Column(db.Float, default=0.0)
    total_spins = db.Column(db.Integer, default=0)
    total_wins = db.Column(db.Integer, default=0)
    biggest_win = db.Column(db.Float, default=0.0)

    total_blackjack_games = db.Column(db.Integer, default=0)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_sold = db.Column(db.Boolean, default=False)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    acquired_at = db.Column(db.DateTime, default=datetime.now)

    item = db.relationship('Item', backref='inventory_records')

class GameType(enum.IntEnum):
    SLOTS = 1
    ROULETTE = 2
    BLACKJACK = 3

class DefaultGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Enum(GameType), nullable=False)
    game_state = db.Column(db.LargeBinary)

class Bjackgame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deck = db.Column(db.Text)
    player_hand = db.Column(db.Text)
    dealer_hand = db.Column(db.Text)
    bet = db.Column(db.Integer)
    game_state = db.Column(db.Text)
    created_at  = db.Column(db.Text)
