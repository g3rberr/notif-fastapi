# notif-fastapi

A lightweight **notification / task service** built with **FastAPI**, **PostgreSQL**, and **Redis pub/sub**.  
The project demonstrates a clean architecture with separation of API, services, repositories, and workers.

- **FastAPI** provides the REST API
- **Redis pub/sub** is used as a message bus between producers and consumers
- **PostgreSQL** stores task metadata
- **Worker** listens to Redis events and processes tasks asynchronously

---

## Features

- Task creation via API (`POST /api/tasks`)
- Asynchronous processing through a Redis pub/sub channel
- Worker updates task status (`pending → processing → done`)
- Task listing with pagination (`GET /api/tasks?limit=...&offset=...`)
- Health check endpoint (`GET /api/health`)
- Dockerized setup with Postgres, Redis, API, and worker services

---

## Project Structure

```app/
├── api
│ ├── deps.py # Dependency injection
│ └── routers
│ ├── health.py # /health endpoint
│ └── tasks.py # /tasks endpoints
├── core
│ ├── config.py # Settings (Pydantic)
│ └── logging.py # Logging setup
├── db
│ ├── base.py # SQLAlchemy Base
│ └── session.py # Async engine + session
├── models
│ └── task.py # SQLAlchemy Task model
├── repositories
│ └── task_repo.py # TaskRepository (CRUD)
├── schemas
│ ├── common.py # Shared schemas
│ └── task.py # Task schemas
├── services
│ ├── pubsub.py # Redis pub/sub client
│ └── task_service.py # Task producer service
├── workers
│ └── consumer.py # Task worker
└── main.py # FastAPI app entrypoint
```

---

## Getting Started

### 1. Clone the repository

```
git clone https://github.com/g3rberr/notif-fastapi.git
cd notif-fastapi
```

### 2. Environment variables

Copy .env.example to .env and adjust values if needed

### 1. Run with Docker Compose

```
docker compose up -d --build
```

## API

### Health

```
curl http://localhost:8000/api/health
```

### Create task

```
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"example","payload":"some data"}'
```

### List tasks

```
curl "http://localhost:8000/api/tasks?limit=5&offset=0"
```
