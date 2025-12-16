# Инструкция по исправлению проблемы с графиками Grafana

## Обнаруженная проблема

В файле `grafana/provisioning/datasources/postgres.yml` был указан **неверный хост базы данных PostgreSQL**:

```yaml
url: postgres:5432  # ❌ НЕВЕРНО
```

В `docker-compose.yml` сервис PostgreSQL называется `db`, а не `postgres`:

```yaml
db:
  image: postgres:16-alpine
  container_name: leetcode-tracker-db
```

## Что было исправлено

### 1. Исправлен URL источника данных PostgreSQL

**Файл:** `grafana/provisioning/datasources/postgres.yml`

**Изменение:**
```yaml
url: db:5432  # ✅ ПРАВИЛЬНО
```

### 2. Добавлены зависимости в docker-compose.yml

**Файл:** `docker-compose.yml`

Добавлены правильные зависимости для Grafana:
```yaml
depends_on:
  db:
    condition: service_healthy
  prometheus:
    condition: service_started
```

Это гарантирует, что Grafana запустится только после того, как:
- PostgreSQL полностью запущена и готова принимать соединения
- Prometheus запущен

## Инструкция по применению исправлений

### Вариант 1: Пересоздание контейнера Grafana (Рекомендуется)

Выполните следующие команды в терминале:

```bash
# 1. Остановите контейнер Grafana
docker stop grafana

# 2. Удалите контейнер Grafana
docker rm grafana

# 3. Пересоздайте и запустите контейнер Grafana с новой конфигурацией
docker-compose up -d grafana

# 4. Проверьте логи Grafana для убедитесь, что нет ошибок
docker logs -f grafana
```

### Вариант 2: Перезапуск всего стека (Если Вариант 1 не помог)

```bash
# 1. Остановите все контейнеры
docker-compose down

# 2. Запустите все контейнеры заново
docker-compose up -d

# 3. Проверьте статус всех контейнеров
docker-compose ps

# 4. Проверьте логи Grafana
docker logs -f grafana
```

### Вариант 3: Полная очистка и пересоздание (Крайний случай)

⚠️ **ВНИМАНИЕ:** Это удалит все данные Grafana (дашборды, настройки и т.д.)

```bash
# 1. Остановите все контейнеры
docker-compose down

# 2. Удалите том Grafana
docker volume rm leetcode_tracker_uv_grafana_data

# 3. Запустите контейнеры заново
docker-compose up -d

# 4. Проверьте логи
docker logs -f grafana
```

## Проверка работоспособности

### 1. Проверка подключения к базе данных

Выполните скрипт диагностики:

```bash
bash diagnose_grafana.sh
```

### 2. Проверка через веб-интерфейс Grafana

1. Откройте Grafana в браузере:
   - Локально: http://localhost:3000
   - Удаленно: https://novel-cloudtech.com:7443/grafana/

2. Войдите с учетными данными:
   - **Username:** admin
   - **Password:** admin

3. Проверьте источник данных:
   - Перейдите в **Configuration → Data Sources**
   - Найдите **LeetCode Tracker PostgreSQL**
   - Нажмите **Test** - должно быть сообщение "Database Connection OK"

4. Проверьте дашборд:
   - Перейдите в **Dashboards**
   - Откройте **LeetCode Tracker Dashboard**
   - Графики должны отображаться с данными

### 3. Проверка данных в базе данных

Убедитесь, что в базе данных есть данные:

```bash
# Проверка пользователей
docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) FROM users;"

# Проверка задач
docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) FROM solved_tasks;"
```

Если в базе нет данных, графики будут пустыми. В этом случае:
- Войдите в приложение и добавьте задачи
- Или используйте скрипт создания тестовых данных:

```bash
cd scripts
python create_test_data.py
```

## Типичные проблемы и решения

### Проблема: "Database Connection Error" в Grafana

**Решение:**
1. Проверьте, что PostgreSQL запущен: `docker ps | grep postgres`
2. Проверьте логи PostgreSQL: `docker logs leetcode-tracker-db`
3. Убедитесь, что Grafana может достучаться до БД:
   ```bash
   docker exec grafana sh -c "nc -zv db 5432"
   ```

### Проблема: "No data" в графиках

**Причина:** В базе данных нет данных

**Решение:**
1. Добавьте задачи через веб-интерфейс приложения
2. Используйте скрипт создания тестовых данных (см. выше)
3. Синхронизируйте данные с LeetCode (если настроено)

### Проблема: Grafana недоступна по URL

**Решение:**
1. Проверьте, что контейнер запущен: `docker ps | grep grafana`
2. Проверьте порты: `docker port grafana`
3. Проверьте логи: `docker logs grafana`
4. Убедитесь, что порт 3000 не занят другим процессом

## Дополнительные команды для диагностики

```bash
# Посмотреть все контейнеры
docker-compose ps

# Посмотреть логи Grafana в реальном времени
docker logs -f grafana

# Посмотреть логи PostgreSQL
docker logs leetcode-tracker-db

# Проверить сеть Docker
docker network inspect leetcode_tracker_uv_default

# Войти в контейнер Grafana
docker exec -it grafana sh

# Проверить файлы provisioning внутри Grafana
docker exec grafana ls -la /etc/grafana/provisioning/datasources/
docker exec grafana cat /etc/grafana/provisioning/datasources/postgres.yml
```

## Контакты и поддержка

Если проблема не решена, предоставьте следующую информацию:

1. Вывод команды `docker-compose ps`
2. Логи Grafana: `docker logs grafana`
3. Логи PostgreSQL: `docker logs leetcode-tracker-db`
4. Результат проверки подключения: `docker exec grafana sh -c "nc -zv db 5432"`

---

**Дата создания:** 2025-12-16
**Версия:** 1.0
