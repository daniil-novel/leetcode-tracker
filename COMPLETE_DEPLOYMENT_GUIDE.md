# Полное руководство по деплою Profile стилей

## Проблема
Стили Profile.css не применяются на production сервере novel-cloudtech.com

## Решение: Пошаговая инструкция

### Часть 1: Локальная подготовка (на вашем компьютере)

#### Шаг 1: Убедитесь, что вы в правильной директории
```bash
cd e:\leetcode_tracker_uv
```

#### Шаг 2: Пересоберите фронтенд с чистого листа
```bash
cd frontend
rm -rf dist/
npm run build
cd ..
```

#### Шаг 3: Проверьте, что стили включены в сборку
```bash
# На Windows PowerShell:
Select-String -Path "frontend\dist\assets\*.css" -Pattern "profile-page"

# На Linux/Mac или Git Bash:
grep -r "profile-page" frontend/dist/assets/*.css
```

Вы должны увидеть строки с `.profile-page`, `.profile-container`, и т.д.

#### Шаг 4: Закоммитьте изменения в Git
```bash
git add frontend/dist/
git add frontend/src/
git commit -m "Deploy: Update frontend build with Profile.css styles"
git push origin main
```

### Часть 2: Деплой на production сервер

#### Вариант A: Использование скрипта (Рекомендуется)

1. **Скопируйте скрипт на сервер:**
```bash
scp server_deploy.sh user@novel-cloudtech.com:/home/user/
```

2. **Подключитесь к серверу:**
```bash
ssh user@novel-cloudtech.com
```

3. **Перейдите в директорию проекта:**
```bash
cd /path/to/leetcode_tracker_uv
```

4. **Скопируйте скрипт в директорию проекта:**
```bash
cp ~/server_deploy.sh .
chmod +x server_deploy.sh
```

5. **Запустите скрипт:**
```bash
./server_deploy.sh
```

#### Вариант B: Ручной деплой (Пошагово)

Подключитесь к серверу и выполните команды по порядку:

```bash
# 1. Подключение к серверу
ssh user@novel-cloudtech.com

# 2. Переход в директорию проекта
cd /path/to/leetcode_tracker_uv

# 3. Получение последних изменений
git fetch origin
git pull origin main

# 4. Проверка, что файлы обновились
ls -lh frontend/dist/assets/

# 5. Проверка наличия Profile стилей в CSS
grep -q "profile-page" frontend/dist/assets/*.css && echo "✅ Profile styles found!" || echo "❌ Profile styles NOT found!"

# 6. Если стили НЕ найдены, пересоберите на сервере:
cd frontend
rm -rf dist/
npm install
npm run build
cd ..

# 7. Перезапуск сервиса
sudo systemctl restart leetcode-tracker

# 8. Проверка статуса сервиса
sudo systemctl status leetcode-tracker

# 9. Проверка логов
sudo journalctl -u leetcode-tracker -n 50 --no-pager

# 10. Тест доступности файлов
curl -I http://localhost:8000/
curl -I http://localhost:8000/assets/index-eGHtU6UY.css
```

### Часть 3: Проверка в браузере

#### Шаг 1: Очистите кэш браузера
- **Windows/Linux**: `Ctrl + Shift + R`
- **Mac**: `Cmd + Shift + R`
- **Или**: Откройте в режиме инкогнито

#### Шаг 2: Проверьте CSS файл напрямую
Откройте в браузере:
```
https://novel-cloudtech.com/assets/index-eGHtU6UY.css
```

Найдите в файле (Ctrl+F): `profile-page`

Вы должны увидеть стили типа:
```css
.profile-page{min-height:100vh;background:linear-gradient(135deg,#0b0b10,#1a1a2e,#16213e)...
```

#### Шаг 3: Проверьте страницу Profile
1. Откройте: `https://novel-cloudtech.com/profile`
2. Откройте DevTools (F12)
3. Перейдите на вкладку "Network"
4. Обновите страницу (F5)
5. Найдите CSS файл в списке загруженных файлов
6. Проверьте, что он загружается со статусом 200

#### Шаг 4: Проверьте применение стилей
В DevTools:
1. Перейдите на вкладку "Elements"
2. Найдите элемент с классом `profile-page`
3. Справа в панели "Styles" должны быть видны стили из `.profile-page`

### Часть 4: Диагностика проблем

