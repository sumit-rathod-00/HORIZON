export interface Project {
  id: string;
  owner_id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  project_id: string;
  name: string;
  asset_type: string;
  ip_address: string | null;
  created_at: string;
  updated_at: string;
}

export interface Scan {
  id: string;
  asset_id: string;
  scanner: string;
  status: string;
  started_at: string;
  completed_at: string | null;
}

export interface Vulnerability {
  id: string;
  asset_id: string;
  title: string;
  description: string | null;
  severity: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export type DeviceStatus =
  | "pending"
  | "active"
  | "inactive"
  | "revoked";

export interface Device {
  id: string;
  owner_id: string;
  name: string;
  platform: string | null;
  operating_system: string | null;
  device_type: string | null;
  status: DeviceStatus;
  last_seen: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeviceEnrollResponse {
  device: Device;
  enrollment_token: string;
  message: string;
}