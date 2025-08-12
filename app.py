import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Создаем папку для загрузок если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Разрешенные форматы файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_info(filename):
    """Получает информацию об изображении"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                file_size = os.path.getsize(filepath)
                return {
                    'filename': filename,
                    'width': width,
                    'height': height,
                    'size': file_size,
                    'format': img.format,
                    'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            return None
    return None

@app.route('/')
def index():
    """Главная страница с галереей изображений"""
    images = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename):
                info = get_image_info(filename)
                if info:
                    images.append(info)
    
    # Сортируем по времени загрузки (новые сначала)
    images.sort(key=lambda x: x['upload_time'], reverse=True)
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка файла"""
    if 'file' not in request.files:
        flash('Файл не выбран', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Сохраняем файл
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Создаем миниатюру
        try:
            with Image.open(filepath) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Создаем миниатюру
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], f"thumb_{unique_filename}")
                img.save(thumbnail_path, 'JPEG', quality=85)
        except Exception as e:
            print(f"Ошибка создания миниатюры: {e}")
        
        flash('Файл успешно загружен!', 'success')
        return redirect(url_for('index'))
    
    flash('Неподдерживаемый формат файла', 'error')
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Отображение загруженного файла"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Удаление файла"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], f"thumb_{filename}")
    
    # Удаляем основной файл
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Удаляем миниатюру если есть
    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)
    
    flash('Файл успешно удален!', 'success')
    return redirect(url_for('index'))

@app.route('/api/images')
def api_images():
    """API для получения списка изображений"""
    images = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename) and not filename.startswith('thumb_'):
                info = get_image_info(filename)
                if info:
                    images.append(info)
    
    images.sort(key=lambda x: x['upload_time'], reverse=True)
    return jsonify(images)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)