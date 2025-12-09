# Полный анализ проекта и план интеграции с Grafana

Этот документ содержит детальный анализ архитектуры проекта LeetCode Tracker, обзор текущей инфраструктуры, рекомендации по улучшению кода и безопасности, а также пошаговую инструкцию по внедрению мониторинга на базе Grafana.

---

## 1. Краткий обзор проекта и архитектуры

Ваш проект представляет собой **гибридное веб-приложение**:
- **Backend**: FastAPI (Python), запускается как системный сервис (systemd) прямо на хосте.
- **Frontend**: React (SPA), собирается в статические файлы и раздается самим FastAPI.
- **Database**: PostgreSQL, работает в Docker-контейнере.
- **Proxy**: Nginx, работает на хосте, терминирует SSL и проксирует запросы.

Это нестандартная "гибридная" схема (часть в Docker, часть на хосте), которая усложняет поддержку, но является полностью работоспособной.

### Архитектура (Текущая)

```mermaid
graph TD
    User[Пользователь (Browser)] -->|HTTPS :7443| Nginx[Nginx (Host)]
    Nginx -->|HTTP :8000| App[FastAPI App (Systemd Service)]
    Nginx -->|HTTP :3000| Grafana[Grafana (Docker - планируется)]
    
    subgraph Host [VPS Server]
        Nginx
        App
        
        subgraph Docker
            Postgres[PostgreSQL DB]
        end
    end
    
    App -->|SQL| Postgres
    App -->|HTTP| LeetCode[LeetCode API]
    App -->|Serve| Static[React Static Files]
```

---

## 2. Подробное описание работы приложения

1.  **Входная точка**: 
    - Запрос приходит на порт `7443` (SSL). 
    - Nginx расшифровывает его и передает на локальный адрес `127.0.0.1:8000`.
2.  **Приложение (FastAPI)**:
    -   Если запрос начинается с `/api`, он обрабатывается роутерами (`routers/`).
    -   Если запрос к корню `/` или другим путям, отдается `index.html` из папки `frontend/dist` (SPA).
3.  **Синхронизация (Background Sync)**:
    -   При старте приложения запускается фоновая задача `LeetCodeSyncService`.
    -   Каждые 10 секунд она перебирает **всех** пользователей, у которых установлен `leetcode_username`.
    -   Для каждого пользователя запрашивает последние 20 решений через API LeetCode.
    -   Новые решения сохраняются в БД `SolvedTask`.

---

## 3. Анализ деплоя и инфраструктуры

-   **Сервис**: `leetcode-tracker.service` запускает команду `uv run uvicorn ...` от имени пользователя `root`.
    -   ⚠️ **Риск**: Запуск веб-приложения от `root` — плохая практика безопасности. Если приложение взломают, злоумышленник получит полные права на сервер.
-   **База данных**: Судя по `docker-compose.yml`, БД запускается в Docker. Приложение на хосте ходит к ней через порт, проброшенный наружу контейнера (обычно 5432).
-   **Связь с продакшеном**:
    -   Адрес `https://novel-cloudtech.com:7443` смотрит на Nginx.
    -   Nginx проксирует на локальный порт 8000.
    -   Порт 8000 слушает Uvicorn (FastAPI).

---

## 4. Code Review и рекомендации

### Качество кода
-   **Плюсы**: Код чистый, используется строгая типизация (Pydantic), современный стек (FastAPI, SQLAlchemy 2.0). Структура проекта логичная и понятная.
-   **Минусы**:
    -   **Синхронизация**: В `background_sync.py` цикл синхронизации последовательный (`await self._sync_user`). Если пользователей станет много (100+), цикл будет занимать минуты, и интервал в 10 секунд перестанет соблюдаться.
    -   **Обработка ошибок**: В цикле синхронизации ошибки логируются, но нет механизма повторных попыток (retry) или уведомлений администратора.

### Безопасность
1.  **Root-права**: Приложение работает от root.
    -   *Рекомендация*: Создать отдельного пользователя (например, `leetcode`) и запускать сервис от его имени.
2.  **Секреты**: `.env` файл лежит в корне проекта.
    -   *Рекомендация*: Убедиться, что права на `.env` установлены в `600` (чтение только владельцем).

### Рекомендации по улучшению
1.  **Docker-only**: Перенести само приложение (FastAPI) тоже в Docker. Это унифицирует деплой и мониторинг. Сейчас у вас "зоопарк": БД в докере, приложение в systemd.
2.  **Оптимизация синка**: Сделать запросы к LeetCode параллельными (с ограничением, например, `asyncio.Semaphore(5)`), чтобы ускорить опрос при большом количестве пользователей.

---

## 5. Проект интеграции с Grafana

