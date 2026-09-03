import { apiClient } from "./client";

export interface DeviceTelemetry {
  id: string;
  collected_at: string;
  cpu_usage_percent: number | null;
  memory_usage_percent: number | null;
  disk_usage_percent: number | null;
  firewall_enabled: boolean | null;
  antivirus_enabled: boolean | null;
  os_updates_pending: number | null;
}

export interface TelemetryQueryParams {
  limit?: number;
  offset?: number;
}

export async function getDeviceTelemetry(
  deviceId: string,
  params?: TelemetryQueryParams
): Promise<DeviceTelemetry[]> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", params.limit.toString());
  if (params?.offset) searchParams.set("offset", params.offset.toString());

  const url = `/devices/${deviceId}/telemetry${searchParams.toString() ? '?' + searchParams : ''}`;
  const response = await apiClient.get<DeviceTelemetry[]>(url);
  return response.data;
}

export interface SecurityEvent {
  id: string;
  event_type: string;
  severity: "info" | "low" | "medium" | "high" | "critical";
  title: string;
  description: string | null;
  status: "open" | "acknowledged" | "resolved" | "false_positive";
  detected_at: string;
  evidence: Record<string, unknown> | null;
}

export interface EventQueryParams {
  limit?: number;
  offset?: number;
  status?: string;
  severity?: string;
}

export async function getDeviceEvents(
  deviceId: string,
  params?: EventQueryParams
): Promise<SecurityEvent[]> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", params.limit.toString());
  if (params?.offset) searchParams.set("offset", params.offset.toString());
  if (params?.status) searchParams.set("status", params.status);
  if (params?.severity) searchParams.set("severity", params.severity);

  const url = `/devices/${deviceId}/events${searchParams.toString() ? '?' + searchParams : ''}`;
  const response = await apiClient.get<SecurityEvent[]>(url);
  return response.data;
}