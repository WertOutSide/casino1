from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def is_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and is_allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        thumb_dir = os.path.join(upload_dir, 'thumbnails')
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, unique_filename)
        file.save(filepath)

        try:
            with Image.open(filepath) as img:
                if img.mode != 'RGB':
                    img.convert('RGB')
                
                img.thumbnail((300, 300))
                thumb_path = os.path.join(thumb_dir, unique_filename)
                img.save(thumb_path, 'JPEG', quality=85)
        except Exception as e:
            thumb_path = f"/static/uploads/thumbnails/{unique_filename}"
        
        image_path = f'/static/uploads/{unique_filename}'
        thumb_path = f'/static/uploads/thumbnails/{unique_filename}'
        
        return image_path, thumb_path
    return None, None
