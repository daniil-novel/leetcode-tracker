@echo off
REM Скрипт для локального запуска приложения LeetCode Tracker (Windows)
setlocal enabledelayedexpansion

echo 🚀 Запуск LeetCode Tracker локально...

REM Проверка .env файла
if not exist .env (
    echo ⚠️  Файл .env не найден. Копирую из .env.example...
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ Создан .env файл. Отредактируйте его перед запуском.
        echo.
        echo 📝 Необходимо настроить следующие параметры в .env:
        echo    - DATABASE_URL
        echo    - SECRET_KEY
        echo    - LEETCODE_SESSION (опционально^)
        echo.
        exit /b 1
    ) else (
        echo ❌ ERROR: .env.example не найден!
        exit /b 1
    )
)

echo ✅ .env файл найден

REM Проверка наличия Docker
where docker >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Docker не установлен
    exit /b 1
)

REM Проверка что Docker запущен
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Docker не запущен. Запустите Docker Desktop.
    exit /b 1
)

echo ✅ Docker запущен

REM Определение команды Docker Compose
where docker-compose >nul 2>&1
if errorlevel 1 (
    set DOCKER_CMD=docker compose
) else (
    set DOCKER_CMD=docker-compose
)

echo ✅ Используется команда: !DOCKER_CMD!

REM Остановка существующих контейнеров
echo 🛑 Остановка существующих контейнеров...
!DOCKER_CMD! down

REM Сборка и запуск контейнеров
echo 🔨 Сборка и запуск контейнеров...
!DOCKER_CMD! up --build -d
if errorlevel 1 (
    echo ❌ ERROR: Не удалось запустить контейнеры
    exit /b 1
)

REM Ожидание запуска БД
echo ⏳ Ожидание запуска PostgreSQL...
timeout /t 5 /nobreak >nul

REM Применение миграций
echo 📦 Применение миграций БД...
!DOCKER_CMD! exec -T app uv run alembic upgrade head
if errorlevel 1 (
    echo ❌ ERROR: Не удалось применить миграции
    echo 📋 Логи приложения:
    !DOCKER_CMD! logs app --tail 30
    exit /b 1
)

echo ✅ Миграции применены успешно

REM Вывод статуса
echo.
echo ✅ Приложение запущено!
echo.
echo 📊 Статус контейнеров:
!DOCKER_CMD! ps
echo.
echo 🌐 Доступные сервисы:
echo    - Приложение: http://localhost:8000
echo    - Grafana: http://localhost:3000
echo    - Prometheus: http://localhost:9093
echo.
echo 📝 Полезные команды:
echo    - Просмотр логов: !DOCKER_CMD! logs -f [service_name]
echo    - Просмотр всех логов: !DOCKER_CMD! logs -f
echo    - Перезапуск сервиса: !DOCKER_CMD! restart [service_name]
echo    - Остановка: !DOCKER_CMD! down
echo    - Или используйте: stop_local.bat
echo.
