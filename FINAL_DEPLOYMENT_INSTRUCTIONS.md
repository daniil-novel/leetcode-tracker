# Финальные инструкции по развертыванию

## Проблема
На сервере порты **9091** и **9092** заняты внешними процессами:
- **9091**: Node.js процесс (PID 1215)
- **9092**: outline-ss-ser процесс (PID 1250)

Также есть "зомби" контейнер Prometheus, который мешает развертыванию.

## Решение
Изменен порт Prometheus на **9093** (свободный порт).

## Команды для выполнения на сервере

### Шаг 1: Удалите зомби-контейнеры
```bash
cd ~/leetcode_tracker_uv

# Удалить все контейнеры prometheus (включая зомби)
docker ps -a --filter "name=prometheus" -q | xargs -r docker rm -f

# Удалить все контейнеры проекта
docker ps -a --filter "name=leetcode" -q | xargs -r docker rm -f
docker ps -a --filter "name=grafana" -q | xargs -r docker rm -f
docker ps -a --filter "name=cadvisor" -q | xargs -r docker rm -f
docker ps -a --filter "name=node_exporter" -q | xargs -r docker rm -f

# Проверить, что контейнеры удалены
docker ps -a
```

### Шаг 2: Обновите код
```bash
git pull
chmod +x deploy.sh cleanup_docker.sh fix_deployment.sh
```

### Шаг 3: Проверьте порт 9093
```bash
# Убедитесь, что порт 9093 свободен
sudo netstat -tulpn | grep :9093
# Если команда ничего не выводит - порт свободен ✅
```

### Шаг 4: Запустите развертывание
```bash
./deploy.sh
```

### Шаг 5: Проверьте статус контейнеров
```bash
# Подождите 30 секунд для healthcheck
sleep 30

# Проверьте статус всех контейнеров
docker ps -a

# Проверьте логи приложения
docker logs leetcode-tracker-app

# Проверьте логи базы данных
docker logs leetcode-tracker-db

# Проверьте логи prometheus
docker logs prometheus
```

### Шаг 6: Проверьте healthcheck
```bash
# Проверьте health endpoint приложения
curl http://localhost:8000/health

# Должен вернуть: {"status":"healthy"}
```

## Если возникнут проблемы

### Проблема: Контейнер app unhealthy
```bash
# Проверьте логи
docker logs leetcode-tracker-app --tail 50

# Проверьте подключение к БД
docker exec -it leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "SELECT 1;"
```

### Проблема: Порт все еще занят
```bash
# Используйте скрипт очистки
./cleanup_docker.sh

# Затем снова запустите развертывание
./deploy.sh
```

### Проблема: Зомби-контейнеры не удаляются
```bash
# Принудительное удаление по ID
docker rm -f $(docker ps -aq)

# Очистка всех неиспользуемых ресурсов
docker system prune -a -f
```

## Доступ к сервисам после развертывания

- **Приложение**: https://novel-cloudtech.com:7443/
- **Grafana**: https://novel-cloudtech.com:7443/grafana/ (или http://<ip>:3000)
- **Prometheus**: http://<ip>:9093
- **cAdvisor**: http://<ip>:8081

## Важные изменения

1. ✅ Добавлен `/health` endpoint для healthcheck
2. ✅ Prometheus теперь на порту **9093** (вместо 9091/9092)
3. ✅ Улучшена очистка контейнеров в deploy.sh
4. ✅ Добавлен healthcheck для контейнера app

## Проверка успешного развертывания

Все контейнеры должны быть в статусе **Up** и **healthy**:
```bash
docker ps

# Ожидаемый вывод:
# leetcode-tracker-app  Up (healthy)
# leetcode-tracker-db   Up (healthy)
# prometheus            Up
# grafana               Up
# cadvisor              Up
# node_exporter         Up
```
