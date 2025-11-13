import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { useAuthStore } from "@/store/useAuthStore";

export function ProfilePage() {
  const { userName, setUserName } = useAuthStore();
  const [name, setName] = useState(userName ?? "Астролог");

  const handleSave = () => {
    setUserName(name);
  };

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <Badge tone="primary">Профиль специалиста</Badge>
        <h1 className="text-3xl font-semibold text-neutral-900">
          Настройки аккаунта
        </h1>
        <p className="max-w-2xl text-neutral-500">
          Управляйте отображаемым именем, контактами и предпочтениями
          уведомлений. Скоро здесь появится интеграция с тарифами и API-ключами.
        </p>
      </header>

      <Card className="space-y-4 md:max-w-2xl">
        <div>
          <h2 className="text-lg font-semibold text-neutral-900">
            Персональные данные
          </h2>
          <p className="text-sm text-neutral-500">
            Обновите сведения, которые будут отображаться в отчётах и
            интерфейсе сервиса.
          </p>
        </div>
        <label className="space-y-2">
          <span className="text-sm font-medium text-neutral-700">
            Отображаемое имя
          </span>
          <Input value={name} onChange={(event) => setName(event.target.value)} />
        </label>
        <div className="flex justify-end">
          <Button variant="secondary" onClick={handleSave}>
            Сохранить изменения
          </Button>
        </div>
      </Card>

      <Card className="md:max-w-2xl">
        <h2 className="text-lg font-semibold text-neutral-900">
          Интеграции и API
        </h2>
        <p className="mt-2 text-sm text-neutral-500">
          В будущих релизах вы сможете управлять API-ключами, токенами доступа и
          подключать мобильные приложения к Horoscopus.
        </p>
        <Button variant="ghost" className="mt-4 cursor-default" disabled>
          Раздел в разработке
        </Button>
      </Card>
    </div>
  );
}

