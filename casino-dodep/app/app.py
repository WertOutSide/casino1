from flask import Flask, send_from_directory, current_app
from utils.flask_helper import render_template
import os
from models import db, User, Item, Inventory
from auth import auth_bp, login_manager
from marketplace import marketplace_bp
from slots import slots_bp
from roulette import roulette_bp
from profile import profile_bp
from blackjack import blackjack_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://casino_user:casino_pass@localhost:5432/casino_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(marketplace_bp, url_prefix='/marketplace')
    app.register_blueprint(slots_bp, url_prefix='/slots')
    app.register_blueprint(roulette_bp, url_prefix='/roulette')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(blackjack_bp,url_prefix='/bj')


    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/static/<path:path>')
    def static_files(path):
        return send_from_directory('static', path)

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    
    app.run('0.0.0.0', debug=True)
