import { apiClient } from "./client";
import type { Scan } from "../types/security";

export async function getAssetScans(
  assetId: string,
): Promise<Scan[]> {
  const response = await apiClient.get<Scan[]>(
    `/scans/${assetId}`,
  );

  return response.data;
}