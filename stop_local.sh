#!/bin/bash
# Скрипт для остановки локального окружения LeetCode Tracker

echo "🛑 Остановка LeetCode Tracker..."

# Определение команды Docker Compose
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_CMD="docker-compose"
else
    DOCKER_CMD="docker compose"
fi

# Остановка и удаление контейнеров
$DOCKER_CMD down

if [ $? -eq 0 ]; then
    echo "✅ Все контейнеры остановлены и удалены"
else
    echo "⚠️  Возникли проблемы при остановке контейнеров"
    exit 1
fi

# Показать оставшиеся контейнеры проекта (если есть)
REMAINING=$(docker ps -a --filter "name=leetcode" --filter "name=prometheus" --filter "name=grafana" -q | wc -l)
if [ "$REMAINING" -gt 0 ]; then
    echo "⚠️  Обнаружены оставшиеся контейнеры:"
    docker ps -a --filter "name=leetcode" --filter "name=prometheus" --filter "name=grafana"
    echo ""
    echo "Для полной очистки выполните: docker ps -a | grep leetcode | awk '{print \$1}' | xargs docker rm -f"
fi
