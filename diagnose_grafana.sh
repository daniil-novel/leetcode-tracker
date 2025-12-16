#!/bin/bash

# Скрипт диагностики Grafana для LeetCode Tracker

echo "====================================="
echo "Диагностика Grafana"
echo "====================================="
echo

# 1. Проверка статуса контейнеров Docker
echo "1. Проверка статуса контейнеров Docker:"
docker ps -a --filter "name=grafana" --filter "name=postgres" --filter "name=leetcode-tracker-db"
echo

# 2. Проверка подключения к PostgreSQL из контейнера Grafana
echo "2. Проверка подключения к PostgreSQL из контейнера Grafana:"
docker exec grafana sh -c "nc -zv db 5432 2>&1 || nc -zv postgres 5432 2>&1 || nc -zv leetcode-tracker-db 5432 2>&1" 2>&1
echo

# 3. Проверка существования базы данных и таблиц
echo "3. Проверка существования базы данных и таблиц:"
docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "\dt" 2>&1
echo

# 4. Проверка данных в таблицах
echo "4. Проверка данных в таблице users:"
docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) as users_count FROM users;" 2>&1
echo

echo "5. Проверка данных в таблице solved_tasks:"
docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) as tasks_count FROM solved_tasks;" 2>&1
echo

# 6. Проверка логов Grafana
echo "6. Последние 30 строк логов Grafana:"
docker logs grafana --tail 30 2>&1
echo

# 7. Проверка конфигурации источника данных
echo "7. Проверка конфигурации источника данных:"
echo "Содержимое файла postgres.yml:"
cat grafana/provisioning/datasources/postgres.yml
echo

# 8. Проверка конфигурации дашбордов
echo "8. Проверка конфигурации дашбордов:"
echo "Содержимое файла dashboard.yml:"
cat grafana/provisioning/dashboards/dashboard.yml
echo

# 9. Проверка сетевого взаимодействия
echo "9. Проверка сети Docker:"
docker network ls | grep leetcode
echo

# 10. Проверка URL Grafana
echo "10. Grafana должна быть доступна по адресу:"
echo "   - Локально: http://localhost:3000"
echo "   - Удаленно: https://novel-cloudtech.com:7443/grafana/"
echo

echo "====================================="
echo "Диагностика завершена"
echo "====================================="
