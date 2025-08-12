#!/usr/bin/env python3
"""
Production запуск фотохостинга
"""

import os
from app import app

if __name__ == '__main__':
    # Получаем настройки из переменных окружения
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Запуск фотохостинга на {host}:{port}")
    print(f"🔧 Режим отладки: {'Включен' if debug else 'Отключен'}")
    print(f"📁 Папка загрузок: {app.config['UPLOAD_FOLDER']}")
    print(f"📏 Максимальный размер файла: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.1f} MB")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )