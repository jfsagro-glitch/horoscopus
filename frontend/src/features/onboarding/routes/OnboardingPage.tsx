import { useCallback, useState } from "react";
import { BirthDataForm } from "@/features/onboarding/components/BirthDataForm";
import { BirthDataFormValues } from "@/features/onboarding/hooks/useBirthDataForm";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useToast } from "@/app/providers/toast-context";

export function OnboardingPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { notify } = useToast();

  const handleSubmit = useCallback(
    async (values: BirthDataFormValues) => {
      setIsSubmitting(true);
      try {
        // TODO: integrate with backend API
        console.debug("Onboarding submission", values);
        await new Promise((resolve) => setTimeout(resolve, 1200));
        notify("Данные сохранены. Рассчитываем натальную карту…");
      } finally {
        setIsSubmitting(false);
      }
    },
    [notify],
  );

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <Badge tone="primary">Шаг 1</Badge>
        <h1 className="text-3xl font-semibold text-neutral-900">
          Ввод данных для натального расчёта
        </h1>
        <p className="max-w-2xl text-neutral-500">
          Заполните точные сведения о рождении клиента. Horoscopus использует
          швейцарские эфемериды и методологию биоастрологии 2.0 для построения
          карты и интерпретаций.
        </p>
      </header>

      <Card className="md:p-10">
        <BirthDataForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
      </Card>
    </div>
  );
}

