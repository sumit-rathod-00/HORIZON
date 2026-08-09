import { apiClient } from "./client";
import type { Asset } from "../types/security";

export async function getProjectAssets(
  projectId: string,
): Promise<Asset[]> {
  const response = await apiClient.get<Asset[]>(
    `/assets/${projectId}`,
  );

  return response.data;
}