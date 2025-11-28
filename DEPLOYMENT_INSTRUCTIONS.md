# Инструкция по деплою обновленного фронтенда на novel-cloudtech.com

## Проблема
Стили Profile.css не применяются на production сервере, потому что там используется старая версия собранных файлов.

## Решение

### Шаг 1: Локальная сборка (✅ ВЫПОЛНЕНО)
```bash
cd frontend
npm run build
```

Результат: Обновленные файлы в `frontend/dist/`:
- `dist/index.html`
- `dist/assets/index-eGHtU6UY.css` (25.73 kB) - содержит стили Profile
- `dist/assets/index-CQe5To13.js` (439.94 kB)

### Шаг 2: Загрузка на production сервер

#### Вариант A: Через Git (Рекомендуется)

1. **Закоммитьте изменения:**
```bash
git add frontend/dist/
git commit -m "Update frontend build with Profile.css styles"
git push origin main
```

2. **На production сервере:**
```bash
ssh user@novel-cloudtech.com
cd /path/to/leetcode_tracker_uv
git pull origin main
sudo systemctl restart leetcode-tracker
```

#### Вариант B: Через SCP (Прямая загрузка)

```bash
# Из локальной директории проекта
scp -r frontend/dist/* user@novel-cloudtech.com:/path/to/leetcode_tracker_uv/frontend/dist/
```

Затем на сервере:
```bash
ssh user@novel-cloudtech.com
sudo systemctl restart leetcode-tracker
```

#### Вариант C: Пересборка на сервере

```bash
ssh user@novel-cloudtech.com
cd /path/to/leetcode_tracker_uv
git pull origin main
cd frontend
npm run build
cd ..
sudo systemctl restart leetcode-tracker
```

### Шаг 3: Проверка на сервере

После деплоя выполните на сервере:

```bash
# Проверить статус сервиса
sudo systemctl status leetcode-tracker

# Проверить логи
sudo journalctl -u leetcode-tracker -f

# Проверить, что файлы обновлены
ls -lh /path/to/leetcode_tracker_uv/frontend/dist/assets/
```

### Шаг 4: Проверка в браузере

1. Откройте https://novel-cloudtech.com/profile
2. **Очистите кэш браузера**: `Ctrl+Shift+R` (Windows/Linux) или `Cmd+Shift+R` (Mac)
3. Проверьте, что стили применяются корректно

## Важные замечания

### Кэширование
Nginx настроен на кэширование статических файлов на 1 год:
```nginx
location /assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**Поэтому обязательно:**
- Очистите кэш браузера после деплоя
- Или используйте режим инкогнито для проверки

### Проверка версии файлов
Обратите внимание на хэши в именах файлов:
- `index-eGHtU6UY.css` - текущая версия
- Если хэш изменится после пересборки, это нормально

### Автоматический деплой (будущее улучшение)
Можно настроить GitHub Actions для автоматического деплоя:
1. При push в main
2. Автоматически собирать фронтенд
3. Деплоить на сервер
4. Перезапускать сервис

## Текущий статус

✅ Локальная сборка выполнена
⏳ Ожидается загрузка на production сервер
⏳ Ожидается перезапуск сервиса

## Команды для быстрого доступа

```bash
# Подключение к серверу
ssh user@novel-cloudtech.com

# Перезапуск сервиса
sudo systemctl restart leetcode-tracker

# Просмотр логов
sudo journalctl -u leetcode-tracker -n 50

# Проверка статуса
sudo systemctl status leetcode-tracker
