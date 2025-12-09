# Grafana Deployment Guide - Финальная инструкция

## 🎯 Что было исправлено

### Проблема
Grafana не загружалась через reverse proxy и показывала ошибку "failed to load its application files".

### Причина
Неправильная конфигурация nginx - двойное добавление `/grafana/` к путям.

### Решение
Изменена строка `proxy_pass` в nginx конфигурации.

## 📋 Инструкция по деплою

### Вариант 1: Автоматический деплой (рекомендуется)

На вашем сервере выполните:

```bash
# 1. Перейдите в директорию проекта
cd /path/to/leetcode_tracker_uv

# 2. Загрузите последние изменения из git
git pull

# 3. Сделайте скрипт исполняемым
chmod +x deploy_nginx_fix.sh

# 4. Запустите скрипт с sudo
sudo bash deploy_nginx_fix.sh
```

Скрипт автоматически:
- Создаст резервную копию текущей конфигурации
- Применит исправленную конфигурацию
- Проверит корректность
- Перезагрузит nginx

### Вариант 2: Ручной деплой

```bash
# 1. Создайте резервную копию
sudo cp /etc/nginx/sites-available/leetcode-tracker /etc/nginx/sites-available/leetcode-tracker.backup

# 2. Скопируйте новую конфигурацию
sudo cp nginx-leetcode-tracker.conf /etc/nginx/sites-available/leetcode-tracker

# 3. Проверьте конфигурацию
sudo nginx -t

# 4. Если проверка успешна, перезагрузите nginx
sudo systemctl reload nginx
```

### Вариант 3: Ручное редактирование

Если вы хотите отредактировать файл вручную:

```bash
sudo nano /etc/nginx/sites-available/leetcode-tracker
```

Найдите секцию:
```nginx
location /grafana/ {
    proxy_pass http://127.0.0.1:3000/grafana/;  # ❌ Удалите /grafana/ в конце
```

Измените на:
```nginx
location /grafana/ {
    proxy_pass http://127.0.0.1:3000;  # ✅ Без /grafana/ в конце
```

Затем:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## ✅ Проверка после деплоя

### 1. Проверка nginx

```bash
# Проверка статуса
sudo systemctl status nginx

# Проверка логов
sudo tail -f /var/log/nginx/novel-cloudtech.com.error.log
```

### 2. Проверка Grafana

```bash
# Проверка доступности
curl -I https://novel-cloudtech.com:7443/grafana/

# Должен вернуть 200 OK или 302 Found
```

### 3. Проверка в браузере

1. Откройте https://novel-cloudtech.com:7443/
2. Нажмите Ctrl+F5 для полной перезагрузки
3. Grafana должна загрузиться корректно
4. Подождите 10-15 секунд для загрузки данных из PostgreSQL

## 🔧 Итоговая конфигурация

### Docker Compose (уже настроено)

```yaml
grafana:
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_AUTH_ANONYMOUS_ENABLED=true
    - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
    - GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s:%(http_port)s/grafana/
    - GF_SERVER_SERVE_FROM_SUB_PATH=true
    - GF_SECURITY_ALLOW_EMBEDDING=true
    - GF_SECURITY_COOKIE_SAMESITE=lax
    - GF_SECURITY_COOKIE_SECURE=false
```

### Nginx (исправлено)

```nginx
location /grafana/ {
    proxy_pass http://127.0.0.1:3000;  # БЕЗ /grafana/ в конце!
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Port $server_port;
    
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

### Frontend (уже настроено)

```tsx
<iframe src="/grafana/d/leetcode-tracker/leetcode-tracker?orgId=1&kiosk" />
```

## 🐛 Troubleshooting

### Проблема: Nginx не перезагружается

```bash
# Проверьте синтаксис
sudo nginx -t

# Посмотрите логи
sudo journalctl -u nginx -n 50

# Перезапустите nginx (если reload не помогает)
sudo systemctl restart nginx
```

### Проблема: Grafana все еще не загружается

```bash
# Проверьте, что Grafana запущена
docker ps | grep grafana

# Проверьте логи Grafana
docker logs leetcode-tracker-grafana --tail 50

# Перезапустите Grafana
docker-compose restart grafana
```

### Проблема: "No data" на панелях

1. Подождите 30 секунд после загрузки
2. Обновите страницу (F5)
3. Проверьте datasource:
   - Откройте https://novel-cloudtech.com:7443/grafana/
   - Войдите (admin/admin)
   - Connections → Data sources → LeetCode Tracker PostgreSQL
   - Нажмите "Save & test"

## 📊 Использование Grafana API

После успешного деплоя вы можете использовать Grafana API:

### 1. Создание API токена

1. Откройте https://novel-cloudtech.com:7443/grafana/
2. Войдите (admin/admin)
3. Administration → Service Accounts
4. Add service account
5. Создайте токен

### 2. Примеры API запросов

```bash
# Получение списка дашбордов
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://novel-cloudtech.com:7443/grafana/api/search?type=dash-db

# Получение дашборда
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://novel-cloudtech.com:7443/grafana/api/dashboards/uid/leetcode-tracker

# Запрос данных
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [{
      "refId": "A",
      "datasource": {"uid": "leetcode-tracker-postgres"},
      "rawSql": "SELECT COUNT(*) FROM solved_tasks",
      "format": "table"
    }],
    "from": "now-1h",
    "to": "now"
  }' \
  https://novel-cloudtech.com:7443/grafana/api/ds/query
```

## 📁 Файлы проекта

- `nginx-leetcode-tracker.conf` - Исправленная nginx конфигурация
- `deploy_nginx_fix.sh` - Скрипт автоматического деплоя
- `docker-compose.yml` - Конфигурация Docker (уже настроена)
- `frontend/src/components/ChartsSection.tsx` - React компонент с iframe

## 🎉 Итог

После применения этих изменений:

- ✅ Grafana загружается корректно через reverse proxy
- ✅ Все статические файлы загружаются
- ✅ Дашборд отображается в iframe
- ✅ Анонимный доступ работает
- ✅ API доступен для программного управления
- ✅ Все 8 панелей из коммита 434ffaa восстановлены

## 📖 Дополнительная документация

- `GRAFANA_COMPLETE_SETUP.md` - Полная документация по Grafana
- `GRAFANA_FIX_COMPLETE.md` - Краткое руководство по исправлению
- `GRAFANA_DOCKER_DESKTOP.md` - Настройка для Docker Desktop
- `GRAFANA_SETUP.md` - Базовая настройка

---

**Важно:** После деплоя обязательно проверьте работу Grafana в браузере!
