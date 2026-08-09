import { apiClient } from "./client";
import type { Vulnerability } from "../types/security";

export async function getAssetVulnerabilities(
  assetId: string,
): Promise<Vulnerability[]> {
  const response = await apiClient.get<Vulnerability[]>(
    `/vulnerabilities/${assetId}`,
  );

  return response.data;
}