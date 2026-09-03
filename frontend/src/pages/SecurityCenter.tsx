import { useEffect, useState } from "react";
import {
  Cpu,
  Shield,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  HardDrive,
  ShieldCheck,
  AlertCircle,
} from "lucide-react";

import { getDevices } from "../api/devices";
import { getDeviceTelemetry, getDeviceEvents, type SecurityEvent, type DeviceTelemetry } from "../api/telemetry";
import type { Device } from "../types/security";

const STATUS_LABELS: Record<string, string> = {
  active: "Active",
  stale: "Stale",
  inactive: "Inactive",
  pending: "Pending",
  revoked: "Revoked",
};

const STATUS_STYLES: Record<string, string> = {
  active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  stale: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  inactive: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
  pending: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  revoked: "bg-red-500/10 text-red-400 border-red-500/20",
};

const SEVERITY_STYLES: Record<string, string> = {
  info: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  low: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
  medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  high: "bg-red-500/10 text-red-400 border-red-500/20",
  critical: "bg-red-600/20 text-red-300 border-red-600/30",
};

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "Just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function calculateDeviceState(device: Device): string {
  if (device.status === "revoked") return "revoked";
  if (!device.last_seen) return "inactive";

  const lastSeen = new Date(device.last_seen);
  const now = new Date();
  const minutesSince = (now.getTime() - lastSeen.getTime()) / 60000;

  if (minutesSince <= 5) return "active";
  if (minutesSince <= 15) return "stale";
  return "inactive";
}

interface DeviceHealthProps {
  device: Device;
  telemetry: DeviceTelemetry | null;
}

function DeviceHealthCard({ device, telemetry }: DeviceHealthProps) {
  const state = calculateDeviceState(device);

  return (
    <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">
      <div className="mb-4 flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/5">
          <Cpu size={19} className="text-cyan-400" />
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-medium ${STATUS_STYLES[state]}`}>
          {STATUS_LABELS[state]}
        </span>
      </div>

      <h3 className="text-lg font-semibold text-white">{device.name}</h3>
      <p className="mt-1 text-sm text-zinc-500">
        {device.platform || "Unknown"} • {device.device_type || "Device"}
      </p>

      <div className="mt-4 space-y-3">
        {telemetry ? (
          <>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-zinc-400">
                <Activity size={14} />
                <span>CPU</span>
              </div>
              <span className="text-zinc-300">{telemetry.cpu_usage_percent?.toFixed(1) || 0}%</span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-zinc-400">
                <HardDrive size={14} />
                <span>Disk</span>
              </div>
              <span className="text-zinc-300">{telemetry.disk_usage_percent?.toFixed(1) || 0}%</span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-zinc-400">
                <ShieldCheck size={14} />
                <span>Firewall</span>
              </div>
              <span className={telemetry.firewall_enabled ? "text-emerald-400" : "text-red-400"}>
                {telemetry.firewall_enabled ? "Enabled" : "Disabled"}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-zinc-400">
                <Clock size={14} />
                <span>Last seen</span>
              </div>
              <span className="text-zinc-300">{formatTimeAgo(telemetry.collected_at)}</span>
            </div>
          </>
        ) : (
          <p className="text-sm text-zinc-500">No telemetry data</p>
        )}
      </div>
    </div>
  );
}

interface EventListProps {
  events: SecurityEvent[];
}

function EventList({ events }: EventListProps) {
  if (events.length === 0) {
    return (
      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-8 text-center">
        <ShieldCheck size={32} className="mx-auto mb-3 text-emerald-500" />
        <p className="text-sm text-zinc-400">No security events</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {events.slice(0, 10).map((event) => (
        <div
          key={event.id}
          className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              {event.severity === "high" || event.severity === "critical" ? (
                <AlertTriangle size={16} className="text-red-400" />
              ) : (
                <AlertCircle size={16} className="text-amber-400" />
              )}
              <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${SEVERITY_STYLES[event.severity]}`}>
                {event.severity}
              </span>
            </div>
            <span className="text-xs text-zinc-500">{formatTimeAgo(event.detected_at)}</span>
          </div>

          <h4 className="mt-2 text-sm font-medium text-white">{event.title}</h4>
          {event.description && (
            <p className="mt-1 text-xs text-zinc-400">{event.description}</p>
          )}
        </div>
      ))}
    </div>
  );
}