#### Проблема: Стили не применяются после деплоя

**Решение 1: Жесткая очистка кэша**
```bash
# В браузере:
1. Откройте DevTools (F12)
2. Правый клик на кнопке обновления
3. Выберите "Empty Cache and Hard Reload"
```

**Решение 2: Проверьте версию CSS файла**
```bash
# На сервере:
ls -lh frontend/dist/assets/*.css

# Проверьте дату модификации - она должна быть свежей
```

**Решение 3: Проверьте, что Nginx отдает правильный файл**
```bash
# На сервере:
curl -I https://novel-cloudtech.com/assets/index-eGHtU6UY.css

# Проверьте заголовки:
# - HTTP/2 200 (должен быть 200, не 304)
# - content-type: text/css
# - content-length: должен быть ~26000 байт
```

**Решение 4: Перезапустите Nginx**
```bash
sudo systemctl restart nginx
sudo systemctl status nginx
```

**Решение 5: Проверьте права доступа к файлам**
```bash
# На сервере:
ls -la frontend/dist/
ls -la frontend/dist/assets/

# Все файлы должны быть читаемыми (r--)
# Если нет, исправьте:
chmod -R 755 frontend/dist/
```

### Часть 5: Финальная проверка

Выполните эти команды на сервере для полной диагностики:

```bash
# 1. Проверка наличия файлов
echo "=== Checking dist files ==="
ls -lh frontend/dist/assets/

# 2. Проверка содержимого CSS
echo "=== Checking CSS content ==="
grep -c "profile-page" frontend/dist/assets/*.css

# 3. Проверка сервиса
echo "=== Checking service ==="
sudo systemctl is-active leetcode-tracker

# 4. Проверка портов
echo "=== Checking ports ==="
sudo netstat -tlnp | grep 8000

# 5. Проверка доступности через localhost
echo "=== Testing localhost ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8000/

# 6. Проверка CSS через localhost
echo "=== Testing CSS file ==="
CSS_FILE=$(ls frontend/dist/assets/*.css | head -n 1)
CSS_NAME=$(basename "$CSS_FILE")
curl -s -o /dev/null -w "HTTP %{http_code}\n" "http://localhost:8000/assets/$CSS_NAME"

# 7. Проверка логов на ошибки
echo "=== Checking for errors in logs ==="
sudo journalctl -u leetcode-tracker -n 100 --no-pager | grep -i error
```

## Контрольный список

- [ ] Локально пересобран фронтенд (`npm run build`)
- [ ] Проверено наличие стилей в CSS файле (grep "profile-page")
- [ ] Изменения закоммичены в Git
- [ ] Изменения запушены на GitHub
- [ ] На сервере выполнен `git pull`
- [ ] На сервере проверено наличие обновленных файлов
- [ ] На сервере проверено наличие стилей в CSS
- [ ] Сервис перезапущен (`systemctl restart`)
- [ ] Статус сервиса проверен (active/running)
- [ ] Логи проверены на ошибки
- [ ] В браузере очищен кэш (Ctrl+Shift+R)
- [ ] CSS файл загружается со статусом 200
- [ ] Стили применяются на странице Profile

## Быстрые команды

### На локальной машине:
```bash
cd e:\leetcode_tracker_uv
cd frontend && rm -rf dist/ && npm run build && cd ..
git add frontend/dist/ frontend/src/
git commit -m "Deploy: Update frontend with Profile styles"
git push origin main
```

### На production сервере:
```bash
cd /path/to/leetcode_tracker_uv
git pull origin main
grep "profile-page" frontend/dist/assets/*.css
sudo systemctl restart leetcode-tracker
sudo systemctl status leetcode-tracker
```

### Проверка в браузере:
1. `Ctrl+Shift+R` для очистки кэша
2. Открыть DevTools (F12) → Network → Обновить
3. Проверить загрузку CSS файла (статус 200)
4. Elements → Найти `.profile-page` → Проверить стили

## Поддержка

Если проблема сохраняется после выполнения всех шагов:
1. Проверьте логи Nginx: `sudo tail -f /var/log/nginx/error.log`
2. Проверьте логи FastAPI: `sudo journalctl -u leetcode-tracker -f`
3. Проверьте права доступа к файлам: `ls -la frontend/dist/`
4. Попробуйте пересобрать на сервере: `cd frontend && npm run build`
