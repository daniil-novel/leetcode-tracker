#!/bin/bash

# Скрипт для проверки данных после настройки синхронизации
set -e

echo "========================================="
echo "📊 Проверка данных в Grafana"
echo "========================================="
echo ""

# Определяем Docker команду
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_CMD="docker-compose"
else
    DOCKER_CMD="docker compose"
fi

echo "1️⃣ Проверка пользователей..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT id, username, leetcode_username FROM users;"
echo ""

echo "2️⃣ Количество синхронизированных задач..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) as total_tasks FROM solved_tasks;"
echo ""

echo "3️⃣ Последние 10 задач..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT title, difficulty, date, points, platform FROM solved_tasks ORDER BY date DESC LIMIT 10;"
echo ""

echo "4️⃣ Статистика по сложности..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT difficulty, COUNT(*) as count FROM solved_tasks GROUP BY difficulty;"
echo ""

echo "5️⃣ Общая сумма XP..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT SUM(points) as total_xp FROM solved_tasks;"
echo ""

echo "6️⃣ Логи синхронизации (последние 30 строк)..."
echo "-----------------------------------"
$DOCKER_CMD logs --tail 30 app | grep -i "sync\|leetcode" || echo "⚠️  Логи синхронизации не найдены"
echo ""

echo "========================================="
echo "✅ Проверка завершена!"
echo "========================================="
echo ""
echo "📊 Теперь откройте Grafana:"
echo "   URL: https://novel-cloudtech.com:7443/grafana/"
echo "   Логин: admin"
echo "   Пароль: admin"
echo ""
echo "💡 Если данных нет, подождите 10-15 секунд и обновите страницу"
echo ""
