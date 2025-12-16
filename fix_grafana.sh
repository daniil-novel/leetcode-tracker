#!/bin/bash

# Скрипт автоматического исправления проблемы с Grafana

echo "====================================="
echo "Исправление проблемы Grafana"
echo "====================================="
echo

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Шаг 1: Проверка, что Docker запущен
echo "Шаг 1: Проверка Docker..."
if ! docker ps &> /dev/null; then
    print_error "Docker не запущен или недоступен"
    exit 1
fi
print_status "Docker работает"
echo

# Шаг 2: Остановка контейнера Grafana
echo "Шаг 2: Остановка контейнера Grafana..."
docker stop grafana &> /dev/null
if [ $? -eq 0 ]; then
    print_status "Контейнер Grafana остановлен"
else
    print_warning "Контейнер Grafana не был запущен или уже остановлен"
fi
echo

# Шаг 3: Удаление контейнера Grafana
echo "Шаг 3: Удаление контейнера Grafana..."
docker rm grafana &> /dev/null
if [ $? -eq 0 ]; then
    print_status "Контейнер Grafana удален"
else
    print_warning "Контейнер Grafana не существовал или уже был удален"
fi
echo

# Шаг 4: Проверка, что PostgreSQL запущен
echo "Шаг 4: Проверка PostgreSQL..."
if docker ps | grep -q "leetcode-tracker-db"; then
    print_status "PostgreSQL запущен"
else
    print_error "PostgreSQL не запущен. Запускаю..."
    docker-compose up -d db
    sleep 5
    if docker ps | grep -q "leetcode-tracker-db"; then
        print_status "PostgreSQL успешно запущен"
    else
        print_error "Не удалось запустить PostgreSQL"
        exit 1
    fi
fi
echo

# Шаг 5: Пересоздание контейнера Grafana
echo "Шаг 5: Создание нового контейнера Grafana с исправленной конфигурацией..."
docker-compose up -d grafana
if [ $? -eq 0 ]; then
    print_status "Контейнер Grafana создан и запущен"
else
    print_error "Не удалось создать контейнер Grafana"
    exit 1
fi
echo

# Шаг 6: Ожидание запуска Grafana
echo "Шаг 6: Ожидание полного запуска Grafana (15 секунд)..."
sleep 15
print_status "Grafana должна быть готова"
echo

# Шаг 7: Проверка логов Grafana
echo "Шаг 7: Проверка логов Grafana (последние 15 строк):"
echo "---------------------------------------"
docker logs grafana --tail 15 2>&1
echo "---------------------------------------"
echo

# Шаг 8: Проверка подключения к базе данных
echo "Шаг 8: Проверка подключения Grafana к PostgreSQL..."
docker exec grafana sh -c "nc -zv db 5432" &> /dev/null
if [ $? -eq 0 ]; then
    print_status "Grafana успешно подключается к PostgreSQL"
else
    print_warning "Не удалось проверить подключение (возможно, nc не установлен в контейнере)"
fi
echo

# Шаг 9: Проверка данных в базе
echo "Шаг 9: Проверка данных в базе данных..."
USERS_COUNT=$(docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs)
TASKS_COUNT=$(docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -t -c "SELECT COUNT(*) FROM solved_tasks;" 2>/dev/null | xargs)

if [ -z "$USERS_COUNT" ]; then
    print_error "Не удалось получить данные из базы"
else
    echo "  - Пользователей: $USERS_COUNT"
    echo "  - Задач: $TASKS_COUNT"
    
    if [ "$TASKS_COUNT" -eq 0 ]; then
        print_warning "В базе нет задач. Графики будут пустыми."
        echo "  Совет: Добавьте задачи через веб-интерфейс или используйте скрипт:"
        echo "         cd scripts && python create_test_data.py"
    else
        print_status "В базе есть данные для отображения"
    fi
fi
echo

# Шаг 10: Итоговая информация
echo "====================================="
echo "Исправление завершено!"
echo "====================================="
echo
echo "Grafana доступна по следующим адресам:"
echo "  - Локально: http://localhost:3000"
echo "  - Удаленно: https://novel-cloudtech.com:7443/grafana/"
echo
echo "Учетные данные для входа:"
echo "  - Username: admin"
echo "  - Password: admin"
echo
echo "Дальнейшие действия:"
echo "  1. Откройте Grafana в браузере"
echo "  2. Войдите с указанными учетными данными"
echo "  3. Перейдите в Configuration → Data Sources"
echo "  4. Проверьте источник данных 'LeetCode Tracker PostgreSQL'"
echo "  5. Нажмите 'Test' - должно быть 'Database Connection OK'"
echo "  6. Откройте 'LeetCode Tracker Dashboard' и проверьте графики"
echo
echo "Если графики пустые, убедитесь что в базе есть данные."
echo "Подробная инструкция: GRAFANA_FIX_INSTRUCTIONS.md"
echo
print_status "Готово!"
