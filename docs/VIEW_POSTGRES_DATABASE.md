# Как посмотреть базу данных PostgreSQL

Есть несколько способов просмотреть вашу базу данных PostgreSQL:

## Способ 1: Через командную строку (psql) - Самый быстрый

### Подключиться к базе данных:
```bash
docker exec -it leetcode-tracker-postgres psql -U leetcode_user -d leetcode_tracker
```

### Полезные команды в psql:

```sql
-- Показать все таблицы
\dt

-- Показать структуру таблицы users
\d users

-- Показать структуру таблицы solved_tasks
\d solved_tasks

-- Показать структуру таблицы month_goals
\d month_goals

-- Посмотреть всех пользователей
SELECT * FROM users;

-- Посмотреть все решенные задачи
SELECT * FROM solved_tasks;

-- Посмотреть цели по месяцам
SELECT * FROM month_goals;

-- Посмотреть количество записей в каждой таблице
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'solved_tasks', COUNT(*) FROM solved_tasks
UNION ALL
SELECT 'month_goals', COUNT(*) FROM month_goals;

-- Выйти из psql
\q
```

## Способ 2: Через pgAdmin (GUI инструмент)

### Установка pgAdmin:
1. Скачайте с https://www.pgadmin.org/download/
2. Установите на свой компьютер

### Подключение:
- **Host**: localhost
- **Port**: 5432
- **Database**: leetcode_tracker
- **Username**: leetcode_user
- **Password**: leetcode_password

## Способ 3: Через DBeaver (Универсальный GUI инструмент)

### Установка DBeaver:
1. Скачайте с https://dbeaver.io/download/
2. Установите на свой компьютер

### Подключение:
1. Создайте новое подключение PostgreSQL
2. Введите параметры:
   - **Host**: localhost
   - **Port**: 5432
   - **Database**: leetcode_tracker
   - **Username**: leetcode_user
   - **Password**: leetcode_password

## Способ 4: Через VS Code расширение

### Установите расширение:
1. Откройте VS Code
2. Перейдите в Extensions (Ctrl+Shift+X)
3. Найдите и установите "PostgreSQL" от Chris Kolkman

### Подключение:
1. Нажмите на иконку PostgreSQL в боковой панели
2. Добавьте новое подключение:
   - **Host**: localhost
   - **Port**: 5432
   - **Database**: leetcode_tracker
   - **Username**: leetcode_user
   - **Password**: leetcode_password

## Способ 5: Добавить pgAdmin в Docker Compose (Рекомендуется!)

Добавьте pgAdmin прямо в ваш docker-compose.yml:

```yaml
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: leetcode-tracker-pgadmin
    restart: unless-stopped
    ports:
      - "5050:80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    networks:
      - leetcode-tracker
    depends_on:
      - postgres
```

Затем:
```bash
docker-compose up -d pgadmin
```

Откройте в браузере: http://localhost:5050
- Email: admin@admin.com
- Password: admin

Добавьте сервер:
- **Name**: LeetCode Tracker
- **Host**: postgres (имя контейнера в Docker сети)
- **Port**: 5432
- **Database**: leetcode_tracker
- **Username**: leetcode_user
- **Password**: leetcode_password

## Быстрая проверка через командную строку

Просто выполните эти команды для быстрой проверки:

```bash
# Подключиться к PostgreSQL
docker exec -it leetcode-tracker-postgres psql -U leetcode_user -d leetcode_tracker

# Внутри psql выполните:
\dt                    # Показать все таблицы
SELECT * FROM users;   # Показать всех пользователей
\q                     # Выйти
```

## Полезные SQL запросы для анализа данных

```sql
-- Статистика по пользователям
SELECT 
    u.username,
    COUNT(st.id) as total_tasks,
    SUM(st.points) as total_points
FROM users u
LEFT JOIN solved_tasks st ON u.id = st.user_id
GROUP BY u.id, u.username;

-- Задачи по сложности
SELECT 
    difficulty,
    COUNT(*) as count,
    SUM(points) as total_points
FROM solved_tasks
GROUP BY difficulty;

-- Активность по датам
SELECT 
    date,
    COUNT(*) as tasks_count,
    SUM(points) as points_earned
FROM solved_tasks
GROUP BY date
ORDER BY date DESC
LIMIT 10;
