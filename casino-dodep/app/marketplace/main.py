from flask import Blueprint, request, render_template, jsonify, current_app
from models import db, User, Item, Inventory
from flask_login import login_required, current_user
from datetime import datetime
from .items import save_image

MAX_FILE_SIZE = 3 * 512 * 512

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/')
@login_required
def marketplace():
    items_page = int(request.args.get('items_page', 1))
    items = Item.query.filter_by(is_sold=False).order_by(Item.created_at.desc()).paginate(page=items_page, per_page=8, error_out=False)
    user_inventory = Inventory.query.filter_by(user_id=current_user.id).order_by(Inventory.acquired_at.desc()).all()
    return render_template('marketplace.html', 
                         items=items.items, 
                         user_inventory=user_inventory,
                         user_balance=current_user.balance,
                         items_pagination=items)


@marketplace_bp.route('/list_item', methods=['POST'])
@login_required
def list_item():
    try:
        name = request.form.get('name', None)
        description = request.form.get('description', None)
        price = float(request.form.get('price', 0))
        if request.files:
            image_file = request.files.get('image')
        else:
            image_file = None

        if not name or not price:
            return jsonify({'error': 'Имя и цена не могу быть пустыми'}), 400
        
        if price <= 0:
            return jsonify({'error': 'Цена не может быть меньше нуля'}), 400
        
        image_url = None
        thumbnail_url = None
        if image_file and image_file.filename:
            if len(image_file.read()) > MAX_FILE_SIZE:
                return jsonify({'error': 'Файл слишком большой'}), 400
            image_file.seek(0)
            image_url, thumbnail_url = save_image(image_file)
            if not image_url:
                return jsonify({'error': 'Некорректный тип файла. Разрешены следующие форматы: PNG, JPG, JPEG, GIF, WEBP'}), 400

        item = Item(
                name=name,
                description=description,
                price=price,
                seller_id=current_user.id,
                image_url=thumbnail_url or image_url or '/static/images/default-item.png'
            )

        db.session.add(item)
        db.session.commit()

        return jsonify({
                'message': 'Лот успешно выставлен на продажу',
                'item': {
                    'id': item.id,
                    'name': item.name,
                    'price': item.price,
                    'image_url': item.image_url
                }
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@marketplace_bp.route('/buy_item/<int:item_id>', methods=['POST'])
@login_required
def buy_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)

        if item.is_sold:
            return jsonify({'error': 'Товар уже купили'}), 400

        if current_user.total_bets < 100:
            return jsonify({'error': 'Нельзя тратить бонусные денги на лоты'})
        
        if item.seller_id == current_user.id:
            return jsonify({'error': 'Нельзя купить свой лот'}), 400

        if current_user.balance < item.price:
            return jsonify({'error': 'Недостаточно денег'}), 400
        
        current_user.balance -= item.price
        seller = User.query.get(item.seller_id)
        seller.balance += item.price

        inventory_item = Inventory(user_id=current_user.id, item_id=item.id)
        db.session.add(inventory_item)
        item.is_sold = True

        db.session.commit()

        return jsonify({
            'message': 'Лот успешно куплен',
            'new_balance': current_user.balance,
            'item_name': item.name
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@marketplace_bp.route('/inventory')
@login_required
def get_inventory():
    inventory = Inventory.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': inv_item.id,
        'item_id': inv_item.item.id,
        'item_name': inv_item.item.name,
        'item_description': inv_item.item.description,
        'original_price': inv_item.item.price,
        'acquired_at': inv_item.acquired_at.isoformat(),
        'image_url': inv_item.item.image_url
    } for inv_item in inventory])

@marketplace_bp.route('/my_listings')
@login_required
def my_listings():
    items = Item.query.filter_by(seller_id=current_user.id).all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': item.price,
        'created_at': item.created_at.isoformat(),
        'image_url': item.image_url,
        'is_sold': item.is_sold
    } for item in items])

@marketplace_bp.route('/remove_listing/<int:item_id>', methods=['DELETE'])
@login_required
def remove_listing(item_id):
    try:
        item = Item.query.get_or_404(item_id)

        if item.is_sold:
            return jsonify({'error': 'Вы не можете удалить уже проданный лот'})

        if item.seller_id != current_user.id:
            return jsonify({'error': 'Необходимо авторизоваться для удаления лота'}), 403
        
        db.session.delete(item)
        db.session.commit()

        return jsonify({'message': 'Лот успешно удален'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500