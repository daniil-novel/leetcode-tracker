@echo off
REM Скрипт для остановки локального окружения LeetCode Tracker (Windows)
setlocal enabledelayedexpansion

echo 🛑 Остановка LeetCode Tracker...

REM Определение команды Docker Compose
where docker-compose >nul 2>&1
if errorlevel 1 (
    set DOCKER_CMD=docker compose
) else (
    set DOCKER_CMD=docker-compose
)

REM Остановка и удаление контейнеров
!DOCKER_CMD! -f docker-compose.local.yml down

if errorlevel 1 (
    echo ⚠️  Возникли проблемы при остановке контейнеров
    exit /b 1
) else (
    echo ✅ Все контейнеры остановлены и удалены
)

REM Проверка оставшихся контейнеров
for /f %%i in ('docker ps -a --filter "name=leetcode" -q 2^>nul ^| find /c /v ""') do set REMAINING=%%i

if !REMAINING! gtr 0 (
    echo ⚠️  Обнаружены оставшиеся контейнеры:
    docker ps -a --filter "name=leetcode"
    echo.
    echo Для полной очистки выполните: docker rm -f $(docker ps -a --filter "name=leetcode" -q)
)
