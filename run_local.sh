#!/bin/bash
# Скрипт для локального запуска приложения LeetCode Tracker

set -e

echo "🚀 Запуск LeetCode Tracker локально..."

# Проверка .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Копирую из .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Создан .env файл. Отредактируйте его перед запуском."
        echo ""
        echo "📝 Необходимо настроить следующие параметры в .env:"
        echo "   - DATABASE_URL"
        echo "   - SECRET_KEY"
        echo "   - LEETCODE_SESSION (опционально)"
        echo ""
        exit 1
    else
        echo "❌ ERROR: .env.example не найден!"
        exit 1
    fi
fi

echo "✅ .env файл найден"

# Проверка наличия Docker
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ ERROR: Docker не установлен"
    exit 1
fi

# Проверка что Docker запущен
if ! docker info >/dev/null 2>&1; then
    echo "❌ ERROR: Docker не запущен. Запустите Docker Desktop."
    exit 1
fi

echo "✅ Docker запущен"

# Определение команды Docker Compose
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_CMD="docker-compose"
else
    DOCKER_CMD="docker compose"
fi

echo "✅ Используется команда: $DOCKER_CMD"

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
$DOCKER_CMD down

# Сборка и запуск контейнеров
echo "🔨 Сборка и запуск контейнеров..."
$DOCKER_CMD up --build -d

# Ожидание запуска БД
echo "⏳ Ожидание запуска PostgreSQL..."
sleep 5

# Применение миграций
echo "📦 Применение миграций БД..."
if ! $DOCKER_CMD exec -T app uv run alembic upgrade head; then
    echo "❌ ERROR: Не удалось применить миграции"
    echo "📋 Логи приложения:"
    $DOCKER_CMD logs app --tail 30
    exit 1
fi

echo "✅ Миграции применены успешно"

# Вывод статуса
echo ""
echo "✅ Приложение запущено!"
echo ""
echo "📊 Статус контейнеров:"
$DOCKER_CMD ps
echo ""
echo "🌐 Доступные сервисы:"
echo "   - Приложение: http://localhost:8000"
echo "   - Grafana: http://localhost:3000"
echo "   - Prometheus: http://localhost:9093"
echo ""
echo "📝 Полезные команды:"
echo "   - Просмотр логов: $DOCKER_CMD logs -f [service_name]"
echo "   - Просмотр всех логов: $DOCKER_CMD logs -f"
echo "   - Перезапуск сервиса: $DOCKER_CMD restart [service_name]"
echo "   - Остановка: $DOCKER_CMD down"
echo "   - Или используйте: ./stop_local.sh"
echo ""
