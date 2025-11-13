import { Link } from "react-router-dom";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export function DashboardPage() {
  const sections = [
    {
      title: "Натальная карта",
      description:
        "Просматривайте ключевые показатели BioAstrology 2.0 и персональные интерпретации.",
      action: { to: "/natal-chart", label: "Открыть карту" },
    },
    {
      title: "Прогнозы",
      description:
        "Получайте краткосрочные, среднесрочные и долгосрочные прогнозы с практическими рекомендациями.",
      action: { to: "/forecasts", label: "Перейти к прогнозам" },
    },
    {
      title: "PDF отчёты",
      description:
        "Формируйте и скачивайте персонализированные отчёты для клиентов и коллег.",
      action: { to: "/reports", label: "Управлять отчётами" },
    },
  ];

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <Badge tone="primary">Версия 0.1.0</Badge>
        <h1 className="text-3xl font-semibold text-neutral-900">
          Центр управления Horoscopus
        </h1>
        <p className="max-w-2xl text-neutral-500">
          Добро пожаловать в систему биоастрологии 2.0. Здесь вы можете
          управлять натальными картами, прогнозами и отчётами, а также
          адаптировать рекомендации под запросы клиентов.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {sections.map((section) => (
          <Card key={section.title} className="flex flex-col gap-3">
            <h2 className="text-lg font-semibold text-neutral-900">
              {section.title}
            </h2>
            <p className="text-sm text-neutral-500">{section.description}</p>
            <Button variant="secondary" asChild>
              <Link to={section.action.to}>{section.action.label}</Link>
            </Button>
          </Card>
        ))}
      </section>
    </div>
  );
}

