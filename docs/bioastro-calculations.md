# Horoscopus — Реализация BioAstrology 2.0

Документ фиксирует архитектуру вычислительного ядра и интерпретационных модулей в соответствии с методологией Павла Андреева.

## 1. Архитектура расчётного ядра

```
apps/charts/services/
  ├── ephemeris.py        # загрузка эфемерид (swisseph)
  ├── houses.py           # вычисление домов (Placidus/Koch/WholeSign)
  ├── aspects.py          # аспекты и их интенсивность
  ├── strengths.py        # многофакторная сила планет
  ├── integrals.py        # интегральные показатели (стихии, кресты, зоны)
  └── pipeline.py         # orchestration, кэширование

apps/charts/interpretation/
  ├── four_births.py      # модель «Четыре рождения»
  ├── inner_light.py      # внутренний свет и сияние
  ├── personality.py      # Личность и психология
  ├── potential.py        # Потенциал и возможности
  ├── risks.py            # Риски и вызовы
  ├── recommendations.py  # Рекомендации
  └── renderer.py         # Формирование текстовых блоков
```

### Ключевые сущности (dataclasses)
```python
@dataclass
class PlanetVector:
    body: str
    longitude: float
    latitude: float
    house: int
    retrograde: bool
    speed: float

@dataclass
class AspectMatrixCell:
    source: str
    target: str
    aspect: AspectType
    orb: float
    intensity: float

@dataclass
class IntegralIndicator:
    name: str
    category: str
    value: float
    weights: dict[str, float]
```

## 2. Алгоритм Pipeline

1. **Нормализация входных данных**
   - Приведение времени к UTC (проверить timezone offset, DST).
   - Расчёт юлианской даты (`julian_day = swe.julday(...)`).
2. **Позиции планет**
   - `swe.calc_ut(jd, body)` для основных тел.
   - Расчёт фиктивных точек: Лилит (`MEAN_APOG`), узлы (`MEAN_NODE`).
3. **Дома**
   - `swe.houses_ex(jd, latitude, longitude, house_system='P')`.
   - Сохранение куспидов, углов (Asc, MC).
4. **Аспекты**
   - Вычисление углов между планетами.
   - Допуски (орбы) из конфигурации: major/minor.
   - Интенсивность = базовый вес * (1 - |orb|/max_orb).
5. **Сила планет (многофакторная)**
   - Факторы: позиция в поле (знаки/дома/аспекты), скорость, ретроградность.
   - Весовые коэффициенты в YAML (`config/bioastro.yml`).
   - Нормализация к шкале 0–100.
6. **Интегральные показатели**
   - Стихии (Огонь/Земля/Воздух/Вода).
   - Кресты (Кардинальные/Фиксированные/Мутабельные).
   - Зоны (Личное/Социальное/Коллективное/Трансцендентное).
7. **Модель «Четыре рождения»**
   - Расчёт активных/непроработанных фаз (Предрождение, Рождение, Пробуждение, Возвращение).
   - Метрики по 12 домам и узлам.
8. **Внутренний свет**
   - Оценка баланса между Солнцем, Луной, управителями.
   - Коэффициенты сияния (целостность, направление, проявление).
9. **Генерация отчёта**
   - Структурирование данных в DTO для провайдера интерпретаций.

## 3. Интерпретационный слой

### Стратегия генерации текстов
- Использовать шаблоны Jinja2 с параметрами и блоками.
- Избегать фатализма: применять модификаторы («потенциально», «рекомендуется»).
- Многоуровневые абзацы:
  1. Общее описание.
  2. Проявление в жизни.
  3. Рекомендации/Практики.

### Пример шаблона
```jinja2
{% macro personality_section(chart) -%}
### Личность и психология

- **Четыре рождения**: {{ chart.four_births.current_stage }} — {{ chart.four_births.description }}
- **Сепарация**: {{ chart.separation.status }} ({{ chart.separation.comment }})

{{ chart.inner_light.summary }}

**Сильные стороны**: {{ chart.personality.strengths | join(', ') }}
**Зоны развития**: {{ chart.personality.challenges | join(', ') }}
{%- endmacro %}
```

### Словари и база текстов
- `interpretation/lexicon.yml` — терминология BioAstrology 2.0.
- `interpretation/templates/*.jinja` — шаблоны по разделам.
- `interpretation/recommendations.yml` — практики и советы.

## 4. Генерация PDF отчётов

| Этап | Инструмент | Детали |
| --- | --- | --- |
| HTML шаблон | Jinja2 + Tailwind CSS (via `weasyprint` styles) | Каталог `templates/reports/natal_report.html` |
| Конвертация | WeasyPrint | Требуется установка `libpango`, `libcairo`, `gdk-pixbuf` |
| Альтернатива | ReportLab | Больше контроля, больше кода |

### Пайплайн
```python
from django.template.loader import render_to_string
from weasyprint import HTML

def generate_natal_pdf(chart: NatalChart, user: User):
    context = {"chart": chart, "user": user}
    html = render_to_string("reports/natal_report.html", context)
    pdf_bytes = HTML(string=html).write_pdf()
    return pdf_bytes
```

### Стилизация
- Использовать CSS-переменные для цветового кодирования стихий.
- Иконки/символы планет — SVG.
- Приложения: таблицы аспектов, графики (PNG/SVG, генерируемые D3/Matplotlib).

## 5. Тестирование

| Тест | Что проверяем |
| --- | --- |
| `test_ephemeris_accuracy` | Сравнение вывода `swisseph` с эталонными данными (±0.01°) |
| `test_aspect_matrix` | Корректность нахождения аспектов, орбов |
| `test_integral_indicators` | Сумма стихий = 100%, корректность весов |
| `test_interpretation_templates` | Генерация текста без ключевых ошибок (linting) |
| `test_pdf_generation` | Размер PDF, наличие ключевых заголовков |
| Property-based tests | Непрерывность баллов при изменении входных параметров |

### Инструменты
- `pytest` + `pytest-snapshot` (снимки текстов/HTML/PDF).
- `hypothesis` для вариативного тестирования расчётов.
- `freezegun` для фиксации времени.

## 6. Дальнейшее развитие

- Добавить прогрессии, дирекции (Secondary/Primary) — модуль `progressions.py`.
- Поддержка синастрии — матрица отношений, композитные карты.
- Big Data аналитика: хранить анонимизированные показатели для статистики.
- API для мобильных приложений (GraphQL/REST).
- Нативные библиотеки (Rust/Go) для ускорения тяжелых расчётов (FFI).

