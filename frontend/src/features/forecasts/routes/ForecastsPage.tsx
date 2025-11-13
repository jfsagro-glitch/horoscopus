import { useMemo, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

const horizons = [
  { id: "day", label: "День" },
  { id: "week", label: "Неделя" },
  { id: "month", label: "Месяц" },
  { id: "quarter", label: "Квартал" },
  { id: "year", label: "Год" },
  { id: "five_years", label: "5 лет" },
];

export function ForecastsPage() {
  const [activeHorizon, setActiveHorizon] = useState(horizons[0].id);

  const placeholder = useMemo(
    () => ({
      summary:
        "Здесь будет отображаться сводка ключевых транзитов и рекомендаций для выбранного периода.",
      opportunities: [
        "Активизация социального взаимодействия и нетворкинга",
        "Расширение профессиональных горизонтов через обучение",
      ],
      challenges: [
        "Возможна эмоциональная нестабильность, связанная с ретроградными аспектами",
        "Необходимость соблюдать баланс между работой и отдыхом",
      ],
    }),
    [],
  );

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <Badge tone="primary">Прогностический модуль</Badge>
        <h1 className="text-3xl font-semibold text-neutral-900">
          Прогнозы по периодам
        </h1>
        <p className="max-w-2xl text-neutral-500">
          Получайте аналитические подсказки на разных временных горизонтах,
          включая стратегические рекомендации и акценты по сферам жизни.
        </p>
      </header>

      <Card className="flex flex-wrap gap-2">
        {horizons.map((horizon) => (
          <Button
            key={horizon.id}
            variant={activeHorizon === horizon.id ? "primary" : "secondary"}
            size="sm"
            onClick={() => setActiveHorizon(horizon.id)}
          >
            {horizon.label}
          </Button>
        ))}
      </Card>

      <section className="grid gap-4 lg:grid-cols-[2fr,1fr]">
        <Card className="space-y-4">
          <h2 className="text-lg font-semibold text-neutral-900">
            Синопсис периода «{horizons.find((item) => item.id === activeHorizon)?.label}»
          </h2>
          <p className="text-sm text-neutral-500">{placeholder.summary}</p>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-xl bg-green-50 p-4">
              <p className="mb-2 text-sm font-semibold text-green-700">
                Возможности
              </p>
              <ul className="list-disc space-y-1 pl-4 text-sm text-green-800">
                {placeholder.opportunities.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl bg-red-50 p-4">
              <p className="mb-2 text-sm font-semibold text-red-700">Вызовы</p>
              <ul className="list-disc space-y-1 pl-4 text-sm text-red-800">
                {placeholder.challenges.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
          <Button variant="secondary" disabled className="self-start">
            Подробный прогноз появится после интеграции с API
          </Button>
        </Card>

        <Card className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-900">
            Ключевые аспекты
          </h3>
          <p className="text-sm text-neutral-500">
            Сюда будет подгружаться матрица транзитов, дирекций и прогрессий
            с указанием силы и точных дат.
          </p>
          <div className="flex flex-col gap-3 rounded-xl border border-dashed border-neutral-200 p-4 text-sm text-neutral-500">
            <p>• Транзит Юпитера к управителю X дома — активация карьерных шансов.</p>
            <p>• Напряжение Марса к Луне — обращайте внимание на эмоциональный баланс.</p>
            <p>• Солярная прогрессия Солнца — уточнение личной миссии на год.</p>
          </div>
        </Card>
      </section>
    </div>
  );
}

