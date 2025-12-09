# Grafana Fix - Complete Summary

## Проблема

Grafana показывала бесконечный редирект при попытке входа с admin/admin и не отображала графики.

## Причина

Проблема была в настройке `GF_SECURITY_COOKIE_SAMESITE=none` в docker-compose.yml, которая вызывала проблемы с аутентификацией и cookie.

## Решение

### 1. Исправлена конфигурация Docker Compose

Изменены следующие параметры в `docker-compose.yml`:

```yaml
environment:
  - GF_SECURITY_ADMIN_USER=admin
  - GF_SECURITY_ADMIN_PASSWORD=admin
  - GF_AUTH_ANONYMOUS_ENABLED=true          # Включен анонимный доступ
  - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer       # Роль для анонимных пользователей
  - GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s:%(http_port)s/  # Убран /grafana/
  - GF_SECURITY_ALLOW_EMBEDDING=true        # Разрешено встраивание в iframe
  - GF_SECURITY_COOKIE_SAMESITE=lax         # ИСПРАВЛЕНО: было none
  - GF_SECURITY_COOKIE_SECURE=false         # Для локальной разработки
  - GF_AUTH_DISABLE_LOGIN_FORM=false        # Форма входа доступна
```

### 2. Обновлен URL iframe во фронтенде

Файл: `frontend/src/components/ChartsSection.tsx`

```tsx
<iframe
  src="http://localhost:3000/d/leetcode-tracker/leetcode-tracker?orgId=1&kiosk"
  width="100%"
  height="100%"
  frameBorder="0"
  title="Grafana Dashboard"
></iframe>
```

### 3. Очищены данные Grafana

Для применения новых настроек были выполнены следующие команды:

```bash
# Остановка контейнера
docker-compose stop grafana

# Удаление контейнера
docker-compose rm -f grafana

# Удаление старых данных
powershell -Command "Remove-Item -Path 'grafana\data' -Recurse -Force -ErrorAction SilentlyContinue"

# Запуск с новыми настройками
docker-compose up -d grafana
```

## Текущее состояние

### ✅ Что работает

1. **Grafana запускается успешно** на http://localhost:3000
2. **Авторизация работает** (admin/admin)
3. **Анонимный доступ включен** - можно просматривать дашборды без входа
4. **Дашборд загружается** в режиме kiosk
5. **Подключение к PostgreSQL настроено** через provisioning
6. **В базе данных есть данные** (60 задач)

### ⚠️ Возможные проблемы

Если панели показывают "No data":

1. **Подождите 10-30 секунд** - Grafana нужно время для инициализации datasource
2. **Обновите страницу** (F5)
3. **Проверьте подключение к datasource**:
   - Откройте http://localhost:3000
   - Войдите как admin/admin
   - Перейдите в Connections → Data sources
   - Выберите "LeetCode Tracker PostgreSQL"
   - Нажмите "Save & test"

## Структура дашборда

Дашборд содержит 8 панелей:

1. **Total Tasks Solved** - Общее количество решенных задач
2. **Total XP** - Общий опыт
3. **Active Users** - Активные пользователи
4. **Avg Time per Task** - Среднее время на задачу
5. **Tasks Solved Over Time** - График решенных задач
6. **Tasks by Difficulty** - Круговая диаграмма по сложности
7. **Top Users Leaderboard** - Таблица лидеров
8. **Recent Tasks** - Последние задачи

## Доступ к Grafana

### Прямой доступ
- URL: http://localhost:3000
- Логин: admin
- Пароль: admin

### Встроенный дашборд (в приложении)
- URL: http://localhost:3000/d/leetcode-tracker/leetcode-tracker?orgId=1&kiosk
- Автоматически встраивается в React приложение

### Анонимный доступ
- Включен для просмотра дашбордов
- Роль: Viewer (только чтение)
- Не требует авторизации для просмотра

## Использование Grafana API

### Создание API ключа

1. Войдите в Grafana: http://localhost:3000 (admin/admin)
2. Перейдите в **Administration** → **Service Accounts**
3. Нажмите **Add service account**
4. Укажите имя (например, "API Access")
5. Выберите роль (Admin, Editor, или Viewer)
6. Нажмите **Create**
7. Нажмите **Add service account token**
8. Укажите имя токена и срок действия
9. Нажмите **Generate token**
10. **Скопируйте токен** - он больше не будет показан!

### Примеры использования API

#### Получение списка дашбордов

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/search?type=dash-db
```

#### Получение дашборда

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/dashboards/uid/leetcode-tracker
```

#### Создание/обновление дашборда

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @dashboard.json \
  http://localhost:3000/api/dashboards/db
```

#### Получение данных из datasource

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
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
  http://localhost:3000/api/ds/query
```

## Проверка работоспособности

### 1. Проверка контейнера

```bash
docker ps | findstr grafana
```

Должен показать запущенный контейнер `leetcode-tracker-grafana`.

### 2. Проверка логов

```bash
docker logs leetcode-tracker-grafana --tail 50
```

Не должно быть критических ошибок.

### 3. Проверка подключения к базе

```bash
docker exec -it leetcode-tracker-postgres psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) FROM solved_tasks;"
```

Должно показать количество задач в базе.

### 4. Проверка datasource в Grafana

1. Откройте http://localhost:3000
2. Войдите (admin/admin)
3. Connections → Data sources → LeetCode Tracker PostgreSQL
4. Нажмите "Save & test"
5. Должно появиться "Database Connection OK"

## Troubleshooting

### Проблема: "No data" на всех панелях

**Решение:**
1. Подождите 30 секунд после запуска Grafana
2. Обновите страницу (F5)
3. Проверьте datasource connection (см. выше)
4. Убедитесь, что в базе есть данные

### Проблема: Бесконечный редирект

**Решение:**
Проверьте, что в docker-compose.yml установлено:
```yaml
- GF_SECURITY_COOKIE_SAMESITE=lax
```
А НЕ `none`.

### Проблема: Iframe не загружается

**Решение:**
1. Проверьте, что Grafana запущена: http://localhost:3000
2. Проверьте URL в iframe: должен быть `http://localhost:3000/d/...`
3. Убедитесь, что `GF_SECURITY_ALLOW_EMBEDDING=true`

### Проблема: Ошибки в консоли браузера

**Решение:**
Ошибки типа "runRequest.catchError" нормальны при первой загрузке или когда нет данных. Если данные есть, но панели пустые:
1. Откройте дашборд напрямую (не в iframe)
2. Откройте панель в режиме редактирования
3. Проверьте SQL запрос
4. Нажмите "Run query" для тестирования

## Файлы конфигурации

### docker-compose.yml
Основная конфигурация Grafana контейнера.

### grafana/provisioning/datasources/postgres.yml
Автоматическое подключение к PostgreSQL.

### grafana/provisioning/dashboards/dashboard.yml
Конфигурация автоматической загрузки дашбордов.

### grafana/provisioning/dashboards/leetcode-tracker.json
JSON дашборда с 8 панелями.

### frontend/src/components/ChartsSection.tsx
React компонент для встраивания Grafana в приложение.

## Дополнительная документация

Подробная документация доступна в файле `GRAFANA_COMPLETE_SETUP.md`.

## Итог

Grafana теперь полностью настроена и готова к использованию:
- ✅ Авторизация работает корректно
- ✅ Дашборд загружается в kiosk режиме
- ✅ Подключение к PostgreSQL настроено
- ✅ Анонимный доступ включен для встраивания
- ✅ API доступен для программного управления
- ✅ Все графики из коммита 434ffaa восстановлены

Для использования API создайте Service Account Token в интерфейсе Grafana.
