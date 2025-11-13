import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardPage } from "@/features/dashboard/routes/DashboardPage";
import { OnboardingPage } from "@/features/onboarding/routes/OnboardingPage";
import { NatalChartPage } from "@/features/natal-chart/routes/NatalChartPage";
import { ForecastsPage } from "@/features/forecasts/routes/ForecastsPage";
import { ReportsPage } from "@/features/reports/routes/ReportsPage";
import { ProfilePage } from "@/features/profile/routes/ProfilePage";
import { NotFoundPage } from "@/components/layout/NotFoundPage";

export const appRouter = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <DashboardPage /> },
      {
        path: "onboarding",
        element: <OnboardingPage />,
      },
      {
        path: "natal-chart/:id?",
        element: <NatalChartPage />,
      },
      {
        path: "forecasts",
        element: <ForecastsPage />,
      },
      {
        path: "reports",
        element: <ReportsPage />,
      },
      {
        path: "profile",
        element: <ProfilePage />,
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);

