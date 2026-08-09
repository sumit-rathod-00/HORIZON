import {
  Bell,
  ChevronDown,
  Search,
} from "lucide-react";

export function Topbar() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-zinc-800 bg-zinc-950/95 px-6">
      {/* Search */}
      <div className="relative w-full max-w-md">
        <Search
          size={17}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
        />

        <input
          type="search"
          placeholder="Search HORIZON..."
          className="h-9 w-full rounded-lg border border-zinc-800 bg-zinc-900 pl-10 pr-4 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
        />
      </div>

      {/* Actions */}
      <div className="ml-6 flex items-center gap-3">
        <button
          type="button"
          aria-label="Notifications"
          className="relative flex h-9 w-9 items-center justify-center rounded-lg text-zinc-400 transition-colors hover:bg-zinc-900 hover:text-white"
        >
          <Bell size={18} />

          <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-cyan-400" />
        </button>

        <div className="h-6 w-px bg-zinc-800" />

        <button
          type="button"
          className="flex items-center gap-3 rounded-lg px-2 py-1.5 transition-colors hover:bg-zinc-900"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-500/10 text-xs font-semibold text-cyan-400">
            SR
          </div>

          <div className="hidden text-left sm:block">
            <p className="text-xs font-medium text-zinc-200">
              Sumit Rathod
            </p>
            <p className="text-[10px] text-zinc-500">
              Administrator
            </p>
          </div>

          <ChevronDown size={15} className="text-zinc-500" />
        </button>
      </div>
    </header>
  );
}