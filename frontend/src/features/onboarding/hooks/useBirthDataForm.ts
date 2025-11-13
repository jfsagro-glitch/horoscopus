import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

const optionalPositiveInt = z.preprocess(
  (value) => {
    if (value === "" || value === null || value === undefined) {
      return undefined;
    }
    return value;
  },
  z.coerce.number().int().gt(0).optional(),
);

export const birthDataSchema = z
  .object({
    birthDate: z.string().min(1, "Укажите дату рождения"),
    birthTime: z.string().min(1, "Укажите время рождения"),
    timezone: z.string().min(1, "Выберите часовой пояс"),
    birthLocationId: z
      .coerce.number()
      .int()
      .gt(0, "Выберите место рождения"),
    currentLocationId: optionalPositiveInt,
  })
  .strict();

export type BirthDataFormValues = z.infer<typeof birthDataSchema>;

export function useBirthDataForm(defaultValues?: Partial<BirthDataFormValues>) {
  return useForm<BirthDataFormValues>({
    resolver: zodResolver<BirthDataFormValues>(birthDataSchema),
    mode: "onBlur",
    defaultValues: {
      birthDate: "",
      birthTime: "",
      timezone: "UTC",
      ...defaultValues,
    },
  });
}

