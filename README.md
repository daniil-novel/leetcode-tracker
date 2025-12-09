# LeetCode Tracker 🚀📈

[![Stars](https://img.shields.io/github/stars/daniil-novel/leetcode-tracker?style=social)](https://github.com/daniil-novel/leetcode-tracker)
[![License](https://img.shields.io/github/license/daniil-novel/leetcode-tracker)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121%2B-brightgreen)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3%2B-61dafb)](https://react.dev/)

## Описание

Современный веб-сервис для **геймифицированного трекинга прогресса на LeetCode** с поддержкой множественных пользователей:

- 🔐 **GitHub OAuth авторизация** - безопасный вход через GitHub аккаунт
- 📊 **Интерактивные графики** - визуализация прогресса с Chart.js
- 📅 **Календарь активности** - тепловая карта решённых задач
- 🎯 **Цели на месяц** - установка и отслеживание целей по XP
- ⏱️ **Трекинг времени** - учёт времени на решение задач
- 📈 **Детальная статистика** - анализ прогресса по дням, неделям, месяцам
- 🏆 **Система рангов** - от Новичка до Легенды
- 💾 **CSV импорт** - массовая загрузка данных
- 🌐 **REST API** - полная документация в `/docs`
- 📊 **Grafana Dashboard** - продвинутая аналитика и визуализация

## 🛠 Технологии

### Backend
- **FastAPI** 0.121+ - современный асинхронный веб-фреймворк
- **SQLAlchemy** 2.0+ - ORM для работы с БД
- **Alembic** - миграции базы данных
- **Authlib** - OAuth 2.0 авторизация
- **python-jose** - JWT токены
- **Pydantic** - валидация данных

### Frontend
- **React** 18.3+ - современный UI фреймворк
- **TypeScript** - типизированный JavaScript
- **Vite** - быстрый сборщик
- **React Router** - маршрутизация
- **Chart.js** - интерактивные графики
- **Tailwind CSS** - утилитарный CSS

### Инфраструктура
- **uv** - быстрый пакетный менеджер Python
- **SQLite** - база данных (по умолчанию)
- **Nginx** - reverse proxy
- **systemd** - управление сервисом

## 📦 Быстрый старт

### 1. Установка uv (если нет)

```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
pip install uv

# Проверка
uv --version
```

### 2. Клонирование и установка

```bash
git clone https://github.com/daniil-novel/leetcode-tracker.git
cd leetcode-tracker
uv sync  # Установит все зависимости и создаст venv
```

### 3. Настройка GitHub OAuth

1. Создайте GitHub OAuth App: https://github.com/settings/developers
2. Настройте URLs:
   - Homepage URL: `http://localhost:8000`
   - Callback URL: `http://localhost:8000/auth/callback/github`
3. Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
# Отредактируйте .env и добавьте:
# GITHUB_CLIENT_ID=your_client_id
# GITHUB_CLIENT_SECRET=your_client_secret
# SECRET_KEY=your_random_secret_key
```

### 4. Сборка фронтенда

```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. Запуск приложения

```bash
uv run uvicorn leetcode_tracker.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте:
- [http://localhost:8000](http://localhost:8000) - Главная страница
- [http://localhost:8000/docs](http://localhost:8000/docs) - API документация

База данных `leetcode.db` создастся автоматически при первом запуске.

## 🔧 Конфигурация

### Переменные окружения (.env)

```bash
# Безопасность
SECRET_KEY=your-secret-key-change-this-to-random-string

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/callback/github

# База данных (опционально)
DATABASE_URL=sqlite:///./leetcode.db

# Приложение
APP_TITLE=LeetCode Tracker
DEBUG=false
LOG_LEVEL=INFO
```

### Система XP
- **Easy**: 1 XP
- **Medium**: 3 XP
- **Hard**: 5 XP

### Система рангов
- 🥉 **Новичок**: 0-49 XP
- 🥈 **Практикант**: 50-149 XP
- 🥇 **Специалист**: 150-299 XP
- 💎 **Эксперт**: 300-499 XP
- 👑 **Мастер**: 500-799 XP
- 🏆 **Легенда**: 800+ XP

## 📁 Структура проекта

```
leetcode_tracker/
├── frontend/                 # React приложение
│   ├── src/
│   │   ├── components/      # React компоненты
│   │   ├── pages/          # Страницы (Login, Dashboard)
│   │   ├── context/        # React Context (Auth)
│   │   └── main.tsx        # Точка входа
│   ├── package.json
│   └── vite.config.ts
├── leetcode_tracker/        # FastAPI приложение
│   ├── routers/            # API роутеры
│   │   ├── auth.py        # Авторизация
│   │   ├── tasks.py       # Задачи
│   │   └── stats.py       # Статистика
│   ├── main.py            # Главный файл приложения
│   ├── models.py          # SQLAlchemy модели
│   ├── schemas.py         # Pydantic схемы
│   ├── auth.py            # OAuth и JWT
│   ├── config.py          # Конфигурация
│   ├── database.py        # Подключение к БД
│   └── deploy.py          # Скрипт деплоя
├── alembic/               # Миграции БД
├── pyproject.toml         # Зависимости Python
├── .env.example           # Пример конфигурации
└── README.md
```

## 🚀 Деплой

### Деплой на сервер (One-command)

Приложение настроено для автоматического деплоя на сервер:

```bash
# Установите dev зависимости и запустите деплой
uv sync --extra dev && uv run deploy
```

Скрипт автоматически:
1. Подключится к серверу по SSH
2. Остановит сервис
3. Загрузит все файлы
4. Обновит зависимости
5. Перезапустит сервис

### Настройка production сервера

1. **Установите зависимости на сервере:**
```bash
# Установите uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Клонируйте репозиторий
git clone https://github.com/daniil-novel/leetcode-tracker.git
cd leetcode-tracker

# Установите зависимости
uv sync
```

2. **Настройте systemd сервис:**
```bash
sudo cp leetcode-tracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable leetcode-tracker
sudo systemctl start leetcode-tracker
```

3. **Настройте Nginx:**
```bash
sudo cp nginx-leetcode-tracker.conf /etc/nginx/sites-available/leetcode-tracker
sudo ln -s /etc/nginx/sites-available/leetcode-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

4. **Настройте SSL (Let's Encrypt):**
```bash
sudo certbot --nginx -d yourdomain.com
```

### Docker (опционально)

```dockerfile
FROM python:3.12-slim

# Установка uv
RUN pip install uv

# Копирование файлов
WORKDIR /app
COPY . .

# Установка зависимостей
RUN uv sync --frozen

# Сборка фронтенда
RUN cd frontend && npm install && npm run build

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "leetcode_tracker.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t leetcode-tracker .
docker run -p 8000:8000 --env-file .env leetcode-tracker
```

## 📊 Grafana Dashboard

Для продвинутой аналитики и визуализации данных доступен Grafana Dashboard.

### Быстрый запуск Grafana

1. **Установите Docker Desktop** (если еще не установлен)
2. **Запустите Grafana:**
   ```bash
   docker-compose up -d
   ```
3. **Откройте в браузере:** http://localhost:3000
4. **Войдите:** admin / admin

Dashboard будет автоматически настроен и готов к использованию!

### Что включено

- 📈 **Метрики в реальном времени** - общее количество задач, XP, активные пользователи
- 📊 **Графики прогресса** - визуализация решенных задач по времени
- 🥧 **Распределение по сложности** - круговая диаграмма Easy/Medium/Hard
- 🏆 **Таблица лидеров** - топ пользователей по XP
- 📋 **Последние задачи** - список недавно решенных задач

**Подробная документация:** [GRAFANA_SETUP.md](GRAFANA_SETUP.md)

## 📊 Использование

### Добавление задачи

1. Войдите через GitHub
2. Нажмите "Добавить задачу"
3. Заполните форму:
   - Название задачи
   - Сложность (Easy/Medium/Hard)
   - Дата решения
   - Время (опционально)
   - Заметки (опционально)
4. Нажмите "Сохранить"

### Импорт из CSV

```python
# Формат CSV:
# date,title,difficulty,time_spent,notes
# 2024-01-15,Two Sum,Easy,30,First problem!
# 2024-01-16,Add Two Numbers,Medium,45,Linked lists

# Импорт через API:
curl -X POST "http://localhost:8000/api/tasks/import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@tasks.csv"
```

### API примеры

```bash
# Получить статистику за месяц
curl "http://localhost:8000/api/month/stats/2024/11" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Получить все задачи
curl "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Добавить задачу
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Two Sum",
    "difficulty": "Easy",
    "date": "2024-11-26",
    "time_spent": 30
  }'
```

## 🔐 Безопасность

- ✅ HTTPS-only cookies
- ✅ JWT токены с истечением срока действия
- ✅ OAuth 2.0 авторизация через GitHub
- ✅ CORS настройки
- ✅ SQL injection защита (SQLAlchemy ORM)
- ✅ XSS защита (React автоматически экранирует)
- ✅ Trusted Host middleware

## 🤝 Contributing

1. Fork проекта
2. Создайте feature branch: `git checkout -b feature/amazing-feature`
3. Commit изменения: `git commit -m "feat: add amazing feature"`
4. Push в branch: `git push origin feature/amazing-feature`
5. Откройте Pull Request

### Формат коммитов

Используем [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг
- `test:` - добавление тестов
- `chore:` - обновление зависимостей и т.д.

## 📝 Changelog

### v1.1.0 (2024-11-26)
- ✨ Добавлена GitHub OAuth авторизация
- ✨ Поддержка множественных пользователей
- ✨ React фронтенд с TypeScript
- ✨ Календарь активности с тепловой картой
- ✨ Система рангов
- ✨ Трекинг времени на задачи
- ✨ CSV импорт
- 🐛 Исправлены проблемы с маршрутизацией
- 🐛 Исправлены JWT токены (sub как строка)
- 🐛 Добавлен недостающий эндпоинт /api/auth/me
- 🔧 Обновлена схема базы данных

### v1.0.0 (2024-11-20)
- 🎉 Первый релиз
- ✨ Базовый функционал трекинга задач
- ✨ Графики и статистика
- ✨ REST API

## 📄 License

MIT © Daniil Novel

## 🙏 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) - за отличный фреймворк
- [React](https://react.dev/) - за мощный UI фреймворк
- [Chart.js](https://www.chartjs.org/) - за красивые графики
- [uv](https://astral.sh/uv) - за быстрый пакетный менеджер

---

⭐ **Star проект, если он вам полезен!** Поделитесь фидбеком в [Issues](https://github.com/daniil-novel/leetcode-tracker/issues).

🌐 **Live Demo**: [https://novel-cloudtech.com:7443](https://novel-cloudtech.com:7443)
