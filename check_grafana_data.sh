#!/bin/bash

# Скрипт для проверки данных в Grafana и PostgreSQL
# Используется для диагностики проблемы "No data" в Grafana

set -e

echo "========================================="
echo "🔍 Диагностика данных Grafana"
echo "========================================="
echo ""

# Определяем Docker команду
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_CMD="docker-compose"
else
    DOCKER_CMD="docker compose"
fi

echo "📊 Используемая команда Docker: $DOCKER_CMD"
echo ""

# 1. Проверка статуса контейнеров
echo "1️⃣ Проверка статуса контейнеров..."
echo "-----------------------------------"
$DOCKER_CMD ps
echo ""

# 2. Проверка подключения к PostgreSQL
echo "2️⃣ Проверка подключения к PostgreSQL..."
echo "-----------------------------------"
$DOCKER_CMD exec db pg_isready -U leetcode_user -d leetcode_tracker
echo ""

# 3. Проверка таблиц в базе данных
echo "3️⃣ Список таблиц в базе данных..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "\dt"
echo ""

# 4. Проверка количества пользователей
echo "4️⃣ Количество пользователей..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) as user_count FROM users;"
echo ""

# 5. Проверка пользователей с leetcode_username
echo "5️⃣ Пользователи с LeetCode username..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT id, username, leetcode_username, last_synced_at FROM users;"
echo ""

# 6. Проверка количества задач
echo "6️⃣ Количество задач в solved_tasks..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) as tasks_count FROM solved_tasks;"
echo ""

# 7. Проверка последних задач
echo "7️⃣ Последние 5 задач..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT id, user_id, title, difficulty, date, points FROM solved_tasks ORDER BY date DESC LIMIT 5;"
echo ""

# 8. Проверка статистики по сложности
echo "8️⃣ Статистика по сложности задач..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT difficulty, COUNT(*) as count FROM solved_tasks GROUP BY difficulty;"
echo ""

# 9. Проверка логов приложения
echo "9️⃣ Последние 20 строк логов приложения..."
echo "-----------------------------------"
$DOCKER_CMD logs --tail 20 app
echo ""

# 10. Проверка логов Grafana
echo "🔟 Последние 20 строк логов Grafana..."
echo "-----------------------------------"
$DOCKER_CMD logs --tail 20 grafana
echo ""

echo "========================================="
echo "✅ Диагностика завершена!"
echo "========================================="
echo ""
echo "📝 Рекомендации:"
echo "- Если таблиц нет, запустите миграции: $DOCKER_CMD exec -T app uv run alembic upgrade head"
echo "- Если нет задач, убедитесь что у пользователя заполнен leetcode_username"
echo "- Если пользователей нет, зарегистрируйтесь через приложение"
echo "- Проверьте логи на наличие ошибок синхронизации"
echo ""
