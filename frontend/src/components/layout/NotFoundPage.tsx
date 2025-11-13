import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center gap-4 py-24 text-center">
      <div className="rounded-full bg-primary-100 px-4 py-2 text-sm font-semibold text-primary-700">
        404 — страница не найдена
      </div>
      <h1 className="text-3xl font-semibold text-neutral-900">
        Похоже, вы попали на неизведанную орбиту.
      </h1>
      <p className="text-neutral-500">
        Проверьте адрес ссылки или вернитесь на главную панель управления,
        чтобы продолжить работу с Horoscopus.
      </p>
      <Button asChild>
        <Link to="/">Вернуться на дашборд</Link>
      </Button>
    </div>
  );
}

