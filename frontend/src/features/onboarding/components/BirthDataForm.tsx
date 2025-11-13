import { useMemo, useState } from "react";
import { Controller } from "react-hook-form";
import { useBirthDataForm } from "@/features/onboarding/hooks/useBirthDataForm";
import type { BirthDataFormValues } from "@/features/onboarding/hooks/useBirthDataForm";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { useAutocompleteLocation } from "@/hooks/useAutocompleteLocation";
import type { LocationSuggestion } from "@/lib/types";

const timezoneOptions = [
  "UTC",
  "Europe/Moscow",
  "Europe/Kaliningrad",
  "Europe/Volgograd",
  "Asia/Yekaterinburg",
  "Asia/Omsk",
  "Asia/Krasnoyarsk",
  "Asia/Irkutsk",
  "Asia/Yakutsk",
  "Asia/Vladivostok",
  "Asia/Magadan",
  "Asia/Kamchatka",
  "America/New_York",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Berlin",
];

interface BirthDataFormProps {
  onSubmit: (values: BirthDataFormValues) => void | Promise<void>;
  isSubmitting?: boolean;
}

export function BirthDataForm({ onSubmit, isSubmitting }: BirthDataFormProps) {
  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors, isSubmitting: isFormSubmitting },
    trigger,
  } = useBirthDataForm();

  const [birthQuery, setBirthQuery] = useState("");
  const [currentQuery, setCurrentQuery] = useState("");
  const [selectedBirthLocation, setSelectedBirthLocation] =
    useState<LocationSuggestion | null>(null);
  const [selectedCurrentLocation, setSelectedCurrentLocation] =
    useState<LocationSuggestion | null>(null);

  const {
    suggestions: birthSuggestions,
    isLoading: isLoadingBirth,
  } = useAutocompleteLocation({
    query: birthQuery,
    enabled: birthQuery.length >= 3,
  });

  const {
    suggestions: currentSuggestions,
    isLoading: isLoadingCurrent,
  } = useAutocompleteLocation({
    query: currentQuery,
    enabled: currentQuery.length >= 3,
  });
  const handleBirthSelect = (suggestion: LocationSuggestion) => {
    setValue("birthLocationId", suggestion.id, { shouldValidate: true });
    setSelectedBirthLocation(suggestion);
    setBirthQuery(suggestion.name);
    void trigger("birthLocationId");
  };

  const handleCurrentSelect = (suggestion: LocationSuggestion) => {
    setValue("currentLocationId", suggestion.id, { shouldValidate: true });
    setSelectedCurrentLocation(suggestion);
    setCurrentQuery(suggestion.name);
    void trigger("currentLocationId");
  };

  const isBusy = isSubmitting || isFormSubmitting;

  return (
    <form
      className="grid gap-6 md:grid-cols-2"
      onSubmit={handleSubmit(onSubmit)}
    >
      <div className="space-y-10 md:col-span-2">
        <section className="grid gap-4 rounded-3xl border border-neutral-200 bg-white/80 p-6 shadow-sm backdrop-blur">
          <div>
            <h2 className="text-xl font-semibold text-neutral-900">
              Данные рождения
            </h2>
            <p className="text-sm text-neutral-500">
              Эти сведения используются для расчёта натальной карты и анализа
              модели «Четыре рождения».
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-medium text-neutral-700">
                Дата рождения
              </span>
              <Input type="date" {...register("birthDate")} />
              {errors.birthDate && (
                <p className="text-xs text-danger">{errors.birthDate.message}</p>
              )}
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium text-neutral-700">
                Время рождения
              </span>
              <Input type="time" {...register("birthTime")} />
              {errors.birthTime && (
                <p className="text-xs text-danger">{errors.birthTime.message}</p>
              )}
            </label>

            <label className="space-y-2 md:col-span-2">
              <span className="text-sm font-medium text-neutral-700">
                Место рождения
              </span>
              <div className="space-y-2">
                <Input
                  placeholder="Введите город или адрес"
                  value={birthQuery}
                  onChange={(event) => {
                    setBirthQuery(event.target.value);
                    if (selectedBirthLocation) {
                      setSelectedBirthLocation(null);
                    }
                  }}
                  onFocus={() => {
                    if (selectedBirthLocation) {
                      setBirthQuery(selectedBirthLocation.name);
                    }
                  }}
                />
                {errors.birthLocationId && (
                  <p className="text-xs text-danger">
                    {errors.birthLocationId.message}
                  </p>
                )}
                <SuggestionList
                  isLoading={isLoadingBirth}
                  suggestions={birthSuggestions}
                  onSelect={handleBirthSelect}
                />
              </div>
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium text-neutral-700">
                Часовой пояс
              </span>
              <Controller
                control={control}
                name="timezone"
                render={({ field }) => (
                  <Select {...field}>
                    {timezoneOptions.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </Select>
                )}
              />
              {errors.timezone && (
                <p className="text-xs text-danger">{errors.timezone.message}</p>
              )}
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium text-neutral-700">
                Текущее место проживания <span className="text-neutral-400">(опционально)</span>
              </span>
              <div className="space-y-2">
                <Input
                  placeholder="Введите текущий город"
                  value={currentQuery}
                  onChange={(event) => {
                    setCurrentQuery(event.target.value);
                    if (selectedCurrentLocation) {
                      setSelectedCurrentLocation(null);
                    }
                  }}
                />
                <SuggestionList
                  isLoading={isLoadingCurrent}
                  suggestions={currentSuggestions}
                  onSelect={handleCurrentSelect}
                />
              </div>
            </label>
          </div>
        </section>

        <div className="flex items-center justify-between rounded-3xl border border-neutral-200 bg-white/80 px-6 py-4 shadow-sm backdrop-blur">
          <div>
            <h3 className="text-base font-semibold text-neutral-900">
              Сохранить данные и перейти к расчётам
            </h3>
            <p className="text-sm text-neutral-500">
              После сохранения мы подготовим натальную карту и предварительные
              интерпретации по модели биоастрологии 2.0.
            </p>
          </div>
          <Button type="submit" disabled={isBusy}>
            {isBusy ? (
              <span className="flex items-center gap-2">
                <Spinner size="sm" />
                Сохраняем...
              </span>
            ) : (
              "Сохранить данные"
            )}
          </Button>
        </div>
      </div>
    </form>
  );
}

interface SuggestionListProps {
  suggestions: LocationSuggestion[];
  isLoading: boolean;
  onSelect: (suggestion: LocationSuggestion) => void;
}

function SuggestionList({
  suggestions,
  isLoading,
  onSelect,
}: SuggestionListProps) {
  const items = useMemo(() => suggestions.slice(0, 5), [suggestions]);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-neutral-500">
        <Spinner size="sm" />
        Подбираем места...
      </div>
    );
  }

  if (items.length === 0) return null;

  return (
    <ul className="divide-y divide-neutral-200 overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-sm">
      {items.map((item) => (
        <li key={item.id}>
          <button
            type="button"
            onClick={() => onSelect(item)}
            className="flex w-full flex-col gap-0.5 px-4 py-3 text-left text-sm text-neutral-600 transition hover:bg-neutral-100"
          >
            <span className="font-medium text-neutral-900">{item.name}</span>
            <span className="text-xs text-neutral-500">
              {item.city && `${item.city}, `} {item.country}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}

