import { apiClient } from "./client";
import type {
  Device,
  DeviceEnrollResponse,
} from "../types/security";

export interface EnrollDeviceData {
  name: string;
  platform?: string;
  operating_system?: string;
  device_type?: string;
}

export async function getDevices(): Promise<Device[]> {
  const response = await apiClient.get<Device[]>("/devices");
  return response.data;
}

export async function getDevice(deviceId: string): Promise<Device> {
  const response = await apiClient.get<Device>(`/devices/${deviceId}`);
  return response.data;
}

export async function enrollDevice(
  data: EnrollDeviceData,
): Promise<DeviceEnrollResponse> {
  const response = await apiClient.post<DeviceEnrollResponse>(
    "/devices/enroll",
    data,
  );
  return response.data;
}

export interface UpdateDeviceData {
  name?: string;
  platform?: string;
  operating_system?: string;
  device_type?: string;
  status?: string;
}

export async function updateDevice(
  deviceId: string,
  data: UpdateDeviceData,
): Promise<Device> {
  const response = await apiClient.patch<Device>(
    `/devices/${deviceId}`,
    data,
  );
  return response.data;
}

export async function revokeDevice(deviceId: string): Promise<Device> {
  const response = await apiClient.post<Device>(
    `/devices/${deviceId}/revoke`,
  );
  return response.data;
}

export async function activateDevice(deviceId: string): Promise<Device> {
  const response = await apiClient.post<Device>(
    `/devices/${deviceId}/activate`,
  );
  return response.data;
}
