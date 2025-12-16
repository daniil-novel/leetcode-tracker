# ⚡ Быстрый старт: Исправление данных в Grafana

## 🎯 Одна команда для деплоя

```bash
bash deploy_to_vdsina.sh
```

## 📝 Что делать после деплоя

### На сервере выполните:

```bash
# 1. Подключитесь к серверу
ssh root@v353999.hosted-by-vdsina.com

# 2. Перейдите в проект
cd /root/leetcode_tracker_uv

# 3. Диагностика
bash check_grafana_data.sh

# 4. Настройка синхронизации (введите ваш LeetCode username)
bash test_leetcode_sync.sh
```

## ✅ Проверка результата

Через 15-20 секунд откройте Grafana:
- URL: https://novel-cloudtech.com:7443/grafana/
- Логин: `admin`
- Пароль: `admin`

Данные должны появиться!

## 📚 Подробная документация

- **Русская инструкция**: [`ИНСТРУКЦИЯ_GRAFANA_ДАННЫЕ.md`](ИНСТРУКЦИЯ_GRAFANA_ДАННЫЕ.md)
- **English guide**: [`GRAFANA_DATA_FIX.md`](GRAFANA_DATA_FIX.md)

## 🆘 Быстрая помощь

**Нет данных в Grafana?**
```bash
ssh root@v353999.hosted-by-vdsina.com
cd /root/leetcode_tracker_uv
bash test_leetcode_sync.sh
```

**Ошибки при деплое?**
```bash
ssh root@v353999.hosted-by-vdsina.com
cd /root/leetcode_tracker_uv
docker-compose logs app | grep -i error
```

**База не подключается?**
```bash
ssh root@v353999.hosted-by-vdsina.com
cd /root/leetcode_tracker_uv
docker-compose restart db grafana
```
