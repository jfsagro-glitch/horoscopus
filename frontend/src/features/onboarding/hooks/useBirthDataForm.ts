import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

const toNumber = (value: unknown) => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed === "") {
      return undefined;
    }
    const parsed = Number(trimmed);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return undefined;
};

export const birthDataSchema = z.object({
  birthDate: z.string().min(1, "Укажите дату рождения"),
  birthTime: z.string().min(1, "Укажите время рождения"),
  timezone: z.string().min(1, "Выберите часовой пояс"),
  birthLocationId: z
    .preprocess((value) => toNumber(value) ?? value, z.number())
    .int("Выберите место рождения")
    .positive("Выберите место рождения"),
  currentLocationId: z.preprocess(
    (value) => toNumber(value) ?? undefined,
    z.number().int().positive().optional(),
  ),
});

export type BirthDataFormValues = z.infer<typeof birthDataSchema>;

export function useBirthDataForm(defaultValues?: Partial<BirthDataFormValues>) {
  return useForm<BirthDataFormValues>({
    resolver: zodResolver(birthDataSchema),
    mode: "onBlur",
    defaultValues: {
      birthDate: "",
      birthTime: "",
      timezone: "UTC",
      ...defaultValues,
    },
  });
}

