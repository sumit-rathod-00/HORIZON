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

export interface CreateScanData {
  scanner: string;
}

export async function createScan(
  assetId: string,
  data: CreateScanData,
): Promise<Scan> {
  const response = await apiClient.post<Scan>(
    `/scans/${assetId}`,
    data,
  );

  return response.data;
}

export async function updateScanStatus(
  scanId: string,
  status: string,
): Promise<Scan> {
  const response = await apiClient.patch<Scan>(
    `/scans/${scanId}`,
    undefined,
    {
      params: {
        status,
      },
    },
  );
  return response.data;
}

export async function deleteScan(
  scanId: string,
): Promise<void> {
  await apiClient.delete(`/scans/${scanId}`);
}