# Детальный анализ проблемы с графиками Grafana

## 📊 Резюме проблемы

Grafana не отображает графики из-за **неправильной конфигурации источника данных PostgreSQL**.

---

## 🔍 Детальный анализ

### 1. Основная проблема: Неверный хост базы данных

**Файл:** `grafana/provisioning/datasources/postgres.yml`

**Проблема:**
```yaml
url: postgres:5432  # ❌ НЕПРАВИЛЬНО
```

**Причина:**
В файле [`docker-compose.yml`](docker-compose.yml:26) сервис PostgreSQL называется `db`, а не `postgres`:

```yaml
services:
  db:                              # ← Имя сервиса
    image: postgres:16-alpine
    container_name: leetcode-tracker-db  # ← Имя контейнера
```

**Последствия:**
- Grafana не может подключиться к базе данных
- Все SQL-запросы в дашбордах терпят неудачу
- Графики остаются пустыми с ошибкой подключения

### 2. Отсутствие явных зависимостей

**Файл:** `docker-compose.yml`

**Проблема:**
```yaml
grafana:
  # ...
  depends_on:
    - prometheus  # ✗ Нет зависимости от db
```

**Последствия:**
- Grafana может запуститься раньше PostgreSQL
- Возникают race conditions при старте
- Источник данных может не инициализироваться корректно

---

## ✅ Исправления

### 1. Исправлен URL источника данных

**Файл:** `grafana/provisioning/datasources/postgres.yml`

```diff
- url: postgres:5432
+ url: db:5432
```

Теперь Grafana будет подключаться к правильному хосту через Docker network.

### 2. Добавлены зависимости в docker-compose.yml

**Файл:** `docker-compose.yml`

```yaml
grafana:
  # ...
  depends_on:
    db:
      condition: service_healthy  # ✓ Ждем пока PostgreSQL готов
    prometheus:
      condition: service_started  # ✓ Ждем запуска Prometheus
```

**Преимущества:**
- Grafana запускается только после PostgreSQL
- PostgreSQL проходит health check перед запуском Grafana
- Корректный порядок инициализации сервисов

---

## 🎯 Архитектура подключения

```
┌─────────────────────────────────────────────────┐
│         Docker Network (leetcode_tracker)       │
│                                                  │
│  ┌──────────┐         ┌──────────────────┐     │
│  │          │         │                  │     │
│  │  Grafana │────────▶│  PostgreSQL (db) │     │
│  │          │  db:5432│                  │     │
│  └──────────┘         └──────────────────┘     │
│                                                  │
│  Grafana подключается к PostgreSQL через        │
│  внутреннее имя сервиса "db" в Docker network   │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 📋 SQL-запросы дашборда

Дашборд [`leetcode-tracker.json`](grafana/provisioning/dashboards/json/leetcode-tracker.json) выполняет следующие запросы:

### Panel 1: Total Tasks Solved
```sql
SELECT COUNT(*) as total FROM solved_tasks
```

### Panel 2: Total XP
```sql
SELECT COALESCE(SUM(points), 0) as total_xp FROM solved_tasks
```

### Panel 3: Active Users
```sql
SELECT COUNT(*) as active_users FROM users
```

### Panel 4: Avg Time per Task
```sql
SELECT COALESCE(AVG(time_spent), 0) as avg_time 
FROM solved_tasks 
WHERE time_spent IS NOT NULL
```

### Panel 5: Tasks Solved Over Time (График времени)
```sql
SELECT date as time, COUNT(*) as tasks_count 
FROM solved_tasks 
GROUP BY date 
ORDER BY date
```

### Panel 6: Tasks by Difficulty (Pie Chart)
```sql
SELECT difficulty, COUNT(*) as count 
FROM solved_tasks 
GROUP BY difficulty
```

### Panel 7: Top Users Leaderboard
```sql
SELECT u.username, u.ranking, u.reputation, u.total_solved, 
       u.easy_solved, u.medium_solved, u.hard_solved, 
       COALESCE(SUM(t.points), 0) as total_xp 
FROM users u 
LEFT JOIN solved_tasks t ON u.id = t.user_id 
GROUP BY u.id, u.username, u.ranking, u.reputation, 
         u.total_solved, u.easy_solved, u.medium_solved, u.hard_solved 
