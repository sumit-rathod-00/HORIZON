import { apiClient } from "./client";
import type { Project } from "../types/security";

export interface CreateProjectData {
  name: string;
  description?: string;
}

export async function getProjects(): Promise<Project[]> {
  const response = await apiClient.get<Project[]>("/projects");

  return response.data;
}

export async function getProject(
  projectId: string,
): Promise<Project> {
  const response = await apiClient.get<Project>(
    `/projects/${projectId}`,
  );

  return response.data;
}

export async function createProject(
  data: CreateProjectData,
): Promise<Project> {
  const response = await apiClient.post<Project>(
    "/projects",
    data,
  );

  return response.data;
}