import { NavLink } from "react-router-dom";
import {
  ChartPieIcon,
  CloudIcon,
  DocumentTextIcon,
  HomeIcon,
  SparklesIcon,
  UserCircleIcon,
} from "@heroicons/react/24/outline";
import { clsx } from "clsx";

const navigation = [
  { label: "Дашборд", to: "/", icon: HomeIcon },
  { label: "Онбординг", to: "/onboarding", icon: SparklesIcon },
  { label: "Натальная карта", to: "/natal-chart", icon: ChartPieIcon },
  { label: "Прогнозы", to: "/forecasts", icon: CloudIcon },
  { label: "Отчёты", to: "/reports", icon: DocumentTextIcon },
  { label: "Профиль", to: "/profile", icon: UserCircleIcon },
];

export function Sidebar() {
  return (
    <aside className="hidden w-64 flex-none border-r border-neutral-200 bg-white/90 px-4 py-6 shadow-sm backdrop-blur md:block">
      <div className="flex items-center gap-2 px-3">
        <div className="h-9 w-9 rounded-full bg-primary-100 text-primary-700 shadow-card" />
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
            Horoscopus
          </p>
          <p className="text-xs text-neutral-400">BioAstrology 2.0</p>
        </div>
      </div>

      <nav className="mt-8 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-100 text-primary-700"
                  : "text-neutral-500 hover:bg-neutral-100 hover:text-neutral-800",
              )
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

