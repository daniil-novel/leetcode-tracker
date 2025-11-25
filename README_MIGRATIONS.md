# Миграции базы данных с Alembic

Этот проект использует Alembic для управления миграциями базы данных SQLite.

## Основные команды

### Создание новой миграции

После изменения моделей в `leetcode_tracker/models.py`:

```bash
# Автоматическое создание миграции на основе изменений в моделях
uv run alembic revision --autogenerate -m "Описание изменений"

# Пример:
uv run alembic revision --autogenerate -m "Add user preferences table"
```

### Применение миграций

```bash
# Применить все неприменённые миграции
uv run alembic upgrade head

# Применить одну миграцию вперёд
uv run alembic upgrade +1

# Применить до конкретной ревизии
uv run alembic upgrade <revision_id>
```

### Откат миграций

```bash
# Откатить одну миграцию назад
uv run alembic downgrade -1

# Откатить до конкретной ревизии
uv run alembic downgrade <revision_id>

# Откатить все миграции
uv run alembic downgrade base
```

### Просмотр истории

```bash
# Показать текущую ревизию
uv run alembic current

# Показать историю миграций
uv run alembic history

# Показать историю с деталями
uv run alembic history --verbose
```

## Рабочий процесс

### 1. Локальная разработка

Когда вы изменяете модели:

```bash
# 1. Изменить модели в leetcode_tracker/models.py
# 2. Создать миграцию
uv run alembic revision --autogenerate -m "Add new field to User model"

# 3. Проверить созданную миграцию в alembic/versions/
# 4. Применить миграцию локально
uv run alembic upgrade head

# 5. Протестировать изменения
uv run uvicorn leetcode_tracker.main:app --reload
```

### 2. Деплой на сервер

```bash
# На сервере после git pull:

# 1. Остановить сервис
sudo systemctl stop leetcode-tracker

# 2. Сделать backup БД
cp /root/leetcode_tracker_uv/leetcode.db /root/leetcode_backup_$(date +%Y%m%d_%H%M%S).db

# 3. Установить зависимости (если добавлены новые)
/root/.local/bin/uv sync

# 4. Применить миграции
/root/.local/bin/uv run alembic upgrade head

# 5. Запустить сервис
sudo systemctl start leetcode-tracker

# 6. Проверить логи
sudo journalctl -u leetcode-tracker -f
```

## Структура файлов

```
.
├── alembic/                    # Директория Alembic
│   ├── env.py                 # Конфигурация окружения
│   ├── script.py.mako         # Шаблон для миграций
│   └── versions/              # Файлы миграций
│       └── xxxx_description.py
├── alembic.ini                # Конфигурация Alembic
└── leetcode_tracker/
    ├── models.py              # Модели SQLAlchemy
    └── database.py            # Настройка БД
```

## Важные замечания

⚠️ **Всегда делайте backup БД перед применением миграций на продакшене!**

⚠️ **Проверяйте автоматически созданные миграции** - иногда Alembic может не корректно определить изменения.

⚠️ **Не редактируйте уже применённые миграции** - создавайте новые миграции для исправлений.

⚠️ **SQLite ограничения**: SQLite не поддерживает некоторые ALTER TABLE операции (например, удаление колонок, изменение типов). В таких случаях Alembic создаст batch операции.

## Troubleshooting

### Проблема: "Target database is not up to date"

```bash
# Проверить текущую ревизию
uv run alembic current

# Посмотреть историю
uv run alembic history

# Применить миграции
uv run alembic upgrade head
```

### Проблема: "Can't locate revision identified by 'xxxxx'"

Это означает что БД содержит ревизию, которой нет в коде. Обычно это происходит если:
- БД с другого окружения
- Миграции были удалены из репозитория

Решение:
```bash
# Восстановить БД из backup
cp /root/leetcode_backup_XXXXXX.db /root/leetcode_tracker_uv/leetcode.db

# Или пересоздать БД (ВНИМАНИЕ: потеря данных!)
# rm leetcode.db
# uv run alembic upgrade head
```

### Проблема: Конфликт миграций при работе в команде

Если два разработчика создали миграции параллельно:

```bash
# 1. Согласовать порядок миграций
# 2. Один из разработчиков должен пересоздать свою миграцию:
uv run alembic revision --autogenerate -m "My changes"
```

## Полезные ссылки

- [Alembic документация](https://alembic.sqlalchemy.org/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)