ORDER BY total_xp DESC 
LIMIT 10
```

### Panel 8: Recent Tasks
```sql
SELECT t.title, t.difficulty, t.date, u.username 
FROM solved_tasks t 
JOIN users u ON t.user_id = u.id 
ORDER BY t.date DESC 
LIMIT 20
```

**Все эти запросы требуют правильного подключения к PostgreSQL!**

---

## 🗄️ Структура базы данных

Из файла [`leetcode_tracker/models.py`](leetcode_tracker/models.py):

### Таблица: users
```python
id              INTEGER       PRIMARY KEY
email           VARCHAR(255)  UNIQUE, NULLABLE
username        VARCHAR(100)  UNIQUE, NOT NULL
oauth_provider  VARCHAR(20)   NULLABLE
oauth_id        VARCHAR(255)  NULLABLE
avatar_url      VARCHAR(500)  NULLABLE
leetcode_username VARCHAR(100) NULLABLE
ranking         INTEGER       NULLABLE
reputation      INTEGER       NULLABLE
total_solved    INTEGER       NULLABLE
easy_solved     INTEGER       NULLABLE
medium_solved   INTEGER       NULLABLE
hard_solved     INTEGER       NULLABLE
last_synced_at  DATETIME      NULLABLE
created_at      DATETIME      DEFAULT NOW()
```

### Таблица: solved_tasks
```python
id          INTEGER      PRIMARY KEY
user_id     INTEGER      FOREIGN KEY → users.id
date        DATE         NOT NULL
platform    VARCHAR(50)  DEFAULT 'leetcode'
problem_id  VARCHAR(50)  NULLABLE
title       VARCHAR(200) NULLABLE
difficulty  VARCHAR(10)  NOT NULL  # Easy/Medium/Hard
points      INTEGER      NOT NULL  # XP
time_spent  INTEGER      NULLABLE  # Minutes
notes       TEXT         NULLABLE
created_at  DATETIME     DEFAULT NOW()
```

### Таблица: month_goals
```python
id         INTEGER  PRIMARY KEY
user_id    INTEGER  FOREIGN KEY → users.id
year       INTEGER  NOT NULL
month      INTEGER  NOT NULL  # 1-12
target_xp  INTEGER  DEFAULT 100
created_at DATETIME DEFAULT NOW()
```

---

## 🛠️ Инструкция по применению исправлений

### Автоматическое исправление (Рекомендуется)

Выполните скрипт:

```bash
bash fix_grafana.sh
```

Скрипт автоматически:
1. ✅ Остановит контейнер Grafana
2. ✅ Удалит старый контейнер
3. ✅ Создаст новый контейнер с исправленной конфигурацией
4. ✅ Проверит подключение к базе данных
5. ✅ Выведет статус и инструкции

### Ручное исправление

```bash
# 1. Остановить и удалить контейнер Grafana
docker stop grafana
docker rm grafana

# 2. Пересоздать контейнер с новой конфигурацией
docker-compose up -d grafana

# 3. Проверить логи
docker logs -f grafana
```

### Проверка исправлений

```bash
# Проверить, что Grafana может подключиться к PostgreSQL
docker exec grafana sh -c "nc -zv db 5432"

# Проверить данные в базе
docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "
SELECT 
  (SELECT COUNT(*) FROM users) as users,
  (SELECT COUNT(*) FROM solved_tasks) as tasks,
  (SELECT COUNT(*) FROM month_goals) as goals;
"
```

---

## 🧪 Создание тестовых данных

Если в базе нет данных, графики будут пустыми. Создайте тестовые данные:

```bash
# Вариант 1: Используя существующий скрипт
cd e:/leetcode_tracker_uv
python scripts/create_test_data.py

# Вариант 2: Через веб-интерфейс приложения
# 1. Войдите в приложение
# 2. Добавьте задачи вручную через форму

