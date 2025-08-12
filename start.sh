#!/bin/bash

# Скрипт запуска фотохостинга
# Автор: AI Assistant
# Версия: 1.0

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 не найден. Установите Python 3.7+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_status "Найден Python $PYTHON_VERSION"
}

# Проверка наличия pip
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 не найден. Установите pip"
        exit 1
    fi
    print_status "pip3 найден"
}

# Создание виртуального окружения
create_venv() {
    if [ ! -d "venv" ]; then
        print_status "Создание виртуального окружения..."
        python3 -m venv venv
        print_success "Виртуальное окружение создано"
    else
        print_status "Виртуальное окружение уже существует"
    fi
}

# Активация виртуального окружения
activate_venv() {
    print_status "Активация виртуального окружения..."
    source venv/bin/activate
    print_success "Виртуальное окружение активировано"
}

# Установка зависимостей
install_dependencies() {
    print_status "Установка зависимостей..."
    pip install -r requirements.txt
    print_success "Зависимости установлены"
}

# Создание папки для загрузок
create_upload_folder() {
    if [ ! -d "uploads" ]; then
        print_status "Создание папки для загрузок..."
        mkdir -p uploads
        print_success "Папка uploads создана"
    fi
}

# Запуск приложения
start_app() {
    print_status "Запуск фотохостинга..."
    print_success "Приложение доступно по адресу: http://localhost:5000"
    print_status "Для остановки нажмите Ctrl+C"
    
    python app.py
}

# Основная функция
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    Запуск фотохостинга${NC}"
    echo -e "${BLUE}================================${NC}"
    
    # Проверки
    check_python
    check_pip
    
    # Подготовка окружения
    create_venv
    activate_venv
    install_dependencies
    create_upload_folder
    
    # Запуск
    start_app
}

# Обработка ошибок
trap 'print_error "Произошла ошибка. Проверьте логи."' ERR

# Запуск основной функции
main "$@"