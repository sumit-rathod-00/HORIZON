import { useEffect, useState } from "react";
import { Play, ShieldCheck, RefreshCw } from "lucide-react";

import {
  createScan,
  deleteScan,
  getAssetScans,
  updateScanStatus,
} from "../api/scans";
import { getProjectAssets } from "../api/assets";

import type { Asset, Scan } from "../types/security";
import { getSelectedProjectId } from "../lib/project-storage";

export function Scans() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState("");
  const [scans, setScans] = useState<Scan[]>([]);

  const [loadingAssets, setLoadingAssets] = useState(true);
  const [loadingScans, setLoadingScans] = useState(false);
  const [creatingScan, setCreatingScan] = useState(false);

  const [error, setError] = useState("");

  const selectedProjectId = getSelectedProjectId();

  async function loadAssets() {
    if (!selectedProjectId) {
      setLoadingAssets(false);
      return;
    }

    try {
      setLoadingAssets(true);
      setError("");

      const data = await getProjectAssets(selectedProjectId);

      setAssets(data);

      if (data.length > 0) {
        setSelectedAssetId((current) =>
          current && data.some((asset) => asset.id === current)
            ? current
            : data[0].id,
        );
      } else {
        setSelectedAssetId("");
        setScans([]);
      }
    } catch (err) {
      console.error("Failed to load assets:", err);
      setError("Unable to load project assets.");
    } finally {
      setLoadingAssets(false);
    }
  }

  async function loadScans(assetId: string) {
    if (!assetId) {
      setScans([]);
      return;
    }

    try {
      setLoadingScans(true);
      setError("");

      const data = await getAssetScans(assetId);

      setScans(data);
    } catch (err) {
      console.error("Failed to load scans:", err);
      setError("Unable to load scans.");
    } finally {
      setLoadingScans(false);
    }
  }

  async function handleStartScan() {
    if (!selectedAssetId) {
      return;
    }
    try {
      setCreatingScan(true);
      setError("");
      await createScan(selectedAssetId, {
        scanner: "HORIZON Scanner",
      });
      await loadScans(selectedAssetId);
    } catch (err) {
      console.error("Failed to create scan:", err);
      setError("Unable to start scan.");
    } finally {
      setCreatingScan(false);
    }
  }

  async function handleStatusChange(
    scanId: string,
    status: string,
  ) {
    try {
      setError("");
      await updateScanStatus(scanId, status);
      await loadScans(selectedAssetId);
    } catch (err) {
      console.error(
        "Failed to update scan status:",
        err,
      );
      setError("Unable to update scan status.");
    }
  }

  async function handleDeleteScan(scanId: string) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this scan?",
    );
    if (!confirmed) {
      return;
    }
    try {
      setError("");
      await deleteScan(scanId);
      await loadScans(selectedAssetId);
    } catch (err) {
      console.error("Failed to delete scan:", err);
      setError("Unable to delete scan.");
    }
  }

  useEffect(() => {
    loadAssets();
  }, [selectedProjectId]);

  useEffect(() => {
    if (selectedAssetId) {
      loadScans(selectedAssetId);
    }
  }, [selectedAssetId]);

  useEffect(() => {
    if (!selectedAssetId) {
      return;
    }
    const hasActiveScan = scans.some(
      (scan) =>
        scan.status === "Pending" ||
        scan.status === "Running",
    );
    if (!hasActiveScan) {
      return;
    }
    const interval = window.setInterval(() => {
      loadScans(selectedAssetId);
    }, 1000);
    return () => {
      window.clearInterval(interval);
    };
  }, [selectedAssetId, scans]);

  if (!selectedProjectId) {
    return (
      <div className="p-8">
        <p className="mb-2 text-sm text-cyan-400">
          HORIZON
        </p>

        <h1 className="text-2xl font-semibold text-white">
          Scans
        </h1>

        <div className="mt-8 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-12 text-center">
          <ShieldCheck
            size={34}
            className="mx-auto mb-4 text-zinc-600"
          />

          <h2 className="text-lg font-medium text-white">
            No project selected
          </h2>

          <p className="mt-2 text-sm text-zinc-500">
            Select a project before managing security scans.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-cyan-400">
            <ShieldCheck size={18} />

            <span className="text-xs font-medium uppercase tracking-[0.18em]">
              Security Operations
            </span>
          </div>

          <h1 className="text-2xl font-semibold text-white">
            Scans
          </h1>

          <p className="mt-2 text-sm text-zinc-500">
            Run and monitor security scans against project assets.
          </p>
        </div>

        <button
          type="button"
          onClick={() =>
            selectedAssetId && loadScans(selectedAssetId)
          }
          disabled={!selectedAssetId || loadingScans}
          className="flex items-center gap-2 rounded-xl border border-white/[0.08] px-4 py-2.5 text-sm text-zinc-300 transition hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Asset selector */}
      <div className="mb-8 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-white">
            Select Asset
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            Choose the asset whose scans you want to inspect.
          </p>
        </div>

        {loadingAssets ? (
          <p className="text-sm text-zinc-500">
            Loading assets...
          </p>
        ) : assets.length === 0 ? (
          <div className="rounded-xl border border-white/[0.06] bg-black/20 p-6 text-center">
            <p className="text-sm text-zinc-500">
              No assets available for this project.
            </p>

            <p className="mt-1 text-xs text-zinc-600">
              Create an asset first before starting a scan.
            </p>
          </div>
        ) : (
          <select
            value={selectedAssetId}
            onChange={(event) =>
              setSelectedAssetId(event.target.value)
            }
            className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
          >
            {assets.map((asset) => (
              <option
                key={asset.id}
                value={asset.id}
                className="bg-zinc-900"
              >
                {asset.name} — {asset.asset_type}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Scans */}
      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025]">
        <div className="flex items-center justify-between border-b border-white/[0.06] px-6 py-5">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Scan History
            </h2>

            <p className="mt-1 text-sm text-zinc-500">
              Security scans associated with the selected asset.
            </p>
          </div>

          {selectedAssetId && (
            <button
              type="button"
              onClick={handleStartScan}
              disabled={creatingScan || !selectedAssetId}
              className="flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Play size={16} />
              {creatingScan ? "Starting..." : "Start Scan"}
            </button>
          )}
        </div>

        {loadingScans ? (
          <div className="p-10 text-center text-sm text-zinc-500">
            Loading scans...
          </div>
        ) : scans.length === 0 ? (
          <div className="p-12 text-center">
            <ShieldCheck
              size={32}
              className="mx-auto mb-4 text-zinc-600"
            />

            <h3 className="text-lg font-medium text-white">
              No scans yet
            </h3>

            <p className="mt-2 text-sm text-zinc-500">
              This asset has not been scanned yet.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-white/[0.06]">
            {scans.map((scan) => (
              <div
                key={scan.id}
                className="flex items-center justify-between px-6 py-5"
              >
                <div>
                  <p className="text-sm font-medium text-white">
                    {scan.scanner}
                  </p>

                  <p className="mt-1 text-xs text-zinc-500">
                    Started{" "}
                    {new Date(
                      scan.started_at,
                    ).toLocaleString()}
                  </p>
                </div>

                <div className="flex items-center justify-end gap-4">
                  <div className="text-right">
                    <select
                      value={scan.status}
                      onChange={(event) =>
                        handleStatusChange(
                          scan.id,
                          event.target.value,
                        )
                      }
                      className="rounded-full border border-cyan-400/20 bg-black/30 px-3 py-1 text-xs text-cyan-300 outline-none"
                    >
                      <option value="Pending">Pending</option>
                      <option value="Running">Running</option>
                      <option value="Completed">Completed</option>
                      <option value="Failed">Failed</option>
                    </select>

                    {scan.completed_at && (
                      <p className="mt-2 text-xs text-zinc-600">
                        Completed{" "}
                        {new Date(
                          scan.completed_at,
                        ).toLocaleString()}
                      </p>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      handleDeleteScan(scan.id)
                    }
                    className="ml-4 rounded-lg border border-red-500/20 px-3 py-1.5 text-xs text-red-400 transition hover:bg-red-500/10 hover:text-red-300"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}