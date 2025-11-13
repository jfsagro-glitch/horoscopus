export const endpoints = {
  locations: {
    autocomplete: "/core/locations/autocomplete",
  },
  charts: {
    list: "/charts/natal-charts",
  },
  forecasts: {
    list: "/forecasts/forecasts",
  },
  reports: {
    list: "/reports/reports",
  },
} as const;

