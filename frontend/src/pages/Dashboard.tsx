import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Bug,
  FolderKanban,
  Loader2,
  ScanSearch,
  ShieldCheck,
} from "lucide-react";

import { getDashboardData } from "../api/dashboard";
import type { DashboardData } from "../api/dashboard";

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const dashboardData = await getDashboardData();

        if (mounted) {
          setData(dashboardData);
        }
      } catch (err) {
        console.error("Dashboard loading failed:", err);

        if (mounted) {
          setError("Unable to load security dashboard data.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      mounted = false;
    };
  }, []);

  const severityCounts = useMemo(() => {
    const vulnerabilities = data?.vulnerabilities ?? [];

    return {
      critical: vulnerabilities.filter(
        (item) => item.severity.toLowerCase() === "critical",
      ).length,

      high: vulnerabilities.filter(
        (item) => item.severity.toLowerCase() === "high",
      ).length,

      medium: vulnerabilities.filter(
        (item) => item.severity.toLowerCase() === "medium",
      ).length,

      low: vulnerabilities.filter(
        (item) => item.severity.toLowerCase() === "low",
      ).length,
    };
  }, [data]);

  const totalVulnerabilities = data?.vulnerabilities.length ?? 0;

  const severityPercentage = (count: number) => {
    if (totalVulnerabilities === 0) {
      return 0;
    }

    return Math.round((count / totalVulnerabilities) * 100);
  };

  const stats = [
    {
      label: "Active Projects",
      value: data?.projects.length ?? 0,
      description: "Projects under monitoring",
      icon: FolderKanban,
    },
    {
      label: "Security Scans",
      value: data?.scans.length ?? 0,
      description: "Scans recorded",
      icon: ScanSearch,
    },
    {
      label: "Vulnerabilities",
      value: data?.vulnerabilities.length ?? 0,
      description: "Issues detected",
      icon: Bug,
    },
    {
      label: "Assets",
      value: data?.assets.length ?? 0,
      description: "Assets being monitored",
      icon: Activity,
    },
  ];

  const hasActivity =
    data !== null &&
    (
      data.projects.length > 0 ||
      data.assets.length > 0 ||
      data.scans.length > 0 ||
      data.vulnerabilities.length > 0
    );

  const recentActivity = data
    ? [
        ...data.vulnerabilities.map((item) => ({
          id: item.id,
          title: item.title,
          detail: `Vulnerability · ${item.severity}`,
          date: item.created_at,
        })),

        ...data.scans.map((item) => ({
          id: item.id,
          title: `${item.scanner} scan`,
          detail: `Scan · ${item.status}`,
          date: item.started_at,
        })),
      ]
        .sort(
          (a, b) =>
            new Date(b.date).getTime() -
            new Date(a.date).getTime(),
        )
        .slice(0, 5)
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}

      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
            <span className="h-2 w-2 rounded-full bg-cyan-400" />
            Security Overview
          </div>

          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">
            Dashboard
          </h1>

          <p className="mt-2 text-sm text-zinc-500">
            Monitor your HORIZON security environment from a
            single operational view.
          </p>
        </div>

        <div className="hidden rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-4 py-2 sm:block">
          <div className="flex items-center gap-2 text-xs font-medium text-emerald-400">
            <ShieldCheck size={15} />
            System Operational
          </div>

          <p className="mt-0.5 text-[10px] text-zinc-500">
            All services available
          </p>
        </div>
      </div>

      {/* Loading */}

      {loading && (
        <div className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 text-sm text-zinc-400">
          <Loader2 size={17} className="animate-spin" />
          Loading security data...
        </div>
      )}

      {/* Error */}

      {error && !loading && (
        <div className="flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          <AlertTriangle size={17} />
          {error}
        </div>
      )}

      {/* Stats */}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;

          return (
            <div
              key={stat.label}
              className="group rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 transition-colors hover:border-cyan-500/20"
            >
              <div className="flex items-start justify-between">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-950 text-cyan-400">
                  <Icon size={18} />
                </div>

                <span className="text-zinc-700">↗</span>
              </div>

              <p className="mt-5 text-sm text-zinc-500">
                {stat.label}
              </p>

              <p className="mt-2 text-3xl font-semibold text-white">
                {loading ? "—" : stat.value}
              </p>

              <p className="mt-1 text-xs text-zinc-600">
                {stat.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Lower dashboard */}

      <div className="grid gap-5 xl:grid-cols-[1.7fr_1fr]">
        {/* Recent Activity */}

        <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/50">
          <div className="border-b border-zinc-800 px-5 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-white">
                  Recent Activity
                </h2>

                <p className="mt-1 text-xs text-zinc-600">
                  Latest security operations
                </p>
              </div>

              <Activity size={17} className="text-zinc-600" />
            </div>
          </div>

          <div className="min-h-52 p-5">
            {loading ? (
              <div className="flex h-48 items-center justify-center">
                <Loader2
                  size={20}
                  className="animate-spin text-cyan-400"
                />
              </div>
            ) : !hasActivity ? (
              <div className="flex h-48 items-center justify-center">
                <div className="text-center">
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl border border-zinc-800 bg-zinc-950 text-zinc-600">
                    <Activity size={20} />
                  </div>

                  <h3 className="mt-4 text-sm font-medium text-zinc-300">
                    No activity yet
                  </h3>

                  <p className="mx-auto mt-2 max-w-sm text-xs leading-5 text-zinc-600">
                    Security activity will appear here once
                    projects, scans, and assets are added to
                    HORIZON.
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {recentActivity.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-950/50 px-4 py-3"
                  >
                    <div>
                      <p className="text-sm text-zinc-300">
                        {item.title}
                      </p>

                      <p className="mt-1 text-xs text-zinc-600">
                        {item.detail}
                      </p>
                    </div>

                    <span className="text-[10px] text-zinc-600">
                      {new Date(
                        item.date,
                      ).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Vulnerability Severity */}

        <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/50">
          <div className="border-b border-zinc-800 px-5 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-white">
                  Vulnerability Severity
                </h2>

                <p className="mt-1 text-xs text-zinc-600">
                  Current vulnerability distribution
                </p>
              </div>

              <AlertTriangle
                size={17}
                className="text-zinc-600"
              />
            </div>
          </div>

          <div className="space-y-5 p-5">
            {[
              {
                label: "Critical",
                count: severityCounts.critical,
                percentage: severityPercentage(
                  severityCounts.critical,
                ),
                text: "text-red-400",
              },
              {
                label: "High",
                count: severityCounts.high,
                percentage: severityPercentage(
                  severityCounts.high,
                ),
                text: "text-orange-400",
              },
              {
                label: "Medium",
                count: severityCounts.medium,
                percentage: severityPercentage(
                  severityCounts.medium,
                ),
                text: "text-yellow-400",
              },
              {
                label: "Low",
                count: severityCounts.low,
                percentage: severityPercentage(
                  severityCounts.low,
                ),
                text: "text-cyan-400",
              },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex items-center justify-between text-xs">
                  <span className={item.text}>
                    {item.label}
                  </span>

                  <span className={item.text}>
                    {item.count}
                  </span>
                </div>

                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-zinc-800">
                  <div
                    className={`h-full rounded-full bg-current ${item.text}`}
                    style={{
                      width: `${item.percentage}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Security Posture */}

      <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-cyan-500/20 bg-cyan-500/5 text-cyan-400">
              <ShieldCheck size={20} />
            </div>

            <div>
              <h2 className="text-sm font-semibold text-white">
                Security Posture
              </h2>

              <p className="mt-1 text-xs text-zinc-600">
                Overall security health of your environment
              </p>
            </div>
          </div>

          <div className="text-right">
            <p className="text-[10px] uppercase tracking-wider text-zinc-600">
              Current score
            </p>

            <p className="mt-1 text-2xl font-semibold text-zinc-400">
              N/A
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}