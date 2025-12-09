# Grafana Setup Guide - Complete Configuration

## Обзор

Grafana настроена для отображения графиков и статистики LeetCode Tracker. Дашборд автоматически загружается через provisioning и подключается к PostgreSQL базе данных.

## Текущая конфигурация

### Docker Compose настройки

Grafana запускается с следующими параметрами:

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: leetcode-tracker-grafana
  restart: unless-stopped
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_AUTH_ANONYMOUS_ENABLED=true
    - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
    - GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s:%(http_port)s/
    - GF_SECURITY_ALLOW_EMBEDDING=true
    - GF_SECURITY_COOKIE_SAMESITE=lax
    - GF_SECURITY_COOKIE_SECURE=false
    - GF_AUTH_DISABLE_LOGIN_FORM=false
```

### Ключевые настройки

1. **Анонимный доступ включен** (`GF_AUTH_ANONYMOUS_ENABLED=true`)
   - Позволяет просматривать дашборды без авторизации
   - Роль: Viewer (только просмотр)

2. **Embedding разрешен** (`GF_SECURITY_ALLOW_EMBEDDING=true`)
   - Позволяет встраивать Grafana в iframe на фронтенде

3. **Cookie настройки**
   - `GF_SECURITY_COOKIE_SAMESITE=lax` - исправляет проблему с бесконечным редиректом
   - `GF_SECURITY_COOKIE_SECURE=false` - для локальной разработки

## Доступ к Grafana

### Прямой доступ
- URL: http://localhost:3000
- Логин: admin
- Пароль: admin

### Встроенный дашборд (в приложении)
- URL дашборда: http://localhost:3000/d/leetcode-tracker/leetcode-tracker?orgId=1&kiosk
- Параметр `kiosk` скрывает меню Grafana для чистого отображения

## Структура файлов

```
grafana/
├── data/                          # Данные Grafana (создается автоматически)
└── provisioning/
    ├── dashboards/
    │   ├── dashboard.yml          # Конфигурация провижининга дашбордов
    │   └── leetcode-tracker.json  # JSON дашборда
    └── datasources/
        └── postgres.yml           # Подключение к PostgreSQL
```

## Дашборд

### Панели дашборда

1. **Total Tasks Solved** - Общее количество решенных задач
2. **Total XP** - Общее количество опыта
3. **Active Users** - Количество активных пользователей
4. **Avg Time per Task** - Среднее время на задачу (в минутах)
5. **Tasks Solved Over Time** - График решенных задач по времени
6. **Tasks by Difficulty** - Круговая диаграмма по сложности
7. **Top Users Leaderboard** - Таблица лидеров
8. **Recent Tasks** - Последние решенные задачи

### Автообновление

Дашборд настроен на автообновление каждые 5 секунд (`"refresh": "5s"`).

## Подключение к базе данных

### PostgreSQL Datasource

Конфигурация в `grafana/provisioning/datasources/postgres.yml`:

```yaml
apiVersion: 1

datasources:
  - name: LeetCode Tracker PostgreSQL
    type: postgres
    uid: leetcode-tracker-postgres
    access: proxy
    url: postgres:5432
    database: leetcode_tracker
    user: leetcode_user
    secureJsonData:
      password: leetcode_password
    jsonData:
      sslmode: disable
      postgresVersion: 1600
      timescaledb: false
    isDefault: true
    editable: true
```

## Использование Grafana API

### Получение API ключа

1. Войдите в Grafana: http://localhost:3000
2. Перейдите в Configuration → API Keys (или Service Accounts в новых версиях)
3. Создайте новый API ключ с нужными правами
4. Сохраните ключ в безопасном месте

### Примеры использования API

#### Получение списка дашбордов

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/search?type=dash-db
```

#### Получение дашборда по UID

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

## Troubleshooting

### Проблема: Бесконечный редирект при входе

**Решение:** Проверьте настройку `GF_SECURITY_COOKIE_SAMESITE`:
- Должно быть `lax` или `disabled`
- НЕ должно быть `none` (вызывает проблемы с авторизацией)

### Проблема: Дашборд не загружается

**Решение:**
1. Проверьте логи Grafana:
   ```bash
   docker logs leetcode-tracker-grafana
   ```

2. Убедитесь, что PostgreSQL доступен:
   ```bash
   docker exec leetcode-tracker-grafana ping postgres
   ```

3. Проверьте provisioning файлы на ошибки

### Проблема: Данные не отображаются

**Решение:**
1. Проверьте подключение к базе данных в Grafana UI
2. Убедитесь, что в базе есть данные:
   ```bash
   docker exec -it leetcode-tracker-postgres psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) FROM solved_tasks;"
   ```

### Сброс Grafana к начальному состоянию

Если нужно полностью сбросить Grafana:

```bash
# Остановить контейнер
docker-compose stop grafana

# Удалить контейнер
docker-compose rm -f grafana

# Удалить данные
powershell -Command "Remove-Item -Path 'grafana\data' -Recurse -Force -ErrorAction SilentlyContinue"

# Запустить заново
docker-compose up -d grafana
```

## Интеграция с фронтендом

Дашборд встраивается в React компонент `ChartsSection.tsx`:

```tsx
<iframe
  src="http://localhost:3000/d/leetcode-tracker/leetcode-tracker?orgId=1&kiosk"
  width="100%"
  height="100%"
  frameBorder="0"
  title="Grafana Dashboard"
></iframe>
```

### Параметры URL

- `orgId=1` - ID организации (по умолчанию 1)
- `kiosk` - режим киоска (скрывает меню и панели Grafana)
- `theme=dark` - можно добавить для темной темы
- `from=now-7d&to=now` - можно добавить для установки временного диапазона

## Безопасность

### Для продакшена

1. **Измените пароль администратора:**
   ```yaml
   - GF_SECURITY_ADMIN_PASSWORD=strong_password_here
   ```

2. **Отключите анонимный доступ** (если не нужен):
   ```yaml
   - GF_AUTH_ANONYMOUS_ENABLED=false
   ```

3. **Включите HTTPS:**
   ```yaml
   - GF_SECURITY_COOKIE_SECURE=true
   - GF_SERVER_PROTOCOL=https
   ```

4. **Используйте переменные окружения** для паролей:
   ```yaml
   - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
   ```

## Дополнительные ресурсы

- [Grafana Documentation](https://grafana.com/docs/)
- [Grafana HTTP API](https://grafana.com/docs/grafana/latest/developers/http_api/)
- [Provisioning Grafana](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [PostgreSQL Data Source](https://grafana.com/docs/grafana/latest/datasources/postgres/)
