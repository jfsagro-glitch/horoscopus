# Horoscopus

Horoscopus — веб-платформа для расчёта натальных карт и прогнозов по методологии биоастрологии 2.0 Павла Андреева. Репозиторий включает backend на Django/DRF и подготовлен для подключения современного frontend на React.

## Backend

Проект Django находится в каталоге `backend/`:

- модульная архитектура (`apps/core`, `apps/charts`, `apps/forecasts`, `apps/reports`, `apps/integrations`, `apps/analytics`, `apps/accounts`);
- REST API (`/api/v1/…`) с аутентификацией и готовыми эндпоинтами для профилей пользователей, расчётов натальных карт, прогнозов и PDF-отчётов;
- Celery + Redis для асинхронных вычислений (вычисление карт, прогнозов, генерация отчётов);
- интеграционный слой для внешних сервисов (астрономические эфемериды, геокодинг);
- заготовленный пайплайн BioAstrology 2.0 с возможностью замены заглушек на реальные расчёты.
- поддержка WeasyPrint/ReportLab для PDF и Swiss Ephemeris (при наличии `pyswisseph` и данных эфемерид).

### Быстрый старт

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
pip install -r requirements-dev.txt  # инструменты тестирования (optional)
python manage.py migrate
python manage.py createsuperuser  # опционально
python manage.py runserver
```

Для фоновых задач:

```bash
celery -A horoscopus_backend worker -l info
celery -A horoscopus_backend beat -l info
```

### Конфигурация

Переменные окружения читаются из файла `.env` (см. пример значений в README). Ключевые параметры:

- `DJANGO_SECRET_KEY`
- `DATABASE_URL` (PostgreSQL или SQLite по умолчанию)
- `REDIS_URL` / `CELERY_BROKER_URL`
- списки доверенных хостов и доменов для CORS/CSRF.
- `EPHEMERIS_PROVIDER` (`swiss`, `nasa-horizons`, `stub`) и `EPHEMERIS_PATH` (директория с файлами Swiss Ephemeris)
- `NOMINATIM_USER_AGENT`, `GEOAPIFY_API_KEY`, `GOOGLE_GEOCODING_API_KEY` для геокодинга
- `REPORTS_PDF_ENGINE` (`weasyprint`/`reportlab`)

> ⚠️ **Swiss Ephemeris**  
> Для точных расчётов необходимо установить `pyswisseph` (Python < 3.13) и добавить файлы эфемерид (например, `sepl_18.se1`) в каталог `backend/data/ephemeris`. Без этого будет использован обучающий stub или REST-запросы в NASA Horizons.

> ⚠️ **WeasyPrint**  
> На Linux требуется установить системные библиотеки `libpango`, `libcairo`, `gdk-pixbuf`. На Windows используется wheel, дополнительных шагов не требуется.

## Frontend

Каталог `frontend/` содержит Vite + React + TypeScript интерфейс с Tailwind CSS, React Query, Zustand и Radix UI.

### Быстрый старт

```bash
cd frontend
npm install
npm run dev      # локальная разработка на http://localhost:3000
npm run lint     # ESLint
npm run typecheck
```

### Ключевые директории

- `src/app` — провайдеры и маршрутизация.
- `src/components` — UI-кит и layout-компоненты.
- `src/features` — страницы и бизнес-компоненты (онбординг, натальная карта, прогнозы и т.д.).
- `src/lib` — конфигурация, API-клиент, типы.
- `src/hooks` и `src/store` — пользовательские хуки и хранилища Zustand.

Для развёртывания на GitHub Pages предусмотрен скрипт `npm run deploy` (использует `gh-pages` после сборки).

## Дальнейшие шаги

- подключить реальные API эфемерид и геокодинга;
- реализовать расчётные алгоритмы BioAstrology 2.0 вместо текущих заглушек;
- разработать UI и интегрировать его с REST API;
- расширить генерацию отчётов (WeasyPrint/ReportLab) и настроить CDN для хранения PDF.

Проект готов к дальнейшему развитию и развертыванию в облачной инфраструктуре (Docker Compose с PostgreSQL, Redis, Celery worker/beat и фронтендом).

