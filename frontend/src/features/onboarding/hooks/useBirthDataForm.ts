import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

export const birthDataSchema = z.object({
  birthDate: z.string().min(1, "Укажите дату рождения"),
  birthTime: z.string().min(1, "Укажите время рождения"),
  timezone: z.string().min(1, "Выберите часовой пояс"),
  birthLocationId: z.coerce
    .number({
      invalid_type_error: "Выберите место рождения",
      required_error: "Выберите место рождения",
    })
    .int()
    .positive("Выберите место рождения"),
  currentLocationId: z.preprocess(
    (value) => {
      if (value === "" || value === null || value === undefined) {
        return undefined;
      }
      const numeric = Number(value);
      return Number.isFinite(numeric) ? numeric : value;
    },
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
      birthLocationId: undefined,
      currentLocationId: undefined,
      ...defaultValues,
    },
  });
}