export function SecurityCenter() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [telemetryMap, setTelemetryMap] = useState<Record<string, DeviceTelemetry | null>>({});
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);

  useEffect(() => {
    loadDevices();
  }, []);

  useEffect(() => {
    if (devices.length > 0) {
      loadTelemetryAndEvents();
    }
  }, [devices]);

  async function loadDevices() {
    try {
      setLoading(true);
      const data = await getDevices();
      setDevices(data);
    } catch (err) {
      console.error("Failed to load devices:", err);
      setError("Unable to load devices");
    } finally {
      setLoading(false);
    }
  }

  async function loadTelemetryAndEvents() {
    setEventsLoading(true);

    const telemetryData: Record<string, DeviceTelemetry | null> = {};
    const allEvents: SecurityEvent[] = [];

    for (const device of devices) {
      try {
        const [telemetry, deviceEvents] = await Promise.all([
          getDeviceTelemetry(device.id, { limit: 1 }),
          getDeviceEvents(device.id, { limit: 5 }),
        ]);

        telemetryData[device.id] = telemetry[0] || null;
        allEvents.push(...deviceEvents);
      } catch (err) {
        console.error(`Failed to load data for device ${device.id}:`, err);
        telemetryData[device.id] = null;
      }
    }

    setTelemetryMap(telemetryData);
    setEvents(allEvents.sort((a, b) =>
      new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime()
    ));
    setEventsLoading(false);
  }

  const activeCount = devices.filter(d => calculateDeviceState(d) === "active").length;
  const staleCount = devices.filter(d => calculateDeviceState(d) === "stale").length;
  const offlineCount = devices.filter(d => calculateDeviceState(d) === "inactive").length;
  const criticalEvents = events.filter(e => e.severity === "high" || e.severity === "critical");

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-2 flex items-center gap-2 text-cyan-400">
          <Shield size={18} />
          <span className="text-xs font-medium uppercase tracking-[0.18em]">
            Security Operations
          </span>
        </div>

        <h1 className="text-2xl font-semibold text-white">Security Center</h1>
        <p className="mt-2 text-sm text-zinc-500">
          Monitor your devices and security events in real-time.
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="mb-8 grid grid-cols-4 gap-4">
        <div className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4">
          <div className="flex items-center gap-2 text-zinc-400">
            <Cpu size={16} />
            <span className="text-sm">Total Devices</span>
          </div>
          <p className="mt-2 text-2xl font-semibold text-white">{devices.length}</p>
        </div>

        <div className="rounded-xl border border-emerald-500/10 bg-emerald-500/5 p-4">
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle size={16} />
            <span className="text-sm">Online</span>
          </div>
          <p className="mt-2 text-2xl font-semibold text-emerald-400">{activeCount}</p>
        </div>

        <div className="rounded-xl border border-amber-500/10 bg-amber-500/5 p-4">
          <div className="flex items-center gap-2 text-amber-400">
            <Clock size={16} />
            <span className="text-sm">Stale</span>
          </div>
          <p className="mt-2 text-2xl font-semibold text-amber-400">{staleCount}</p>
        </div>

        <div className="rounded-xl border border-red-500/10 bg-red-500/5 p-4">
          <div className="flex items-center gap-2 text-red-400">
            <XCircle size={16} />
            <span className="text-sm">Offline</span>
          </div>
          <p className="mt-2 text-2xl font-semibold text-red-400">{offlineCount}</p>
        </div>
      </div>

      {/* Critical Events Alert */}
      {criticalEvents.length > 0 && (
        <div className="mb-8 rounded-xl border border-red-500/20 bg-red-500/10 p-4">
          <div className="flex items-center gap-2 text-red-400">
            <AlertTriangle size={18} />
            <span className="font-medium">{criticalEvents.length} critical security events</span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Devices */}
        <div className="lg:col-span-2">
          <h2 className="mb-4 text-lg font-semibold text-white">Device Health</h2>

          {loading ? (
            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-10 text-center text-sm text-zinc-500">
              Loading devices...
            </div>
          ) : devices.length === 0 ? (
            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-12 text-center">
              <Shield size={32} className="mx-auto mb-4 text-zinc-600" />
              <h3 className="text-lg font-medium text-white">No devices enrolled</h3>
              <p className="mt-2 text-sm text-zinc-500">
                Enroll devices to start monitoring their security status.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {devices.map((device) => (
                <DeviceHealthCard
                  key={device.id}
                  device={device}
                  telemetry={telemetryMap[device.id] || null}
                />
              ))}
            </div>
          )}
        </div>

        {/* Events */}
        <div>
          <h2 className="mb-4 text-lg font-semibold text-white">Security Events</h2>

          {eventsLoading ? (
            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-10 text-center text-sm text-zinc-500">
              Loading events...
            </div>
          ) : (
            <EventList events={events} />
          )}
        </div>
      </div>
    </div>
  );
}