# Руководство по устранению проблем развертывания

## Проблема 1: Ошибка `KeyError: 'ContainerConfig'`

### Симптомы
```
ERROR: for cadvisor  'ContainerConfig'
ERROR: for prometheus  'ContainerConfig'
KeyError: 'ContainerConfig'
```

### Причина
Старая версия docker-compose (1.29.2) пытается пересоздать контейнеры, но метаданные старых контейнеров несовместимы.

### Решение
Скрипт `deploy.sh` теперь автоматически очищает старые контейнеры перед развертыванием:
```bash
./deploy.sh
```

---

## Проблема 2: Ошибка `bind: address already in use`

### Симптомы
```
ERROR: for prometheus  Cannot start service prometheus: driver failed programming external connectivity
failed to bind port 0.0.0.0:9091/tcp: Error starting userland proxy: listen tcp4 0.0.0.0:9091: bind: address already in use
```

### Причина
Порты заняты старыми контейнерами, которые не были полностью остановлены.

### Решение 1: Автоматическая очистка (рекомендуется)
Скрипт `deploy.sh` теперь включает принудительное удаление контейнеров:
```bash
./deploy.sh
```

### Решение 2: Ручная очистка
Если автоматическая очистка не помогла, используйте скрипт аварийной очистки:
```bash
chmod +x cleanup_docker.sh
./cleanup_docker.sh
```

Затем запустите развертывание:
```bash
./deploy.sh
```

### Решение 3: Проверка портов вручную
Проверьте, какие процессы используют порты:
```bash
# Проверка порта 9091 (Prometheus)
sudo netstat -tulpn | grep :9091
sudo lsof -i :9091

# Проверка порта 8081 (cAdvisor)
sudo netstat -tulpn | grep :8081

# Проверка порта 3000 (Grafana)
sudo netstat -tulpn | grep :3000

# Проверка порта 8000 (App)
sudo netstat -tulpn | grep :8000
```

Остановите процессы вручную:
```bash
# Найдите PID процесса и остановите его
sudo kill -9 <PID>
```

---

## Проблема 3: Контейнер `app` unhealthy

### Симптомы
```
ERROR: for app  Container "xxx" is unhealthy.
```

### Причина
База данных не готова или приложение не может подключиться к БД.

### Решение
1. Проверьте логи контейнера приложения:
```bash
docker logs leetcode-tracker-app
```

2. Проверьте логи базы данных:
```bash
docker logs leetcode-tracker-db
```

3. Проверьте healthcheck базы данных:
```bash
docker inspect leetcode-tracker-db | grep -A 10 Health
```

4. Если БД не запускается, проверьте volumes:
```bash
docker volume ls
docker volume inspect leetcode_tracker_uv_postgres_data
```

---

## Полная очистка и переустановка

Если все остальное не помогает, выполните полную очистку:

```bash
# 1. Остановите все контейнеры
docker-compose down -v --remove-orphans

# 2. Удалите все контейнеры проекта
docker ps -a | grep -E "leetcode|prometheus|grafana|cadvisor|node_exporter" | awk '{print $1}' | xargs -r docker rm -f

# 3. Удалите volumes (ВНИМАНИЕ: это удалит все данные!)
docker volume rm leetcode_tracker_uv_postgres_data
docker volume rm leetcode_tracker_uv_prometheus_data
docker volume rm leetcode_tracker_uv_grafana_data

# 4. Очистите Docker кэш
docker system prune -a -f

# 5. Запустите развертывание заново
./deploy.sh
```

---

## Полезные команды

### Проверка состояния контейнеров
```bash
docker ps -a
docker-compose ps
```

### Просмотр логов
```bash
# Все контейнеры
docker-compose logs -f

# Конкретный контейнер
docker logs -f leetcode-tracker-app
docker logs -f leetcode-tracker-db
docker logs -f prometheus
docker logs -f grafana
```

### Перезапуск отдельного сервиса
```bash
docker-compose restart app
docker-compose restart db
docker-compose restart prometheus
```

### Вход в контейнер
```bash
docker exec -it leetcode-tracker-app bash
docker exec -it leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker
```

---

## Обновление docker-compose (рекомендуется)

Старая версия docker-compose (1.29.2) может вызывать проблемы. Рекомендуется обновить:

```bash
# Удалите старую версию
sudo apt-get remove docker-compose

# Установите новую версию (Docker Compose V2)
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Проверьте версию
docker compose version
```

После обновления используйте `docker compose` вместо `docker-compose` (скрипт deploy.sh автоматически определит правильную команду).

---

## Контакты для поддержки

Если проблема не решена, создайте issue в репозитории с:
- Полным выводом ошибки
- Результатом команды `docker ps -a`
- Логами контейнеров
- Версией Docker и docker-compose
