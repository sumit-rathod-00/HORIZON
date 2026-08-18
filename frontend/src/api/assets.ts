import { apiClient } from "./client";
import type { Asset } from "../types/security";

export interface CreateAssetData {
  name: string;
  asset_type: string;
  ip_address?: string;
}

export async function getProjectAssets(
  projectId: string,
): Promise<Asset[]> {
  const response = await apiClient.get<Asset[]>(
    `/assets/${projectId}`,
  );

  return response.data;
}

export async function createAsset(
  projectId: string,
  data: CreateAssetData,
): Promise<Asset> {
  const response = await apiClient.post<Asset>(
    `/assets/${projectId}`,
    data,
  );

  return response.data;
}

export async function deleteAsset(
  assetId: string,
): Promise<void> {
  await apiClient.delete(`/assets/${assetId}`);
}

export interface UpdateAssetData {
  name?: string;
  asset_type?: string;
  ip_address?: string;
}

export async function updateAsset(
  assetId: string,
  data: UpdateAssetData,
): Promise<Asset> {
  const response = await apiClient.put<Asset>(
    `/assets/${assetId}`,
    data,
  );

  return response.data;
}