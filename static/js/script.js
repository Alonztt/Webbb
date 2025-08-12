// Глобальные переменные
let currentDeleteFilename = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeFileInput();
    initializeDragAndDrop();
    initializeImageCards();
});

// Инициализация поля ввода файла
function initializeFileInput() {
    const fileInput = document.getElementById('file');
    const fileLabel = document.querySelector('.file-label');
    const fileText = fileLabel.querySelector('.file-text');
    const fileInfo = fileLabel.querySelector('.file-info');

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Обновляем текст
            fileText.textContent = file.name;
            fileInfo.textContent = `${formatFileSize(file.size)} • ${file.type.split('/')[1].toUpperCase()}`;
            
            // Добавляем класс для визуального изменения
            fileLabel.classList.add('file-selected');
            
            // Предпросмотр изображения
            showImagePreview(file);
        }
    });
}

// Инициализация drag & drop
function initializeDragAndDrop() {
    const fileLabel = document.querySelector('.file-label');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileLabel.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        fileLabel.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        fileLabel.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        fileLabel.classList.add('drag-over');
    }
    
    function unhighlight(e) {
        fileLabel.classList.remove('drag-over');
    }
    
    fileLabel.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                // Устанавливаем файл в input
                const fileInput = document.getElementById('file');
                fileInput.files = files;
                
                // Запускаем событие change
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            } else {
                showNotification('Пожалуйста, выберите изображение', 'error');
            }
        }
    }
}

// Инициализация карточек изображений
function initializeImageCards() {
    const imageCards = document.querySelectorAll('.image-card');
    
    imageCards.forEach(card => {
        // Добавляем hover эффекты
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        // Добавляем клик для увеличения
        const image = card.querySelector('.image-thumb');
        if (image) {
            image.addEventListener('click', function() {
                openImageModal(this.src);
            });
        }
    });
}

// Показ предпросмотра изображения
function showImagePreview(file) {
    const reader = new FileReader();
    const fileLabel = document.querySelector('.file-label');
    
    reader.onload = function(e) {
        // Очищаем содержимое
        fileLabel.innerHTML = '';
        
        // Создаем предпросмотр
        const preview = document.createElement('img');
        preview.src = e.target.result;
        preview.style.width = '100%';
        preview.style.height = '100%';
        preview.style.objectFit = 'cover';
        preview.style.borderRadius = '15px';
        
        fileLabel.appendChild(preview);
        
        // Добавляем информацию о файле
        const info = document.createElement('div');
        info.style.position = 'absolute';
        info.style.bottom = '10px';
        info.style.left = '10px';
        info.style.right = '10px';
        info.style.background = 'rgba(0,0,0,0.7)';
        info.style.color = 'white';
        info.style.padding = '8px';
        info.style.borderRadius = '8px';
        info.style.fontSize = '12px';
        info.textContent = `${file.name} (${formatFileSize(file.size)})`;
        
        fileLabel.style.position = 'relative';
        fileLabel.appendChild(info);
    };
    
    reader.readAsDataURL(file);
}

// Открытие модального окна с изображением
function openImageModal(imageSrc) {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
        cursor: pointer;
    `;
    
    const img = document.createElement('img');
    img.src = imageSrc;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
        border-radius: 10px;
    `;
    
    modal.appendChild(img);
    document.body.appendChild(modal);
    
    // Закрытие по клику
    modal.addEventListener('click', function() {
        document.body.removeChild(modal);
    });
}

// Удаление изображения
function deleteImage(filename) {
    currentDeleteFilename = filename;
    const modal = document.getElementById('deleteModal');
    modal.style.display = 'block';
}

// Подтверждение удаления
function confirmDelete() {
    if (currentDeleteFilename) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/delete/${currentDeleteFilename}`;
        document.body.appendChild(form);
        form.submit();
    }
    closeDeleteModal();
}

// Закрытие модального окна удаления
function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.style.display = 'none';
    currentDeleteFilename = null;
}

// Закрытие модального окна по клику вне его
window.addEventListener('click', function(event) {
    const modal = document.getElementById('deleteModal');
    if (event.target === modal) {
        closeDeleteModal();
    }
});

// Форматирование размера файла
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Показ уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 3000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    // Цвета для разных типов уведомлений
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    notification.style.background = colors[type] || colors.info;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Автоматическое скрытие
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Добавление CSS для drag & drop
const style = document.createElement('style');
style.textContent = `
    .file-label.drag-over {
        border-color: #764ba2 !important;
        background: rgba(118, 75, 162, 0.1) !important;
        transform: scale(1.02);
    }
    
    .file-label.file-selected {
        border-color: #28a745;
        background: rgba(40, 167, 69, 0.05);
    }
    
    .image-modal img {
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    .notification {
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
`;
document.head.appendChild(style);

// Обработка ошибок
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showNotification('Произошла ошибка. Попробуйте обновить страницу.', 'error');
});

// Обработка unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('Произошла ошибка при загрузке данных.', 'error');
});