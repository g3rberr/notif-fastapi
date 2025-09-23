# email notification service
Сервис уведомлений, принимает задачи на отправку писем, кладет их в очередь и довозит до SMTP. Используется - FastAPI + PostgreSQL (SQLAlchemy async) + Redis/Celery

## Эндпоинты
- GET /api/health - проверяет работает ли сервис
- POST /api/tasks/email - принимает задачу на отправку письма и перенаправляет ее в очередь Celery. Возвращает task_id
- GET /api/tasks - возвращает список принятых задач (используется пагинация: limit/offset)

## примеры API
### GET /api/health
Ответ:
```
{"ok": true}
```
### POST /api/tasks/email
```
{
  "to": "test@example.com",
  "subject": "Hello",
  "message": "This is a test message"
}
```
Ответ:
```
{ "accepted": true, "task_id": "17c6e24b-0b95-44f9-8fdc-ad6b53d9e5e3" }
```
### GET /api/tasks
Возвращает массив TaskRead. Ответ:
```
[
  {
    "id": "17c6e24b-0b95-44f9-8fdc-ad6b53d9e5e3",
    "title": "send_email",
    "payload": "{\"to\":\"test@example.com\",\"subject\":\"Hello\",\"message\":\"This is a test message\" }",
    "status": "processing",
    "attempt_count": 0,
    "max_attempts": 5,
    "next_attempt_at": null,
    "locked_by": "celery@8b2b419455e2",
    "last_error": null,
    "created_at": "2025-09-21T16:48:43.201295Z",
    "updated_at": "2025-09-21T16:48:43.201295Z"
  },
  {...},
]
```

## Запуск
Приложение запускается через Docker compose.

В корне есть docker-compose.yml, который поднимает api, worker, dispatcher, redis, db и flower
```
docker-compose up --build
```
