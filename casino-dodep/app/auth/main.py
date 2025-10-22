from flask import Blueprint, redirect, url_for, request, flash, jsonify
from utils.flask_helper import render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        
        user = User.query.filter_by(username = username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Успешно вошел!')
            return redirect(url_for('index'))
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует')
            return render_template('registration.html')
        
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            name=username
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('registration.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
