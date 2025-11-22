# LeetCode Tracker 🐍📈

[![Stars](https://img.shields.io/github/stars/daniil-novel/leetcode-tracker?style=social)](https://github.com/daniil-novel/leetcode-tracker)
[![License](https://img.shields.io/github/license/daniil-novel/leetcode-tracker)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-brightgreen)](https://fastapi.tiangolo.com/)

## Описание

Небольшой веб-сервис для **геймифицированного трекинга прогресса на LeetCode**:

- Форма добавления решённых задач с XP (Easy=1, Medium=3, Hard=5).
- Сохранение в БД (SQLite по умолчанию).
- Интерактивные графики (Chart.js):
  - Задач в день.
  - XP в день.
  - Кумулятивный XP.
  - Streak по дням.
- Таблица последних задач.
- API для интеграций (`/docs`).

![Demo](https://via.placeholder.com/800x400?text=LeetCode+Tracker+Demo) <!-- Замените на реальный скриншот -->

## 🛠 Технологии

- **Backend**: FastAPI, SQLAlchemy, Alembic (миграции).
- **Frontend**: Jinja2, HTMX, Alpine.js, Chart.js, Tailwind CSS.
- **Пакетный менеджер**: [uv](https://astral.sh/uv) (быстрее pip/poetry).
- **БД**: SQLite (default) / PostgreSQL.
- **Деплой**: Docker-ready.

## 📦 Быстрый старт

### 1. Установка uv (если нет)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# или pip install uv
uv --version
```

### 2. Клонируйте и установите

```bash
git clone https://github.com/daniil-novel/leetcode-tracker.git
cd leetcode_tracker-tracker  # или ваш форк
uv sync  # Установит deps + venv
```

### 3. Запуск

```bash
uv run uvicorn leetcode_tracker.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте:
- [http://localhost:8000](http://localhost:8000) — Дашборд.
- [http://localhost:8000/docs](http://localhost:8000/docs) — Swagger UI.

БД `leetcode.db` создастся автоматически.

## 🔧 Конфигурация

### База данных

**SQLite (default)**: Нет настроек.

**PostgreSQL**:
```bash
# Создайте БД, затем:
set DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/leetcode  # Windows
# или export DATABASE_URL=... (Linux/Mac)
uv run uvicorn ...
```

### Кастомизация XP
- Easy: 1 XP
- Medium: 3 XP
- Hard: 5 XP

Расширьте в `main.py` → `/api/stats/daily`.

## 📁 Структура проекта

```
leetcode_tracker/
├── pyproject.toml      # Deps (uv)
├── uv.lock            # Lockfile
├── leetcode_tracker/
│   ├── __init__.py
│   ├── main.py        # FastAPI app
│   ├── models.py      # SQLAlchemy
│   ├── schemas.py     # Pydantic
│   ├── database.py    # DB engine
│   ├── static/        # CSS/JS (Tailwind, Chart.js)
│   └── templates/     # Jinja2 HTML
└── README.md
```

## 🚀 Деплой

### Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim
RUN pip install uv
COPY . .
RUN uv sync --frozen
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "leetcode_tracker.main:app", "--host", "0.0.0.0"]
```

```bash
docker build -t leetcode-tracker .
docker run -p 8000:8000 leetcode-tracker
```

### Railway / Render / Vercel
- `DATABASE_URL` в secrets.
- `uv sync && uv run uvicorn ...`.

## 📊 Импорт данных

Для Excel/CSV напишите скрипт `scripts/import.py`:

```python
# Пример: pd.read_csv('Цель-на-месяц.csv') → db.add()
```

## 🤝 Contributing

1. Fork → clone → `uv sync`.
2. Создайте branch: `git checkout -b feature/xyz`.
3. Commit: `git commit -m "feat: add xyz"`.
4. Push → PR.

Формат коммитов: [Conventional Commits](https://www.conventionalcommits.org/).

## 📄 License

MIT © Daniil Novel.

---

⭐ **Star проект, если полезно!** Поделитесь фидбеком в Issues.
