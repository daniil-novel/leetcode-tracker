
## Обзор

Теперь ваше приложение может автоматически импортировать решённые задачи из LeetCode в базу данных. Задачи будут отображаться в календаре и статистике без необходимости ручного ввода или импорта CSV.

## Как это работает

1. Пользователь устанавливает свой LeetCode username
2. Приложение запрашивает последние принятые решения через LeetCode API
3. Для каждого решения определяется сложность задачи
4. Задачи автоматически добавляются в базу данных
5. Задачи отображаются в календаре и статистике

## API Endpoints

### 1. Установить LeetCode Username

**Endpoint**: `PUT /api/sync/leetcode-username`

**Параметры**:
- `leetcode_username` (query parameter) - ваш username на LeetCode

**Пример**:
```bash
curl -X PUT "https://novel-cloudtech.com:7443/api/sync/leetcode-username?leetcode_username=your_username" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Ответ**:
```json
{
  "message": "LeetCode username updated successfully",
  "leetcode_username": "your_username"
}
```

### 2. Синхронизировать задачи

**Endpoint**: `POST /api/sync/from-leetcode`

**Параметры**:
- `limit` (query parameter, optional) - количество последних решений для синхронизации (по умолчанию 100)

**Пример**:
```bash
curl -X POST "https://novel-cloudtech.com:7443/api/sync/from-leetcode?limit=100" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Ответ**:
```json
{
  "message": "Sync started in background",
  "leetcode_username": "your_username",
  "limit": 100
}
```

**Примечание**: Синхронизация выполняется в фоновом режиме, поэтому ответ приходит сразу. Задачи появятся в базе данных через несколько секунд.

### 3. Проверить статус синхронизации

**Endpoint**: `GET /api/sync/status`

**Пример**:
```bash
curl "https://novel-cloudtech.com:7443/api/sync/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Ответ**:
```json
{
  "leetcode_username": "your_username",
  "has_leetcode_username": true,
  "total_leetcode_tasks": 150
}
```

## Пошаговая инструкция

### Шаг 1: Установите LeetCode Username

После входа в приложение, установите свой LeetCode username:

```bash
# Замените YOUR_TOKEN на ваш JWT токен
# Замените your_leetcode_username на ваш username на LeetCode

curl -X PUT "https://novel-cloudtech.com:7443/api/sync/leetcode-username?leetcode_username=your_leetcode_username" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Шаг 2: Запустите синхронизацию

```bash
curl -X POST "https://novel-cloudtech.com:7443/api/sync/from-leetcode?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Шаг 3: Проверьте результат

Обновите страницу дашборда - ваши задачи из LeetCode должны появиться в календаре!

## Как работает синхронизация

### 1. Получение данных

Приложение запрашивает последние принятые решения через LeetCode GraphQL API:
```graphql
query getRecentAcSubmissions($username: String!, $limit: Int) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    title
    titleSlug
    timestamp
    lang
  }
}
```

### 2. Определение сложности

Для каждой уникальной задачи приложение запрашивает детали, чтобы узнать сложность:
```graphql
query getProblemDetails($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    difficulty
  }
}
```

### 3. Расчёт XP

- **Easy**: 1 XP
- **Medium**: 3 XP
- **Hard**: 5 XP

### 4. Сохранение в базу данных

Каждое решение сохраняется как задача:
- **Дата**: дата решения задачи
- **Название**: название задачи
- **Сложность**: Easy/Medium/Hard
- **XP**: рассчитанные очки
- **Платформа**: "leetcode"
- **Заметки**: язык программирования

### 5. Предотвращение дубликатов

Приложение проверяет, существует ли уже задача с таким же названием и датой. Если да - пропускает её.

## Особенности

### ✅ Преимущества

1. **Автоматический импорт** - не нужно вручную вводить каждую задачу
2. **Фоновая обработка** - синхронизация не блокирует интерфейс
3. **Определение сложности** - автоматически определяется сложность каждой задачи
4. **Предотвращение дубликатов** - задачи не дублируются при повторной синхронизации
5. **Информация о языке** - сохраняется язык программирования

### ⚠️ Ограничения

1. **Лимит запросов** - LeetCode может ограничивать количество запросов
2. **Публичный профиль** - ваш профиль на LeetCode должен быть публичным
3. **Только принятые решения** - синхронизируются только accepted submissions
4. **Последние N решений** - по умолчанию последние 100 (можно изменить параметром `limit`)

## Рекомендации

### Первая синхронизация

Для первой синхронизации рекомендуется использовать большой лимит:

```bash
curl -X POST "https://novel-cloudtech.com:7443/api/sync/from-leetcode?limit=500" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Регулярная синхронизация

Для регулярных обновлений достаточно меньшего лимита:

```bash
curl -X POST "https://novel-cloudtech.com:7443/api/sync/from-leetcode?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Автоматическая синхронизация

Вы можете настроить автоматическую синхронизацию с помощью cron:

```bash
# Синхронизация каждый день в 00:00
0 0 * * * curl -X POST "https://novel-cloudtech.com:7443/api/sync/from-leetcode?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Ошибка: "LeetCode username not set"

**Решение**: Сначала установите LeetCode username через `PUT /api/sync/leetcode-username`

### Ошибка: "LeetCode user not found"

**Решение**: 
- Проверьте правильность написания username (регистр важен)
- Убедитесь, что профиль на LeetCode публичный

### Задачи не появляются

**Решение**:
1. Проверьте статус синхронизации: `GET /api/sync/status`
2. Проверьте логи сервера на наличие ошибок
3. Убедитесь, что у вас есть принятые решения на LeetCode

### Дубликаты задач

**Решение**: Приложение автоматически предотвращает дубликаты. Если вы видите дубликаты, это может быть из-за:
- Разных дат решения одной и той же задачи
- Ручного добавления задач с теми же названиями

## Примеры использования

### Пример 1: Полная настройка

```bash
# 1. Установить username
curl -X PUT "https://novel-cloudtech.com:7443/api/sync/leetcode-username?leetcode_username=john_doe" \
  -H "Authorization: Bearer eyJ..."

# 2. Синхронизировать все задачи
curl -X POST "https://novel-cloudtech.com:7443/api/sync/from-leetcode?limit=500" \
  -H "Authorization: Bearer eyJ..."

# 3. Проверить статус
curl "https://novel-cloudtech.com:7443/api/sync/status" \
  -H "Authorization: Bearer eyJ..."
```

### Пример 2: Регулярное обновление

```bash
# Синхронизировать последние 20 решений
curl -X POST "https://novel-cloudtech.com:7443/api/sync/from-leetcode?limit=20" \
  -H "Authorization: Bearer eyJ..."
```

## Интеграция с Frontend

В будущем можно добавить кнопку синхронизации в интерфейс:

```typescript
// Пример React компонента
const SyncButton = () => {
  const [syncing, setSyncing] = useState(false);
  
  const handleSync = async () => {
    setSyncing(true);
    try {
      const response = await fetch('/api/sync/from-leetcode?limit=100', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Sync failed');
    } finally {
      setSyncing(false);
    }
  };
  
  return (
    <button onClick={handleSync} disabled={syncing}>
      {syncing ? 'Syncing...' : 'Sync from LeetCode'}
    </button>
  );
};
```

## Заключение

Теперь вы можете автоматически импортировать все свои решения из LeetCode! Задачи будут отображаться в календаре и учитываться в статистике, как если бы вы добавили их вручную.

Для вопросов и поддержки обращайтесь к документации API: `/docs`
