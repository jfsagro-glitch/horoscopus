import { useState } from "react";
import { clsx } from "clsx";
import { MagnifyingGlassIcon, BellIcon } from "@heroicons/react/24/outline";

export function Topbar() {
  const [query, setQuery] = useState("");

  return (
    <header className="flex flex-none items-center justify-between border-b border-neutral-200 bg-white/70 px-6 py-4 shadow-sm backdrop-blur">
      <div className="flex items-center gap-3">
        <div className="relative">
          <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-400" />
          <input
            type="search"
            placeholder="Поиск по картам и прогнозам"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className={clsx(
              "w-72 rounded-full border border-neutral-200 bg-white py-2 pl-10 pr-4 text-sm",
              "placeholder:text-neutral-400 focus:border-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-200",
            )}
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button
          type="button"
          className="relative flex h-9 w-9 items-center justify-center rounded-full border border-neutral-200 text-neutral-500 transition hover:border-primary-200 hover:text-primary-600"
        >
          <BellIcon className="h-5 w-5" />
          <span className="absolute right-0 top-0 h-2 w-2 rounded-full bg-primary-500" />
        </button>
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-500 text-white">
          Ю
        </div>
      </div>
    </header>
  );
}

