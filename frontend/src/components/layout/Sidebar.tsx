import {
  Activity,
  Bug,
  Cpu,
  FolderKanban,
  LayoutDashboard,
  LogOut,
  ScanSearch,
  Settings,
  Shield,
  TrendingUp,
  User,
  Users,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const navigation = [
  {
    label: "Overview",
    items: [
      { label: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
      { label: "Projects", icon: FolderKanban, path: "/projects" },
    ],
  },
  {
    label: "Security",
    items: [
      { label: "Security Center", icon: Shield, path: "/security-center" },
      { label: "Intelligence", icon: TrendingUp, path: "/intelligence" },
      { label: "Scans", icon: ScanSearch, path: "/scans" },
      { label: "Vulnerabilities", icon: Bug, path: "/vulnerabilities" },
      { label: "Assets", icon: Activity, path: "/assets" },
      { label: "Devices", icon: Cpu, path: "/devices" },
    ],
  },
  {
    label: "Management",
    items: [
      { label: "Users", icon: Users, path: "/users" },
    ],
  },
];

export function Sidebar() {
  return (
    <aside className="flex h-screen w-64 flex-col border-r border-zinc-800 bg-zinc-950">
      {/* Brand */}
      <div className="flex h-16 items-center gap-3 border-b border-zinc-800 px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400">
          <Shield size={20} />
        </div>

        <div>
          <h1 className="text-sm font-semibold tracking-wide text-white">
            HORIZON
          </h1>
          <p className="text-[10px] uppercase tracking-widest text-zinc-500">
            Security Platform
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-5">
        {navigation.map((section) => (
          <div key={section.label} className="mb-6">
            <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-zinc-600">
              {section.label}
            </p>

            <div className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                        isActive
                          ? "bg-cyan-500/10 text-cyan-400"
                          : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
                      }`
                    }
                  >
                    <Icon
                      size={17}
                      className="text-zinc-500 transition-colors group-hover:text-cyan-400"
                    />

                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Bottom navigation */}
      <div className="border-t border-zinc-800 p-3">
        <NavLink
          to="/profile"
          className={({ isActive }) =>
            `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
              isActive
                ? "bg-cyan-500/10 text-cyan-400"
                : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
            }`
          }
        >
          <User size={17} />
          Profile
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
              isActive
                ? "bg-cyan-500/10 text-cyan-400"
                : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
            }`
          }
        >
          <Settings size={17} />
          Settings
        </NavLink>

        <button
          type="button"
          className="mt-1 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-zinc-400 hover:bg-red-500/10 hover:text-red-400"
        >
          <LogOut size={17} />
          Logout
        </button>
      </div>
    </aside>
  );
}