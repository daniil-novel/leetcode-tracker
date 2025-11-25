# План внедрения улучшений архитектуры LeetCode Tracker

## Анализ текущего состояния

### ✅ Что уже сделано:
1. **Рефакторинг кода:**
   - Приложение разделено на модули (routers: auth, tasks, stats, frontend)
   - Dependencies централизованы в dependencies.py
   - ProxyHeadersMiddleware добавлен в main.py
   - HTTP 401 exception handler настроен для редиректа на /login

2. **Модели данных:**
   - User (с OAuth полями)
   - SolvedTask (с полями для трекинга задач)
   - MonthGoal (цели по месяцам)
   - Все с правильными relationships и индексами

3. **Аутентификация:**
   - GitHub OAuth реализован
   - JWT токены в secure cookies
   - get_current_user и get_current_user_optional зависимости

### ❌ Проблемы, требующие решения:

1. **Systemd сервис НЕ использует `--proxy-headers`**
   - Uvicorn не знает что работает за HTTPS прокси
   - Это может вызывать проблемы с cookies и редиректами
   - **КРИТИЧНО:** Нужно добавить флаг в systemd service

2. **Отсутствует система миграций БД (Alembic)**
   - При изменении моделей нужно пересоздавать БД вручную
   - Теряются данные при обновлениях схемы
   - Нет версионирования структуры БД

3. **Недостаточно логирования для отладки сессий**
   - Сложно понять где именно происходит "вылет" из сессии
   - Нужно добавить подробное логирование auth flow

4. **Отсутствует config.py с централизованными настройками**
   - Настройки разбросаны по файлам
   - Нет валидации environment variables через Pydantic Settings

## План действий (пошагово)

### Этап 1: HOTFIX - Исправление Systemd сервиса (КРИТИЧНО) ⚡
**Цель:** Добавить `--proxy-headers` чтобы FastAPI правильно понимал HTTPS
- [ ] Создать обновленный systemd service файл 
- [ ] Добавить `--proxy-headers` к команде uvicorn
- [ ] Добавить переменные окружения в service файл
- [ ] Создать скрипт для обновления сервиса на сервере
- [ ] **Коммит:** "fix: add --proxy-headers to systemd service for proper HTTPS handling"

### Этап 2: Настройка Config.py с Pydantic Settings
**Цель:** Централизовать и валидировать конфигурацию
- [ ] Создать config.py с BaseSettings
- [ ] Перенести все переменные окружения в Settings класс
- [ ] Обновить код для использования settings вместо os.getenv
- [ ] **Коммит:** "refactor: centralize configuration with Pydantic Settings"

### Этап 3: Настройка Alembic для миграций
**Цель:** Версионирование структуры БД
- [ ] Установить alembic в pyproject.toml
- [ ] Инициализировать alembic (alembic init)
- [ ] Настроить alembic.ini и env.py
- [ ] Создать начальную миграцию с текущей схемой
- [ ] Создать README_MIGRATIONS.md с инструкциями
- [ ] **Коммит:** "feat: add Alembic for database migrations"

### Этап 4: Улучшение логирования
**Цель:** Детальное логирование для отладки
- [ ] Добавить structured logging
- [ ] Логировать все этапы аутентификации
- [ ] Логировать установку/проверку cookies
- [ ] Добавить request ID для трейсинга
- [ ] **Коммит:** "feat: enhance logging for auth flow debugging"

### Этап 5: Улучшение обработки ошибок
**Цель:** Graceful degradation
- [ ] Добавить middleware для логирования всех requests
- [ ] Улучшить обработку истекших токенов
- [ ] Добавить user-friendly error страницы
- [ ] **Коммит:** "feat: improve error handling and user experience"

### Этап 6: Тестирование функциональности
**Цель:** Проверить что все кнопки работают
- [ ] Протестировать GitHub OAuth login
- [ ] Протестировать добавление задачи через форму
- [ ] Протестировать редактирование задачи
- [ ] Протестировать удаление задачи
- [ ] Протестировать импорт CSV
- [ ] Протестировать установку цели месяца
- [ ] Протестировать навигацию по календарю
- [ ] Протестировать все графики
- [ ] **Коммит:** "test: verify all functionality works correctly"

### Этап 7: Оптимизация и финальные улучшения
**Цель:** Performance и UX
- [ ] Добавить индексы если нужны
- [ ] Проверить N+1 queries
- [ ] Добавить кеширование статстики если нужно
- [ ] Улучшить responsive design
- [ ] **Коммит:** "perf: optimize queries and add caching"

## Критерии успеха

1. ✅ Пользователь НЕ "вылетает" на страницу логина при нажатии кнопок
2. ✅ Все кнопки (добавить, редактировать, удалить, импорт) работают
3. ✅ Сессия сохраняется между перезагрузками страницы
4. ✅ Логи показывают детальную информацию о auth flow
5. ✅ БД можно мигрировать без потери данных
6. ✅ Все настройки валидируются через Pydantic

## Технические детали

### Systemd Service с --proxy-headers
```ini
[Service]
ExecStart=/root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 127.0.0.1 --port 8000 --proxy-headers
```

### Alembic миграция
```bash
# Инициализация
alembic init alembic

# Создание миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграции
alembic upgrade head
```

### Pydantic Settings пример
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    github_client_id: str
    github_client_secret: str
    
    class Config:
        env_file = ".env"
```

## Порядок деплоя на сервер

1. Остановить сервис: `systemctl stop leetcode-tracker`
2. Сделать backup БД: `cp /root/leetcode_tracker_uv/leetcode.db /root/leetcode_backup_$(date +%Y%m%d).db`
3. Pull код: `git pull origin main`
4. Установить зависимости: `/root/.local/bin/uv sync`
5. Применить миграции: `/root/.local/bin/uv run alembic upgrade head`
6. Обновить systemd service: `cp leetcode-tracker.service /etc/systemd/system/`
7. Перезагрузить daemon: `systemctl daemon-reload`
8. Запустить сервис: `systemctl start leetcode-tracker`
9. Проверить статус: `systemctl status leetcode-tracker`
10. Проверить логи: `journalctl -u leetcode-tracker -f`
