import { useEffect, useState } from "react";
import { Cpu, Plus, ShieldCheck, ShieldOff, X } from "lucide-react";

import {
  activateDevice,
  enrollDevice,
  getDevices,
  revokeDevice,
} from "../api/devices";

import type {
  Device,
  DeviceStatus,
} from "../types/security";

const STATUS_LABELS: Record<DeviceStatus, string> = {
  pending: "Pending",
  active: "Active",
  inactive: "Inactive",
  revoked: "Revoked",
};

const STATUS_STYLES: Record<DeviceStatus, string> = {
  pending: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  inactive: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
  revoked: "bg-red-500/10 text-red-400 border-red-500/20",
};

function formatLastSeen(lastSeen: string | null): string {
  if (!lastSeen) {
    return "Never";
  }

  return new Date(lastSeen).toLocaleString();
}

export function Devices() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showEnrollForm, setShowEnrollForm] = useState(false);
  const [enrolling, setEnrolling] = useState(false);

  const [name, setName] = useState("");
  const [platform, setPlatform] = useState("");
  const [operatingSystem, setOperatingSystem] = useState("");
  const [deviceType, setDeviceType] = useState("");

  const [enrollmentToken, setEnrollmentToken] = useState("");
  const [enrollmentMessage, setEnrollmentMessage] = useState("");

  async function loadDevices() {
    try {
      setLoading(true);
      setError("");
      const data = await getDevices();
      setDevices(data);
    } catch (err) {
      console.error("Failed to load devices:", err);
      setError("Unable to load devices.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDevices();
  }, []);

  async function handleEnrollDevice(event: React.FormEvent) {
    event.preventDefault();

    if (!name.trim()) {
      setError("Device name is required.");
      return;
    }

    try {
      setEnrolling(true);
      setError("");

      const result = await enrollDevice({
        name: name.trim(),
        platform: platform.trim() || undefined,
        operating_system: operatingSystem.trim() || undefined,
        device_type: deviceType.trim() || undefined,
      });

      setDevices((current) => [result.device, ...current]);
      setEnrollmentToken(result.enrollment_token);
      setEnrollmentMessage(result.message);

      setName("");
      setPlatform("");
      setOperatingSystem("");
      setDeviceType("");
    } catch (err) {
      console.error("Failed to enroll device:", err);
      setError("Unable to enroll device.");
    } finally {
      setEnrolling(false);
    }
  }

  async function handleActivate(deviceId: string) {
    try {
      setError("");
      const updated = await activateDevice(deviceId);
      setDevices((current) =>
        current.map((device) =>
          device.id === updated.id ? updated : device,
        ),
      );
    } catch (err) {
      console.error("Failed to activate device:", err);
      setError("Unable to activate device.");
    }
  }

  async function handleRevoke(device: Device) {
    const confirmed = window.confirm(
      `Revoke "${device.name}"? This will prevent further operations.`,
    );
    if (!confirmed) {
      return;
    }

    try {
      setError("");
      const updated = await revokeDevice(device.id);
      setDevices((current) =>
        current.map((item) =>
          item.id === updated.id ? updated : item,
        ),
      );
    } catch (err) {
      console.error("Failed to revoke device:", err);
      setError("Unable to revoke device.");
    }
  }

  function resetEnrollment() {
    setShowEnrollForm(false);
    setEnrollmentToken("");
    setEnrollmentMessage("");
    setError("");
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-cyan-400">
            <Cpu size={18} />

            <span className="text-xs font-medium uppercase tracking-[0.18em]">
              Universal Device Protection
            </span>
          </div>

          <h1 className="text-2xl font-semibold text-white">
            Devices
          </h1>

          <p className="mt-2 text-sm text-zinc-500">
            Enroll and manage the devices protected by HORIZON.
          </p>
        </div>

        <button
          onClick={() => setShowEnrollForm(true)}
          className="flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-cyan-300"
        >
          <Plus size={17} />
          Enroll Device
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Enrollment success / token */}
      {enrollmentToken && (
        <div className="mb-8 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-6">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">
              Device enrolled successfully
            </h2>

            <button
              type="button"
              onClick={resetEnrollment}
              className="rounded-lg p-2 text-zinc-400 transition hover:bg-white/5 hover:text-white"
            >
              <X size={18} />
            </button>
          </div>

          <p className="mb-4 text-sm text-zinc-400">
            {enrollmentMessage}
          </p>

          <div>
            <p className="mb-2 text-sm font-medium text-zinc-300">
              Enrollment token (store securely, shown only once):
            </p>

            <code className="block select-all break-all rounded-xl border border-emerald-500/20 bg-black/40 px-4 py-3 text-sm text-emerald-300">
              {enrollmentToken}
            </code>
          </div>
        </div>
      )}

      {/* Enroll form */}
      {showEnrollForm && (
        <div className="mb-8 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">
              Enroll New Device
            </h2>

            <button
              type="button"
              onClick={resetEnrollment}
              className="rounded-lg p-2 text-zinc-500 transition hover:bg-white/5 hover:text-white"
            >
              <X size={18} />
            </button>
          </div>

          <form
            onSubmit={handleEnrollDevice}
            className="space-y-5"
          >
            {/* Name */}
            <div>
              <label
                htmlFor="device-name"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                Device name
              </label>

              <input
                id="device-name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. Work Laptop"
                disabled={enrolling}
                className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

            {/* Platform */}
            <div>
              <label
                htmlFor="device-platform"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                Platform
              </label>

              <input
                id="device-platform"
                value={platform}
                onChange={(event) => setPlatform(event.target.value)}
                placeholder="e.g. Windows, macOS, Linux, Android, iOS"
                disabled={enrolling}
                className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

            {/* Operating system */}
            <div>
              <label
                htmlFor="device-os"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                Operating system
              </label>

              <input
                id="device-os"
                value={operatingSystem}
                onChange={(event) => setOperatingSystem(event.target.value)}
                placeholder="e.g. Windows 11 Pro"
                disabled={enrolling}
                className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

            {/* Device type */}
            <div>
              <label
                htmlFor="device-type"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                Device type
              </label>

              <input
                id="device-type"
                value={deviceType}
                onChange={(event) => setDeviceType(event.target.value)}
                placeholder="e.g. Laptop, Desktop, Server, Mobile"
                disabled={enrolling}
                className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

            {/* Buttons */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={resetEnrollment}
                disabled={enrolling}
                className="rounded-xl border border-white/[0.08] px-4 py-2.5 text-sm text-zinc-400 transition hover:bg-white/5 hover:text-white"
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={enrolling}
                className="rounded-xl bg-cyan-400 px-5 py-2.5 text-sm font-semibold text-black transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {enrolling ? "Enrolling..." : "Enroll Device"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Device list */}
      {loading ? (
        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-10 text-center text-sm text-zinc-500">
          Loading devices...
        </div>
      ) : devices.length === 0 ? (
        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-12 text-center">
          <Cpu
            size={32}
            className="mx-auto mb-4 text-zinc-600"
          />

          <h2 className="text-lg font-medium text-white">
            No devices enrolled
          </h2>

          <p className="mt-2 text-sm text-zinc-500">
            Enroll your first device to start protecting it.
          </p>

          <button
            onClick={() => setShowEnrollForm(true)}
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-black hover:bg-cyan-300"
          >
            <Plus size={17} />
            Enroll Device
          </button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {devices.map((device) => (
            <div
              key={device.id}
              className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6"
            >
              <div className="mb-4 flex items-start justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/5">
                  <Cpu
                    size={19}
                    className="text-cyan-400"
                  />
                </div>

                <span
                  className={`rounded-full border px-3 py-1 text-xs font-medium ${STATUS_STYLES[device.status]}`}
                >
                  {STATUS_LABELS[device.status]}
                </span>
              </div>

              <h2 className="text-lg font-semibold text-white">
                {device.name}
              </h2>

              <p className="mt-2 text-sm text-zinc-500">
                Type: {device.device_type || "Not specified"}
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                Platform: {device.platform || "Not specified"}
              </p>

              {device.operating_system && (
                <p className="mt-1 text-sm text-zinc-500">
                  OS: {device.operating_system}
                </p>
              )}

              <p className="mt-1 text-sm text-zinc-500">
                Last seen: {formatLastSeen(device.last_seen)}
              </p>

              <div className="mt-5 flex justify-end gap-2">
                {device.status === "pending" && (
                  <button
                    type="button"
                    onClick={() => handleActivate(device.id)}
                    className="flex items-center gap-1.5 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-3 py-2 text-sm font-medium text-emerald-300 transition hover:bg-emerald-500/10 hover:text-emerald-200"
                  >
                    <ShieldCheck size={15} />
                    Activate
                  </button>
                )}

                {device.status !== "revoked" && (
                  <button
                    type="button"
                    onClick={() => handleRevoke(device)}
                    className="flex items-center gap-1.5 rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 text-sm font-medium text-red-300 transition hover:bg-red-500/10 hover:text-red-200"
                  >
                    <ShieldOff size={15} />
                    Revoke
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
