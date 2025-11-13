# Horoscopus — План фронтенда (React + Tailwind + D3.js)

## 1. Технологический стек

| Категория | Выбор | Обоснование |
| --- | --- | --- |
| Bundler | Vite + React 18 + TypeScript | Быстрые сборки, поддержка HMR, современный DX |
| UI | Tailwind CSS + Headless UI | Быстрая разработка адаптивного UI, кастомизация компонентов |
| Визуализация | D3.js + Recharts | D3 — для круговой карты, Recharts — для графиков и диаграмм |
| Управление данными | React Query + Zustand | React Query — для запросов к API, Zustand — для локального состояния |
| Маршрутизация | React Router v6 | Поддержка nested routes и data loaders |
| Формы | React Hook Form + Zod | Валидация, аннотирование схем |
| Тестирование | Vitest + Testing Library + Playwright | Unit/Integration/UI тесты |

## 2. Архитектура проекта

```
frontend/
  src/
    app/
      providers/           # React Query provider, Theme provider
      router/              # маршруты и layout
    features/
      onboarding/
      natal-chart/
      forecasts/
      reports/
      profile/
      synastry/
    components/
      ui/                  # базовые компоненты (buttons, inputs)
      charts/              # D3 компоненты (NatalWheel, AspectGraph)
      layout/              # Shell, Sidebar, Topbar
    services/
      api/                 # клиент API
      auth/                # auth state, tokens
    hooks/
    utils/
    styles/
    types/
```

### Правила организации кода
- `features/*` — функциональные блоки с own state + UI + сервисы.
- Стили: Tailwind modules + CSS variables для темной/светлой темы.
- Переводы: `i18next` (подготовка к RU/EN).

## 3. Ключевые экраны

### 3.1 Онбординг / Ввод данных

| Компонент | Поведение |
| --- | --- |
| `BirthDataForm` | Поля: дата, время, место (autocomplete), текущая локация, таймзона |
| `LocationAutocomplete` | Запрос к `/api/v1/core/locations/autocomplete` |
| `ChartPreviewCard` | быстрый превью основных показателей |

### 3.2 Дашборд

| Виджет | Содержимое |
| --- | --- |
| `NatalSnapshot` | Карточка с ключевыми метриками BioAstrology 2.0 |
| `ForecastTimeline` | Переключатель периодов, график событий |
| `RecentReports` | Список последних PDF |
| `TasksWidget` | Рекомендации/напоминания |

### 3.3 Натальная карта

| Секция | Описание |
| --- | --- |
| `NatalWheel` | Круговая карта (D3.js), интерактивные планеты, дома, аспекты |
| `PlanetsTable` | Таблица планет с силами, статусом (ретроградность) |
| `AspectsMatrix` | Матрица аспектов, интенсивность (heatmap) |
| `IntegralIndicators` | Диаграммы по стихиям, крестам, зонам |
| `Interpretations` | Разделы: Личность, Потенциал, Риски, Рекомендации |

### 3.4 Прогнозы

| Компонент | Функциональность |
| --- | --- |
| `HorizonSelector` | Табы: день/неделя/месяц/квартал/год/5/10/30 лет |
| `TransitCalendar` | Календарь/лента событий с фильтрами |
| `OpportunityRiskChart` | График возможностей/рисков |
| `RecommendationsPanel` | Практические советы по периодам |

### 3.5 Личный кабинет

| Вкладка | Содержание |
| --- | --- |
| `ProfileSettings` | Данные пользователя, предпочтения, timezone |
| `SavedCharts` | История, теги, экспорт |
| `Subscriptions` | Информация о тарифах (roadmap) |
| `Security` | Управление устройствами, токенами |

### 3.6 Дополнительно

- `Synastry` — сравнение двух карт (таблица и визуализация).
- `Elective` — выбор дат (roadmap).

## 4. Схема взаимодействия с API

### Базовый клиент
```typescript
import axios from "axios";
import { getAccessToken } from "@/services/auth";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### React Query hooks
```typescript
import { useQuery, useMutation } from "@tanstack/react-query";

export const useNatalChart = (chartId: string) =>
  useQuery({
    queryKey: ["natal-chart", chartId],
    queryFn: () => api.get(`/charts/natal-charts/${chartId}`).then(res => res.data),
    staleTime: Infinity,
    cacheTime: Infinity,
  });

export const useCreateNatalChart = () =>
  useMutation({
    mutationFn: (payload: CreateNatalChartPayload) =>
      api.post("/charts/natal-charts/", payload).then(res => res.data),
  });
```

## 5. UX требования

- Адаптив: mobile-first, поддержка 360px → desktop.
- Темы: Светлая, Темная, «Космическая» (roadmap).
- Обратная связь: skeletons, loaders, toast уведомления (`@radix-ui/react-toast`).
- Shortcuts (roadmap): `CTRL+K` — глобальный поиск, `?` — подсказки.

## 6. Тестирование

| Тип | Инструмент | Охват |
| --- | --- | --- |
| Unit | Vitest | Утилиты, hooks |
| UI | Testing Library | Компоненты форм и таблиц |
| E2E | Playwright | Ключевые пользовательские сценарии |
| Линтинг | ESLint + Prettier | Git hook через Husky |

## 7. CI/CD и деплой фронтенда

- GitHub Actions workflow `frontend.yml`:
  1. `npm ci`
  2. `npm run lint`
  3. `npm run test -- --coverage`
  4. `npm run build`
  5. `npm run deploy` (для main) — публикация на GitHub Pages (`gh-pages` branch).
- `vite.config.ts`: `base: "/horoscopus/"`.
- `CNAME`: `horoscopus.jfsagro.glitch.me` (если кастомный домен).

## 8. Roadmap улучшений

- PWA (offline-first, установка на устройство).
- WebGL-визуализации (Three.js) для анимаций аспектов.
- Интеграция с календарями (ICS).
- i18n: локализация терминологии BioAstrology 2.0.
- Микроанимации (Framer Motion) для интерактивных элементов.

