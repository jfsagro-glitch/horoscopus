# Horoscopus — DevOps и инфраструктура

## 1. Обзор инфраструктуры

| Слой | Технологии | Детали |
| --- | --- | --- |
| Контейнеризация | Docker, Docker Compose | Единый стек для dev/stage/prod |
| Оркестрация (prod) | Kubernetes (K3s/DigitalOcean/KinD) — roadmap | Начало с Docker Compose на VPS |
| CI/CD | GitHub Actions | Пайплайны для backend, frontend, инфраструктуры |
| Мониторинг | Sentry, Prometheus + Grafana | Логи, метрики Celery, uptime |
| Логирование | `structlog` → JSON → ELK/Vector | Корреляция запросов и задач |
| Секреты | GitHub Secrets (CI) → Vault/Doppler | Чёткое разграничение доступа |

## 2. Docker Compose (dev/stage)

```yaml
version: "3.9"
services:
  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-horoscopus}
      POSTGRES_USER: ${POSTGRES_USER:-horoscopus}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-horoscopus}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  celery-worker:
    build: ./backend
    command: celery -A horoscopus_backend worker -l info
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - backend
      - redis

  celery-beat:
    build: ./backend
    command: celery -A horoscopus_backend beat -l info
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - backend
      - redis

  frontend:
    build:
      context: ./frontend
      target: dev
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 3. Dockerfile'ы

### Backend (`backend/Dockerfile`)
```dockerfile
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev libffi-dev libxml2-dev libxslt1-dev \
    libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "horoscopus_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Frontend (`frontend/Dockerfile`)
```dockerfile
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .

FROM base AS dev
CMD ["npm", "run", "dev", "--", "--host"]

FROM base AS build
RUN npm run build

FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

## 4. CI/CD Workflows

### backend.yml
```yaml
name: Backend CI
on:
  push:
    paths:
      - "backend/**"
    branches: [ main ]
  pull_request:
    paths:
      - "backend/**"

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: horoscopus
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python manage.py test
      - run: cd backend && black --check .
      - run: cd backend && isort --check .
      - run: cd backend && flake8
```

### frontend.yml
```yaml
name: Frontend CI/CD
on:
  push:
    paths:
      - "frontend/**"
    branches: [ main ]
  pull_request:
    paths:
      - "frontend/**"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: "frontend/package-lock.json"
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run test -- --watch=false
      - run: cd frontend && npm run build
      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: cd frontend && npm run deploy
```

## 5. Развёртывание продакшена

### Вариант 1 — VPS (Docker Compose)
1. Сервер (Ubuntu 24.04, 4 CPU, 8 GB RAM).
2. Docker + Docker Compose + Caddy/Nginx.
3. Секреты в `.env` (Ansible + sops).
4. SSL (Let's Encrypt через Caddy).
5. Systemd unit для `docker compose up`.

### Вариант 2 — Heroku / Railway (MVP)
1. Backend → Heroku (Container stack).
2. Redis add-on + PostgreSQL add-on.
3. Frontend → GitHub Pages / Vercel.

### Вариант 3 — Kubernetes (roadmap)
1. Ресурсы в Helm chart:
   - Deployment `backend`, `celery-worker`, `celery-beat`.
   - StatefulSet `postgres`.
   - Deployment `redis`.
   - Ingress + cert-manager.
   - PersistentVolume для статических файлов.
2. ArgoCD/GitOps.

## 6. Мониторинг и логирование

| Инструмент | Метрики |
| --- | --- |
| Prometheus Exporters | Django Prometheus, Celery Exporter |
| Grafana | Dashboard: запросы, время ответов, Celery queue length |
| Sentry | Ошибки backend/frontend, релизные теги |
| ELK / OpenSearch | JSON логи с `structlog` |

## 7. Управление конфигурацией

| Среда | Хранение секретов | Управление |
| --- | --- | --- |
| Local | `.env` в `backend/.env` | direnv / dotenv-linter |
| CI | GitHub Secrets | Требуется разграничение на `BACKEND_`, `FRONTEND_` |
| Prod | Doppler / AWS Parameter Store | Автоматическая синхронизация |

## 8. Backups и данные

- PostgreSQL: `pg_dump` ежедневно (S3, rclone, 7 retention).
- Redis: snapshot (RDB) каждые 6 часов.
- Медиа/отчёты: S3 bucket (версионирование).
- Проверка восстановления ежеквартально.

## 9. Безопасность

- HTTPS везде, HSTS.
- CORS настройка по списку доверенных доменов.
- Django security middlewares (SSL redirect, `SECURE_*`).
- Регулярные обновления зависимостей (Dependabot).
- Сканирование образов (`trivy`).
- Лимит размеров файлов (`DATA_UPLOAD_MAX_MEMORY_SIZE`).