# Вариант 3: Синхронизация с LeetCode
# 1. Настройте leetcode_username в профиле
# 2. Используйте функцию синхронизации
```

---

## 📝 Чек-лист проверки

После применения исправлений, проверьте:

- [ ] Docker контейнеры запущены:
  ```bash
  docker-compose ps
  ```

- [ ] Grafana доступна:
  - Локально: http://localhost:3000
  - Удаленно: https://novel-cloudtech.com:7443/grafana/

- [ ] Источник данных работает:
  - Configuration → Data Sources → LeetCode Tracker PostgreSQL
  - Нажать "Test" → "Database Connection OK"

- [ ] Дашборд загружается:
  - Dashboards → LeetCode Tracker Dashboard
  - Графики отображаются (если есть данные)

- [ ] Данные в базе:
  ```bash
  bash diagnose_grafana.sh
  ```

---

## 🚨 Типичные ошибки и решения

### Ошибка: "Database Connection Error"

**Причина:** Grafana не может подключиться к PostgreSQL

**Решение:**
1. Проверьте, что PostgreSQL запущен: `docker ps | grep postgres`
2. Проверьте URL в `postgres.yml`: должно быть `db:5432`
3. Перезапустите Grafana: `bash fix_grafana.sh`

### Ошибка: "No data" в графиках

**Причина:** В базе данных нет данных

**Решение:**
1. Проверьте наличие данных:
   ```bash
   docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) FROM solved_tasks;"
   ```
2. Создайте тестовые данные: `python scripts/create_test_data.py`

### Ошибка: "Failed to load dashboards"

**Причина:** Проблемы с provisioning

**Решение:**
1. Проверьте, что файлы provisioning mounted:
   ```bash
   docker exec grafana ls -la /etc/grafana/provisioning/datasources/
   docker exec grafana ls -la /etc/grafana/provisioning/dashboards/
   ```
2. Проверьте права доступа к файлам
3. Пересоздайте контейнер: `bash fix_grafana.sh`

---

## 📊 Ожидаемый результат

После исправления вы должны увидеть:

1. **Статистические панели (Stat):**
   - Total Tasks Solved: число решенных задач
   - Total XP: общее количество очков опыта
   - Active Users: количество активных пользователей
   - Avg Time per Task: среднее время на задачу (в минутах)

2. **График времени (Time Series):**
   - Tasks Solved Over Time: линейный график решенных задач по датам

3. **Круговая диаграмма (Pie Chart):**
   - Tasks by Difficulty: распределение задач по сложности (Easy/Medium/Hard)

4. **Таблицы (Table):**
   - Top Users Leaderboard: топ пользователей с их статистикой
   - Recent Tasks: последние 20 решенных задач

---

## 🔧 Дополнительные команды диагностики

```bash
# Проверить все контейнеры
docker-compose ps

# Проверить логи Grafana
docker logs grafana --tail 50

# Проверить логи PostgreSQL  
docker logs leetcode-tracker-db --tail 50

# Проверить сеть Docker
docker network inspect leetcode_tracker_uv_default

# Войти в контейнер Grafana
docker exec -it grafana sh

# Проверить конфигурацию datasource внутри контейнера
docker exec grafana cat /etc/grafana/provisioning/datasources/postgres.yml

# Проверить наличие дашборда
docker exec grafana cat /etc/grafana/provisioning/dashboards/json/leetcode-tracker.json

# Тест подключения из Grafana к PostgreSQL
docker exec grafana sh -c "nc -zv db 5432"
```

---

## 📚 Дополнительная документация

- [`GRAFANA_FIX_INSTRUCTIONS.md`](GRAFANA_FIX_INSTRUCTIONS.md) - Подробная инструкция по исправлению
- [`diagnose_grafana.sh`](diagnose_grafana.sh) - Скрипт диагностики
- [`fix_grafana.sh`](fix_grafana.sh) - Скрипт автоматического исправления
- [`docker-compose.yml`](docker-compose.yml) - Конфигурация Docker Compose
- [`grafana/provisioning/datasources/postgres.yml`](grafana/provisioning/datasources/postgres.yml) - Конфигурация источника данных
- [`grafana/provisioning/dashboards/json/leetcode-tracker.json`](grafana/provisioning/dashboards/json/leetcode-tracker.json) - Дашборд Grafana

---

## ✅ Выводы

1. **Основная проблема:** Неверное имя хоста PostgreSQL в конфигурации Grafana (`postgres` вместо `db`)

2. **Исправление:** Изменен URL с `postgres:5432` на `db:5432` в файле `postgres.yml`

3. **Дополнительно:** Добавлены явные зависимости в `docker-compose.yml` для правильного порядка запуска

4. **Применение:** Выполните `bash fix_grafana.sh` для автоматического исправления

5. **Проверка:** После исправления откройте Grafana и проверьте источник данных и дашборд

---

**Дата анализа:** 2025-12-16  
**Статус:** ✅ Проблема идентифицирована и исправлена  
**Автор:** Kilo Code AI Assistant
