import { getProjectAssets } from "./assets";
import { getProjects } from "./projects";
import { getAssetScans } from "./scans";
import { getAssetVulnerabilities } from "./vulnerabilities";

import type {
  Asset,
  Project,
  Scan,
  Vulnerability,
} from "../types/security";

export interface DashboardData {
  projects: Project[];
  assets: Asset[];
  scans: Scan[];
  vulnerabilities: Vulnerability[];
}

export async function getDashboardData(): Promise<DashboardData> {
  const projects = await getProjects();

  const assetResults = await Promise.all(
    projects.map((project) =>
      getProjectAssets(project.id),
    ),
  );

  const assets: Asset[] = assetResults.flat();

  const scanResults = await Promise.all(
    assets.map((asset) =>
      getAssetScans(asset.id),
    ),
  );

  const vulnerabilityResults = await Promise.all(
    assets.map((asset) =>
      getAssetVulnerabilities(asset.id),
    ),
  );

  const scans: Scan[] = scanResults.flat();

  const vulnerabilities: Vulnerability[] =
    vulnerabilityResults.flat();

  return {
    projects,
    assets,
    scans,
    vulnerabilities,
  };
}