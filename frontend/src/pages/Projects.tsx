import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FolderKanban, Plus, X } from "lucide-react";

import {
  createProject,
  getProjects,
} from "../api/projects";

import {
  setSelectedProjectId,
} from "../lib/project-storage";

import type { Project } from "../types/security";

export function Projects() {
  const navigate = useNavigate();

  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const [showCreateForm, setShowCreateForm] =
    useState(false);

  const [name, setName] = useState("");
  const [description, setDescription] =
    useState("");

  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  async function loadProjects() {
    try {
      setLoading(true);
      setError("");

      const data = await getProjects();

      setProjects(data);
    } catch (err) {
      console.error("Failed to load projects:", err);
      setError("Unable to load projects.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProjects();
  }, []);

  async function handleCreateProject(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    if (!name.trim()) {
      setError("Project name is required.");
      return;
    }

    try {
      setCreating(true);
      setError("");

      const project = await createProject({
        name: name.trim(),
        description: description.trim() || undefined,
      });

      setProjects((current) => [
        project,
        ...current,
      ]);

      setName("");
      setDescription("");
      setShowCreateForm(false);
    } catch (err) {
      console.error(
        "Failed to create project:",
        err,
      );

      setError("Unable to create project.");
    } finally {
      setCreating(false);
    }
  }

  function handleSelectProject(projectId: string) {
    setSelectedProjectId(projectId);
    navigate("/assets");
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-cyan-400">
            <FolderKanban size={18} />

            <span className="text-xs font-medium uppercase tracking-[0.18em]">
              Security Management
            </span>
          </div>

          <h1 className="text-2xl font-semibold text-white">
            Projects
          </h1>

          <p className="mt-2 text-sm text-zinc-500">
            Manage the security projects monitored by
            HORIZON.
          </p>
        </div>

        <button
          onClick={() =>
            setShowCreateForm(true)
          }
          className="flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-cyan-300"
        >
          <Plus size={17} />
          New Project
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Create form */}
      {showCreateForm && (
        <div className="mb-8 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">
              Create Project
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
            onSubmit={handleCreateProject}
            className="space-y-5"
          >
            <div>
              <label
                htmlFor="project-name"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                Project name
              </label>

              <input
                id="project-name"
                value={name}
                onChange={(event) =>
                  setName(event.target.value)
                }
                placeholder="e.g. HORIZON Web Security"
                disabled={creating}
                className="w-full rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

            <div>
              <label
                htmlFor="project-description"
                className="mb-2 block text-sm font-medium text-zinc-300"
              >
                Description
              </label>

              <textarea
                id="project-description"
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value,
                  )
                }
                placeholder="Describe this security project..."
                rows={4}
                disabled={creating}
                className="w-full resize-none rounded-xl border border-white/[0.08] bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-cyan-400/40 focus:ring-2 focus:ring-cyan-400/10"
              />
            </div>

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
                  : "Create Project"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Projects */}
      {loading ? (
        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-10 text-center text-sm text-zinc-500">
          Loading projects...
        </div>
      ) : projects.length === 0 ? (
        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-12 text-center">
          <FolderKanban
            size={32}
            className="mx-auto mb-4 text-zinc-600"
          />

          <h2 className="text-lg font-medium text-white">
            No projects yet
          </h2>

          <p className="mt-2 text-sm text-zinc-500">
            Create your first security project to
            start monitoring assets and scans.
          </p>

          <button
            onClick={() =>
              setShowCreateForm(true)
            }
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-black hover:bg-cyan-300"
          >
            <Plus size={17} />
            Create Project
          </button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {projects.map((project) => (
            <div
              key={project.id}
              onClick={() => handleSelectProject(project.id)}
              className="cursor-pointer rounded-2xl border border-white/[0.08] bg-white/[0.025] p-6 transition hover:border-cyan-400/30 hover:bg-cyan-400/[0.03]"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/5">
                <FolderKanban
                  size={19}
                  className="text-cyan-400"
                />
              </div>

              <h2 className="text-lg font-semibold text-white">
                {project.name}
              </h2>

              <p className="mt-2 text-sm leading-6 text-zinc-500">
                {project.description ||
                  "No description provided."}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}