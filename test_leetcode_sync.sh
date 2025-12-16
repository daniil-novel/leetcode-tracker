#!/bin/bash

# Скрипт для тестирования синхронизации LeetCode
# Заполняет тестовыми данными и проверяет работу синхронизации

set -e

echo "========================================="
echo "🧪 Тестирование синхронизации LeetCode"
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

# Запрашиваем LeetCode username
read -p "Введите LeetCode username для тестирования (например: admin-daniil): " LEETCODE_USERNAME

if [ -z "$LEETCODE_USERNAME" ]; then
    echo "❌ LeetCode username не может быть пустым!"
    exit 1
fi

echo ""
echo "1️⃣ Обновление leetcode_username для первого пользователя..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "UPDATE users SET leetcode_username = '$LEETCODE_USERNAME' WHERE id = 1;"
echo ""

echo "2️⃣ Проверка обновленного пользователя..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT id, username, leetcode_username FROM users WHERE id = 1;"
echo ""

echo "3️⃣ Перезапуск приложения для запуска синхронизации..."
echo "-----------------------------------"
$DOCKER_CMD restart app
echo ""

echo "⏳ Ожидание 15 секунд для синхронизации..."
sleep 15
echo ""

echo "4️⃣ Проверка логов синхронизации..."
echo "-----------------------------------"
$DOCKER_CMD logs app --tail 30 | grep -A 5 -B 5 "sync"
echo ""

echo "5️⃣ Проверка синхронизированных задач..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) as synced_tasks FROM solved_tasks WHERE user_id = 1;"
echo ""

echo "6️⃣ Последние синхронизированные задачи..."
echo "-----------------------------------"
$DOCKER_CMD exec -T db psql -U leetcode_user -d leetcode_tracker -c "SELECT title, difficulty, date, points FROM solved_tasks WHERE user_id = 1 ORDER BY date DESC LIMIT 10;"
echo ""

echo "========================================="
echo "✅ Тестирование завершено!"
echo "========================================="
echo ""
echo "📝 Проверьте Grafana для отображения данных:"
echo "   URL: https://novel-cloudtech.com:7443/grafana/"
echo "   Логин: admin"
echo "   Пароль: admin"
echo ""
