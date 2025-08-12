# Фотохостинг (FastAPI)

Минималистичный фотохостинг: загрузка изображений, автоматическая генерация превью (`sm`, `md`, `lg`), список, выдача и удаление. Фронтенд — одна страница со стандартным drag&drop.

## Запуск локально

Требуется Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте в браузере: `http://localhost:8000/`

Документация API: `http://localhost:8000/docs`

## Docker

```bash
docker build -t photohosting .
docker run --rm -it -p 8000:8000 -v $(pwd)/uploads:/workspace/uploads -v $(pwd)/data:/workspace/data photohosting
```

## API

- `POST /api/upload` — загрузка одного или нескольких файлов (multipart form field: `files`)
- `GET /api/images` — список последних изображений
- `GET /i/{uuid}/{variant}` — выдача файла (`orig|sm|md|lg`)
- `DELETE /api/images/{uuid}` — удалить изображение

## Хранение

- База: SQLite в `data/db.sqlite3`
- Файлы: в каталоге `uploads/`:
  - Оригиналы: `uploads/original/{uuid}.{ext}`
  - Превью: `uploads/{sm,md,lg}/{uuid}.jpg`