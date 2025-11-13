import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell() {
  return (
    <div className="flex h-screen overflow-hidden bg-neutral-50 text-neutral-900">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 overflow-y-auto bg-white px-6 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

