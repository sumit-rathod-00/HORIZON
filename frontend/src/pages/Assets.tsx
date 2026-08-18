import { useEffect, useState } from "react";
import { Box, Plus, X } from "lucide-react";

import {
  createAsset,
  deleteAsset,
  getProjectAssets,
} from "../api/assets";

import { getProjects } from "../api/projects";

import type { Asset, Project } from "../types/security";

export function Assets() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] =
    useState("");

  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);

  const [showCreateForm, setShowCreateForm] =
    useState(false);

  const [name, setName] = useState("");
  const [assetType, setAssetType] = useState("");
  const [ipAddress, setIpAddress] = useState("");

  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  // Load projects
  useEffect(() => {
    async function loadProjects() {
      try {
        const data = await getProjects();

        setProjects(data);

        if (data.length > 0) {
          setSelectedProjectId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load projects:", err);
        setError("Unable to load projects.");
      }
    }

    loadProjects();
  }, []);

  // Load assets for selected project
  useEffect(() => {
    if (!selectedProjectId) {
      setAssets([]);
      setLoading(false);
      return;
    }

    async function loadAssets() {
      try {
        setLoading(true);
        setError("");

        const data = await getProjectAssets(
          selectedProjectId,
        );

        setAssets(data);
      } catch (err) {
        console.error("Failed to load assets:", err);
        setError("Unable to load assets.");
      } finally {
        setLoading(false);
      }
    }

    loadAssets();
  }, [selectedProjectId]);

  async function handleCreateAsset(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    if (!selectedProjectId) {
      setError("Please select a project first.");
      return;
    }

    if (!name.trim()) {
      setError("Asset name is required.");
      return;
    }

    if (!assetType.trim()) {
      setError("Asset type is required.");
      return;
    }

    try {
      setCreating(true);
      setError("");

      const asset = await createAsset(
        selectedProjectId,
        {
          name: name.trim(),
          asset_type: assetType.trim(),
          ip_address:
            ipAddress.trim() || undefined,
        },
      );

      setAssets((current) => [
        asset,
        ...current,
      ]);

      setName("");
      setAssetType("");
      setIpAddress("");
      setShowCreateForm(false);
    } catch (err) {
      console.error(
        "Failed to create asset:",
        err,
      );

      setError("Unable to create asset.");
    } finally {
      setCreating(false);
    }
  }

  async function handleDeleteAsset(
    assetId: string,
  ) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this asset?",
    );
    if (!confirmed) {
      return;
    }
    try {
      setError("");
      await deleteAsset(assetId);
      setAssets((current) =>
        current.filter(
          (asset) => asset.id !== assetId,
        ),
      );
    } catch (err) {
      console.error(
        "Failed to delete asset:",
        err,
      );
      setError("Unable to delete asset.");
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-cyan-400">
            <Box size={18} />

            <span className="text-xs font-medium uppercase tracking-[0.18em]">
              Security Management
            </span>
          </div>

          <h1 className="text-2xl font-semibold text-white">
            Assets
          </h1>

          <p className="mt-2 text-sm text-zinc-500">
            Manage the assets monitored by HORIZON.
          </p>
        </div>

        <button
          onClick={() =>
            setShowCreateForm(true)
          }
          disabled={!selectedProjectId}
          className="flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Plus size={17} />
          New Asset
        </button>
      </div>

      {/* Project selector */}
      <div className="mb-6 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-5">
        <label
          htmlFor="project-select"
          className="mb-2 block text-sm font-medium text-zinc-300"
        >
          Project
        </label>

        <select
          id="project-select"
          value={selectedProjectId}
          onChange={(event) =>
            setSelectedProjectId(
              event.target.value,
            )
          }
          className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
        >
          {projects.length === 0 ? (
            <option value="">
              No projects available
            </option>
          ) : (
            projects.map((project) => (
              <option
                key={project.id}
                value={project.id}
              >
                {project.name}
              </option>
            ))
          )}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Create Asset Form */}
      {showCreateForm && (
        <div className="mb-8 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">
              Create Asset
            </h2>

            <button
              type="button"
              onClick={() =>
                setShowCreateForm(false)
              }
              className="rounded-lg p-2 text-zinc-500 transition hover:bg-white/5 hover:text-white"
            >
              <X size={18} />
            </button>
          </div>

          <form
            onSubmit={handleCreateAsset}
            className="space-y-5"
          >
            {/* Name */}
            <div>
              <label
                htmlFor="asset-name"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                Asset name
              </label>

              <input
                id="asset-name"
                value={name}
                onChange={(event) =>
                  setName(event.target.value)
                }
                placeholder="e.g. Production Server"
                disabled={creating}
                className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

            {/* Asset type */}
            <div>
              <label
                htmlFor="asset-type"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                Asset type
              </label>

              <input
                id="asset-type"
                value={assetType}
                onChange={(event) =>
                  setAssetType(event.target.value)
                }
                placeholder="e.g. Server, Website, API"
                disabled={creating}
                className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

            {/* IP */}
            <div>
              <label
                htmlFor="asset-ip"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                IP address
              </label>

              <input
                id="asset-ip"
                value={ipAddress}
                onChange={(event) =>
                  setIpAddress(event.target.value)
                }
                placeholder="e.g. 192.168.1.10"
                disabled={creating}
                className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

            {/* Buttons */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() =>
                  setShowCreateForm(false)
                }
                disabled={creating}
                className="rounded-xl border border-white/[0.08] px-4 py-2.5 text-sm text-zinc-400 transition hover:bg-white/5 hover:text-white"
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={creating}
                className="rounded-xl bg-cyan-400 px-5 py-2.5 text-sm font-semibold text-black transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {creating
                  ? "Creating..."
                  : "Create Asset"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Assets */}
      {loading ? (
        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-10 text-center text-sm text-zinc-500">
          Loading assets...
        </div>
      ) : !selectedProjectId ? (
        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-12 text-center">
          <Box
            size={32}
            className="mx-auto mb-4 text-zinc-600"
          />

          <h2 className="text-lg font-medium text-white">
            No project selected
          </h2>

          <p className="mt-2 text-sm text-zinc-500">
            Create a project first before adding
            assets.
          </p>
        </div>
      ) : assets.length === 0 ? (
        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-12 text-center">
          <Box
            size={32}
            className="mx-auto mb-4 text-zinc-600"
          />

          <h2 className="text-lg font-medium text-white">
            No assets yet
          </h2>

          <p className="mt-2 text-sm text-zinc-500">
            Add your first asset to start monitoring
            this project.
          </p>

          <button
            onClick={() =>
              setShowCreateForm(true)
            }
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-black hover:bg-cyan-300"
          >
            <Plus size={17} />
            Create Asset
          </button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {assets.map((asset) => (
            <div
              key={asset.id}
              className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/5">
                <Box
                  size={19}
                  className="text-cyan-400"
                />
              </div>

              <h2 className="text-lg font-semibold text-white">
                {asset.name}
              </h2>

              <p className="mt-2 text-sm text-zinc-500">
                Type: {asset.asset_type}
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                IP: {asset.ip_address || "Not provided"}
              </p>

              <div className="mt-5 flex justify-end">
                <button
                  type="button"
                  onClick={() =>
                    handleDeleteAsset(asset.id)
                  }
                  className="rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 text-sm font-medium text-red-300 transition hover:bg-red-500/10 hover:text-red-200"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}