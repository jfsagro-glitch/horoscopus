import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Link } from "react-router-dom";

const placeholderMetrics = [
  { label: "Элемент Огня", value: "32%" },
  { label: "Элемент Воды", value: "18%" },
  { label: "Кардинальные знаки", value: "41%" },
  { label: "Фиксированные знаки", value: "37%" },
];

export function NatalChartPage() {
  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="space-y-2">
          <Badge tone="primary">Натальная аналитика</Badge>
          <h1 className="text-3xl font-semibold text-neutral-900">
            Натальная карта BioAstrology 2.0
          </h1>
          <p className="max-w-2xl text-neutral-500">
            Визуализация круговой карты, матрицы аспектов и интегральных
            показателей. Данные обновляются после каждого перерасчёта.
          </p>
        </div>
        <Button variant="secondary" asChild>
          <Link to="/reports">Сформировать отчёт</Link>
        </Button>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="min-h-[320px]">
          <h2 className="text-lg font-semibold text-neutral-900">
            Круговая карта
          </h2>
          <p className="mt-2 text-sm text-neutral-500">
            Здесь появится интерактивная визуализация домов, планет и аспектных
            линий (D3.js). Пользователь сможет переключать режимы отображения.
          </p>
          <div className="mt-6 flex h-48 items-center justify-center rounded-2xl border border-dashed border-neutral-300 text-sm text-neutral-400">
            Визуализация в разработке
          </div>
        </Card>

        <Card className="space-y-4">
          <h2 className="text-lg font-semibold text-neutral-900">
            Интегральные показатели
          </h2>
          <p className="text-sm text-neutral-500">
            Распределение стихий, крестов и зон (личное — социальное —
            коллективное — трансцендентное).
          </p>
          <div className="grid gap-3">
            {placeholderMetrics.map((metric) => (
              <div
                key={metric.label}
                className="flex items-center justify-between rounded-xl bg-neutral-100 px-4 py-3 text-sm"
              >
                <span className="font-medium text-neutral-600">
                  {metric.label}
                </span>
                <span className="font-semibold text-neutral-900">
                  {metric.value}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold text-neutral-900">
          Интерпретационный конструктор
        </h2>
        <p className="text-sm text-neutral-500">
          Здесь будут представлены разделы «Личность и психология», «Потенциал и
          возможности», «Риски и вызовы», «Рекомендации по развитию» с
          динамическими блоками на основе терминологии Павла Андреева.
        </p>
        <Button variant="primary" className="self-start" disabled>
          Модуль в разработке
        </Button>
      </Card>
    </div>
  );
}

