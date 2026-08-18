const SELECTED_PROJECT_KEY = "horizon_selected_project_id";

export function getSelectedProjectId(): string | null {
  return localStorage.getItem(SELECTED_PROJECT_KEY);
}

export function setSelectedProjectId(projectId: string): void {
  localStorage.setItem(SELECTED_PROJECT_KEY, projectId);
}

export function clearSelectedProjectId(): void {
  localStorage.removeItem(SELECTED_PROJECT_KEY);
}