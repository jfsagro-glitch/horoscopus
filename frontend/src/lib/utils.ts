export function formatDate(date: Date | string, locale: string = "ru-RU") {
  const parsed = typeof date === "string" ? new Date(date) : date;
  return parsed.toLocaleDateString(locale, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function classNames(...values: Array<string | false | undefined | null>) {
  return values.filter(Boolean).join(" ");
}