### 5.1. Выбор схемы: Self-Hosted (Docker)
Для вашего VPS лучше всего подойдет **Self-Hosted** вариант.
-   **Почему**: У вас уже есть Docker для БД. Поднять рядом Grafana и Prometheus — дело 5 минут. Это бесплатно, безопасно и дает полный контроль над данными.
-   **Компоненты**:
    1.  **Prometheus**: Собирает метрики.
    2.  **Grafana**: Визуализирует данные.
    3.  **Node Exporter**: Метрики сервера (CPU, RAM, Disk).
    4.  **Cadvisor**: Метрики Docker-контейнеров.

### 5.2. Метрики, которые будем собирать
1.  **Технические**:
    -   Загрузка CPU/RAM сервера и контейнеров.
    -   RPS (запросов в секунду) к API.
    -   Latency (время ответа) API.
    -   Количество ошибок (5xx коды).
2.  **Бизнес-метрики** (требуют доработки кода):
    -   Количество успешных синхронизаций с LeetCode.
    -   Количество ошибок синхронизации.
    -   Общее число решенных задач пользователями.

### 5.3. Изменения в коде (Добавление метрик)

Вам нужно добавить библиотеку `prometheus-fastapi-instrumentator` в проект.

**1. Обновите зависимости:**
```bash
uv add prometheus-fastapi-instrumentator
```

**2. Модифицируйте `leetcode_tracker/main.py`:**

```python
# Добавьте импорт
from prometheus_fastapi_instrumentator import Instrumentator

# ... (после создания app = FastAPI(...))

# Настройка метрик
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True,
)

# Запуск инструментатора (после всех app.include_router)
instrumentator.instrument(app).expose(app)
```

Это автоматически создаст эндпоинт `/metrics`, который будет отдавать RPS, latency и ошибки в формате Prometheus.

### 5.4. Настройка экспортеров и сборщиков (Docker Compose)

Создайте новый файл `docker-compose.monitoring.yml` (или добавьте эти сервисы в существующий `docker-compose.yml`):

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./grafana/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    ports:
      - "9090:9090"
    restart: always

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin  # Поменяйте при первом входе!
    ports:
      - "3000:3000"
    restart: always

  node_exporter:
    image: prom/node-exporter:latest
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    restart: always

volumes:
  grafana_data:
```

**Конфиг Prometheus (`grafana/prometheus.yml`):**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node_exporter:9100']

  - job_name: 'fastapi_app'
    metrics_path: '/metrics'
    static_configs:
      # Важно: так как app работает на хосте, используем host.docker.internal
      # Для Linux может потребоваться extra_hosts в docker-compose
      - targets: ['host.docker.internal:8000'] 
```

### 5.5. Пошаговая инструкция по запуску Grafana

1.  **Подготовка**:
    -   Создайте файл `grafana/prometheus.yml` с содержимым выше.
    -   Создайте `docker-compose.monitoring.yml`.
    -   Обновите код `main.py` и перезапустите сервис: `systemctl restart leetcode-tracker`.

2.  **Запуск**:
    ```bash
    docker compose -f docker-compose.monitoring.yml up -d
    ```

3.  **Вход в Grafana**:
    -   Откройте в браузере: `https://novel-cloudtech.com:7443/grafana/` (если Nginx настроен правильно) или напрямую по порту, если он открыт.
    -   **Логин**: `admin`
    -   **Пароль**: `admin` (или тот, что вы задали в docker-compose).
    -   При первом входе система попросит сменить пароль.

### 5.6. Настройка Data Sources и Дашбордов

1.  **Добавить Prometheus**:
    -   В меню слева: **Connections** -> **Data Sources** -> **Add data source**.
    -   Выберите **Prometheus**.
    -   В поле URL введите: `http://prometheus:9090` (внутри сети Docker они видят друг друга по именам сервисов).
    -   Нажмите **Save & Test**. Должно появиться зеленое сообщение.

2.  **Создать Дашборд**:
    -   **Dashboards** -> **New dashboard**.
    -   **Add visualization**.
    -   Выберите источник **Prometheus**.
    -   Пример запроса (RPS): `rate(http_requests_total[1m])`.
    -   Пример запроса (CPU): `100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)`.

3.  **Импорт готовых дашбордов**:
    -   Для Node Exporter есть отличный готовый дашборд ID: `1860`.
    -   В Grafana: **Dashboards** -> **New** -> **Import** -> Введите `1860` -> **Load**.

---

## 6. Итоговый чек-лист действий

1.  [ ] **Безопасность**: Создать пользователя `leetcode` и перенастроить systemd unit (не запускать от root).
2.  [ ] **Код**: Добавить `prometheus-fastapi-instrumentator` в `main.py` и перезапустить сервис.
3.  [ ] **Инфраструктура**:
    -   Создать папку `grafana` (если нет) и файл `grafana/prometheus.yml`.
    -   Создать `docker-compose.monitoring.yml`.
4.  [ ] **Запуск**: Запустить мониторинг командой `docker compose -f docker-compose.monitoring.yml up -d`.
5.  [ ] **Настройка**: Зайти в Grafana, добавить Prometheus как источник и импортировать дашборд `1860` (для сервера) и создать свой для приложения.
