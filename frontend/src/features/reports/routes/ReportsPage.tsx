import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Link } from "react-router-dom";

const sampleReports = [
  {
    id: 1,
    title: "Натальный отчёт — Анна",
    createdAt: "2025-11-10T18:45:00Z",
    status: "Готов",
  },
  {
    id: 2,
    title: "Прогноз на квартал — Максим",
    createdAt: "2025-11-09T12:30:00Z",
    status: "Формируется",
  },
];

export function ReportsPage() {
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="space-y-2">
          <Badge tone="primary">PDF отчёты</Badge>
          <h1 className="text-3xl font-semibold text-neutral-900">
            Управление отчётами
          </h1>
          <p className="max-w-2xl text-neutral-500">
            Создавайте персонализированные PDF-материалы с интерпретациями и
            рекомендациями, основанными на биоастрологии 2.0.
          </p>
        </div>
        <Button disabled>Новый отчёт</Button>
      </header>

      <Card className="space-y-4">
        <h2 className="text-lg font-semibold text-neutral-900">
          Недавние отчёты
        </h2>
        <p className="text-sm text-neutral-500">
          После интеграции с backend здесь будет список с возможностью
          скачивания и повторной генерации.
        </p>
        <div className="divide-y divide-neutral-200 rounded-xl border border-neutral-200">
          {sampleReports.map((report) => (
            <div
              key={report.id}
              className="flex items-center justify-between gap-4 px-5 py-4 text-sm"
            >
              <div>
                <p className="font-medium text-neutral-900">{report.title}</p>
                <p className="text-xs text-neutral-500">
                  {new Date(report.createdAt).toLocaleString("ru-RU", {
                    day: "2-digit",
                    month: "long",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}{" "}
                  · {report.status}
                </p>
              </div>
              <Button variant="secondary" disabled>
                Скачать
              </Button>
            </div>
          ))}
        </div>
      </Card>

      <Card className="space-y-3">
        <h3 className="text-lg font-semibold text-neutral-900">
          Шаблоны отчётов
        </h3>
        <p className="text-sm text-neutral-500">
          Настройте фирменные шаблоны и включайте дополнительные разделы для
          клиентов. Функция появится после подключения админ-панели.
        </p>
        <Button variant="secondary" asChild>
          <Link to="/natal-chart">Перейти к натальной карте</Link>
        </Button>
      </Card>
    </div>
  );
}

