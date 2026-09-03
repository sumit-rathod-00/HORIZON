import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface RiskSummary {
  total_devices: number;
  total_assets: number;
  total_vulnerabilities: number;
  critical_vulnerabilities: number;
  high_vulnerabilities: number;
  total_events: number;
  critical_events: number;
  active_devices: number;
  unhealthy_devices: number;
  average_risk_score: number;
  highest_risk_device: string | null;
  highest_risk_score: number;
}

export interface DeviceCorrelation {
  device_id: string;
  device_name: string | null;
  device_status: string | null;
  asset_id: string | null;
  asset_ip: string | null;
  asset_hostname: string | null;
  vulnerability_count: number;
  critical_vulnerabilities: number;
  high_vulnerabilities: number;
  open_events: number;
  critical_events: number;
  last_telemetry: string | null;
  firewall_enabled: boolean | null;
  antivirus_enabled: boolean | null;
  risk_score: number;
}

export interface PrioritizedFinding {
  id: string;
  type: "vulnerability" | "event";
  title: string;
  description: string;
  severity: string;
  risk_score: number;
  priority_score: number;
  device_id: string | null;
  device_name: string | null;
  asset_id: string | null;
  asset_ip: string | null;
  detected_at: string;
  cve_id?: string | null;
  cwe_id?: string | null;
  cvss_score?: number | null;
  category?: string | null;
  evidence?: string | null;
  remediation?: string | null;
  status?: string | null;
}

export interface SecurityRecommendation {
  id: string;
  title: string;
  description: string;
  priority: string;
  impact: string;
  effort: string;
  category: string;
  steps: string[];
  related_findings: string[];
  devices_affected: string[];
  estimated_risk_reduction: number;
}

const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    Authorization: `Bearer ${token}`,
  };
};

export const getRiskSummary = async (): Promise<RiskSummary> => {
  const response = await axios.get(`${API_URL}/api/v1/intelligence/risk-summary`, {
    headers: getAuthHeaders(),
  });
  return response.data;
};

export const getDeviceCorrelation = async (deviceId: string): Promise<DeviceCorrelation> => {
  const response = await axios.get(
    `${API_URL}/api/v1/intelligence/devices/${deviceId}/correlation`,
    {
      headers: getAuthHeaders(),
    }
  );
  return response.data;
};

export const getPrioritizedFindings = async (params?: {
  min_priority?: number;
  severity?: string[];
  limit?: number;
}): Promise<PrioritizedFinding[]> => {
  const queryParams = new URLSearchParams();
  if (params?.min_priority !== undefined) {
    queryParams.append("min_priority", params.min_priority.toString());
  }
  if (params?.severity) {
    params.severity.forEach((s) => queryParams.append("severity", s));
  }
  if (params?.limit) {
    queryParams.append("limit", params.limit.toString());
  }

  const response = await axios.get(
    `${API_URL}/api/v1/intelligence/prioritized-findings${queryParams.toString() ? `?${queryParams.toString()}` : ""}`,
    {
      headers: getAuthHeaders(),
    }
  );
  return response.data;
};

export const getRecommendations = async (): Promise<SecurityRecommendation[]> => {
  const response = await axios.get(`${API_URL}/api/v1/intelligence/recommendations`, {
    headers: getAuthHeaders(),
  });
  return response.data;
};
