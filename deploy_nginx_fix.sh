#!/bin/bash

# Скрипт для применения исправленной nginx конфигурации
# Использование: bash deploy_nginx_fix.sh

set -e  # Остановка при ошибке

echo "🔧 Применение исправленной nginx конфигурации для Grafana..."

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка, что скрипт запущен с правами sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Пожалуйста, запустите скрипт с sudo${NC}"
    echo "Использование: sudo bash deploy_nginx_fix.sh"
    exit 1
fi

# Путь к nginx конфигурации
NGINX_CONF="/etc/nginx/sites-available/leetcode-tracker"
NGINX_ENABLED="/etc/nginx/sites-enabled/leetcode-tracker"

echo -e "${YELLOW}📋 Шаг 1: Создание резервной копии текущей конфигурации...${NC}"
if [ -f "$NGINX_CONF" ]; then
    cp "$NGINX_CONF" "${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✅ Резервная копия создана${NC}"
else
    echo -e "${YELLOW}⚠️  Файл конфигурации не найден, будет создан новый${NC}"
fi

echo -e "${YELLOW}📋 Шаг 2: Копирование новой конфигурации...${NC}"
cp nginx-leetcode-tracker.conf "$NGINX_CONF"
echo -e "${GREEN}✅ Конфигурация скопирована${NC}"

echo -e "${YELLOW}📋 Шаг 3: Создание символической ссылки (если нужно)...${NC}"
if [ ! -L "$NGINX_ENABLED" ]; then
    ln -s "$NGINX_CONF" "$NGINX_ENABLED"
    echo -e "${GREEN}✅ Символическая ссылка создана${NC}"
else
    echo -e "${GREEN}✅ Символическая ссылка уже существует${NC}"
fi

echo -e "${YELLOW}📋 Шаг 4: Проверка конфигурации nginx...${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Конфигурация nginx корректна${NC}"
else
    echo -e "${RED}❌ Ошибка в конфигурации nginx!${NC}"
    echo -e "${YELLOW}Восстанавливаем резервную копию...${NC}"
    LATEST_BACKUP=$(ls -t ${NGINX_CONF}.backup.* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        cp "$LATEST_BACKUP" "$NGINX_CONF"
        echo -e "${GREEN}✅ Резервная копия восстановлена${NC}"
    fi
    exit 1
fi

echo -e "${YELLOW}📋 Шаг 5: Перезагрузка nginx...${NC}"
if systemctl reload nginx; then
    echo -e "${GREEN}✅ Nginx успешно перезагружен${NC}"
else
    echo -e "${RED}❌ Ошибка при перезагрузке nginx!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Готово! Nginx конфигурация успешно применена${NC}"
echo ""
echo -e "${YELLOW}📝 Следующие шаги:${NC}"
echo "1. Откройте ваш сайт: https://novel-cloudtech.com:7443/"
echo "2. Обновите страницу (Ctrl+F5)"
echo "3. Grafana должна загрузиться корректно"
echo "4. Подождите 10-15 секунд для загрузки данных"
echo ""
echo -e "${YELLOW}🔍 Проверка:${NC}"
echo "curl -I https://novel-cloudtech.com:7443/grafana/"
echo ""
echo -e "${YELLOW}📖 Логи nginx:${NC}"
echo "sudo tail -f /var/log/nginx/novel-cloudtech.com.error.log"
