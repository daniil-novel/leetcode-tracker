# Архитектура фронтенда LeetCode Tracker

## Общая структура

Проект использует **React SPA (Single Page Application)** с **FastAPI бэкендом** и **Nginx** в качестве reverse proxy.

```
e:/leetcode_tracker_uv/
├── frontend/                    # React приложение
│   ├── src/
│   │   ├── components/         # Переиспользуемые компоненты
│   │   ├── pages/             # Страницы приложения
│   │   ├── context/           # React Context для состояния
│   │   ├── main.tsx           # Точка входа
│   │   └── main.css           # Глобальные стили
│   ├── dist/                  # Собранное приложение (после npm run build)
│   ├── package.json           # Зависимости и скрипты
│   └── vite.config.ts         # Конфигурация Vite
├── leetcode_tracker/           # FastAPI бэкенд
│   ├── main.py                # Основное приложение FastAPI
│   ├── routers/               # API роутеры
│   └── static/                # Статические файлы бэкенда
└── nginx-leetcode-tracker.conf # Конфигурация Nginx
```

## React Frontend

### Технологии
- **React 19** - основной фреймворк
- **TypeScript** - типизация
- **Vite** - сборщик и dev-сервер
- **React Router** - клиентский роутинг
- **Chart.js + react-chartjs-2** - графики
- **CSS Modules** - стилизация

### Структура компонентов

#### Pages (страницы)
- `Login.tsx` - страница авторизации
- `Dashboard.tsx` - главная страница с дашбордом
- `Profile.tsx` - страница профиля пользователя

#### Components (переиспользуемые компоненты)
- `CalendarSection.tsx` - интерактивный календарь
- `ChartsSection.tsx` - графики продуктивности
- `GoalSection.tsx` - управление целями
- `MetricsSection.tsx` - метрики KPI
- `RecentTasksTable.tsx` - таблица последних задач
- `TaskForm.tsx` - форма добавления задач

#### Context
- `AuthContext.tsx` - управление аутентификацией

### Роутинг
```typescript
// frontend/src/App.tsx
<BrowserRouter>
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
    <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
  </Routes>
</BrowserRouter>
```

### Сборка и запуск

#### Development
```bash
cd frontend
npm install          # установка зависимостей
npm run dev         # запуск dev-сервера на http://localhost:5173
```

#### Production
```bash
cd frontend
npm run build       # сборка в dist/
npm run preview     # локальный preview собранного приложения
```

### Конфигурация Vite
```typescript
// frontend/vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',    // прокси API запросов
      '/auth': 'http://localhost:8000',   // прокси аутентификации
      '/add': 'http://localhost:8000',    // прокси добавления задач
    }
  }
})
```

## FastAPI Backend Integration

### Обслуживание статических файлов
```python
# leetcode_tracker/main.py
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"

# Монтирование статических файлов React
if FRONTEND_DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="assets")

# Обслуживание index.html для SPA роутинга
@app.get("/")
async def serve_root():
    return FileResponse(FRONTEND_DIST_DIR / "index.html")

# Catch-all для клиентского роутинга
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    if full_path.startswith(("api/", "auth/", "add/", "stats/", "static/")):
        raise HTTPException(status_code=404, detail="Not found")

    file_path = FRONTEND_DIST_DIR / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)

    return FileResponse(FRONTEND_DIST_DIR / "index.html")
```

### API роутеры
- `/api/profile/*` - управление профилем
- `/api/tasks/*` - CRUD операции с задачами
- `/api/stats/*` - статистика и метрики
- `/api/month/*` - месячные цели
- `/auth/*` - аутентификация (GitHub OAuth)

## Nginx Configuration

### Основные настройки
```nginx
# nginx-leetcode-tracker.conf
server {
    listen 80;
    server_name novel-cloudtech.com www.novel-cloudtech.com;

    # SSL настройки
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/novel-cloudtech.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/novel-cloudtech.com/privkey.pem;

    # Проксирование к FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Статические файлы (кеширование)
    location /assets/ {
        proxy_pass http://127.0.0.1:8000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Деплоймент

### Production сборка
1. **Сборка фронтенда:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Запуск FastAPI:**
   ```bash
   cd leetcode_tracker
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Nginx как reverse proxy** на порту 80/443

### Важные моменты
- **SPA роутинг:** Все не-API запросы перенаправляются на `index.html`
- **Кеширование:** Статические файлы кешируются на 1 год
- **HTTPS:** Обязательно для OAuth и безопасности
- **CORS:** Настроен в FastAPI для development

## Аутентификация

### GitHub OAuth Flow
1. Пользователь кликает "Login with GitHub"
2. Редирект на `/auth/github/login`
3. FastAPI перенаправляет на GitHub
4. После авторизации - редирект обратно с токеном
5. Токен сохраняется в localStorage
6. Все API запросы включают `Authorization: Bearer ${token}`

### Защищенные роуты
```typescript
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};
```

## Стилизация

### CSS Modules
- Каждый компонент имеет свой CSS файл
- Импорт: `import './Component.css'`
- Классы доступны как глобальные

### Темная тема
- CSS переменные для цветов
- Градиенты и современный дизайн
- Адаптивность для мобильных устройств

## Мониторинг и отладка

### Development
- **Vite dev server** на `http://localhost:5173`
- **Hot reload** для быстрой разработки
- **Source maps** для отладки

### Production
- **Browser DevTools** для анализа сети и производительности
- **FastAPI logs** для API запросов
- **Nginx access/error logs** для веб-сервера

## Важные файлы для понимания

### Frontend
- `frontend/src/main.tsx` - точка входа
- `frontend/src/App.tsx` - главный компонент с роутингом
- `frontend/src/context/AuthContext.tsx` - управление аутентификацией
- `frontend/package.json` - зависимости и скрипты

### Backend
- `leetcode_tracker/main.py` - FastAPI приложение
- `leetcode_tracker/routers/` - API endpoints
- `nginx-leetcode-tracker.conf` - веб-сервер

### Конфигурация
- `frontend/vite.config.ts` - настройки сборки
- `pyproject.toml` - Python зависимости
- `.env.example` - переменные окружения

## Troubleshooting

### Проблемы со стилями
- Очистить кэш браузера
- Проверить, что `npm run build` выполнен
- Убедиться, что Nginx отдает правильные заголовки кеширования

### API ошибки
- Проверить CORS настройки
- Проверить токен аутентификации
- Проверить логи FastAPI

### Роутинг проблемы
- Убедиться, что Nginx правильно проксирует запросы
- Проверить, что `index.html` отдается для SPA роутов
- Проверить, что API пути исключены из catch-all
