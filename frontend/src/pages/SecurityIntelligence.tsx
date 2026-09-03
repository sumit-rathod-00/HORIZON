import { useEffect, useState } from "react";
import {
  Shield,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Target,
  Lightbulb,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

import {
  getRiskSummary,
  getPrioritizedFindings,
  getRecommendations,
  type RiskSummary,
  type PrioritizedFinding,
  type SecurityRecommendation,
} from "../api/intelligence";

const SEVERITY_STYLES: Record<string, string> = {
  critical: "bg-red-600/20 text-red-300 border-red-600/30",
  high: "bg-red-500/10 text-red-400 border-red-500/20",
  medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  low: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
  info: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

const PRIORITY_STYLES: Record<string, string> = {
  critical: "bg-red-600/20 text-red-300",
  high: "bg-red-500/10 text-red-400",
  medium: "bg-amber-500/10 text-amber-400",
  low: "bg-zinc-500/10 text-zinc-400",
};

function RiskScoreBadge({ score }: { score: number }) {
  let color = "text-emerald-400";
  if (score >= 7) color = "text-red-400";
  else if (score >= 4) color = "text-amber-400";

  return (
    <div className="flex items-baseline gap-1">
      <span className={`text-3xl font-bold ${color}`}>{score.toFixed(1)}</span>
      <span className="text-sm text-zinc-500">/10</span>
    </div>
  );
}

function FindingCard({ finding }: { finding: PrioritizedFinding }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span
              className={`rounded-full border px-2 py-0.5 text-xs font-medium ${
                SEVERITY_STYLES[finding.severity.toLowerCase()]
              }`}
            >
              {finding.severity}
            </span>
            {finding.cve_id && (
              <span className="rounded border border-purple-500/20 bg-purple-500/10 px-2 py-0.5 text-xs text-purple-400">
                {finding.cve_id}
              </span>
            )}
            {finding.cvss_score && (
              <span className="text-xs text-zinc-500">
                CVSS: {finding.cvss_score.toFixed(1)}
              </span>
            )}
          </div>

          <h4 className="mt-2 text-sm font-medium text-white">{finding.title}</h4>

          <div className="mt-2 flex items-center gap-4 text-xs text-zinc-500">
            <span>{finding.device_name || "Unknown Device"}</span>
            {finding.asset_ip && <span>{finding.asset_ip}</span>}
            <span className="rounded bg-zinc-800 px-2 py-0.5">
              Priority: {finding.priority_score.toFixed(0)}
            </span>
          </div>

          {expanded && (
            <div className="mt-4 space-y-3 border-t border-white/[0.08] pt-3">
              <p className="text-sm text-zinc-400">{finding.description}</p>

              {finding.category && (
                <div>
                  <span className="text-xs font-medium text-zinc-500">Category:</span>
                  <span className="ml-2 text-xs text-zinc-400">{finding.category}</span>
                </div>
              )}

              {finding.cwe_id && (
                <div>
                  <span className="text-xs font-medium text-zinc-500">Weakness:</span>
                  <span className="ml-2 text-xs text-zinc-400">{finding.cwe_id}</span>
                </div>
              )}

              {finding.remediation && (
                <div>
                  <span className="text-xs font-medium text-zinc-500">Remediation:</span>
                  <p className="mt-1 whitespace-pre-line text-xs text-zinc-400">
                    {finding.remediation}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="ml-4 rounded p-1 hover:bg-white/[0.05]"
        >
          {expanded ? (
            <ChevronUp size={16} className="text-zinc-400" />
          ) : (
            <ChevronDown size={16} className="text-zinc-400" />
          )}
        </button>
      </div>
    </div>
  );
}

function RecommendationCard({ recommendation }: { recommendation: SecurityRecommendation }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-400/20 bg-cyan-400/5">
            <Lightbulb size={16} className="text-cyan-400" />
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  PRIORITY_STYLES[recommendation.priority]
                }`}
              >
                {recommendation.priority}
              </span>
              <span className="text-xs text-zinc-500">
                Effort: {recommendation.effort}
              </span>
              <span className="text-xs text-emerald-400">
                -{recommendation.estimated_risk_reduction.toFixed(1)} risk
              </span>
            </div>

            <h4 className="mt-2 text-sm font-medium text-white">
              {recommendation.title}
            </h4>
            <p className="mt-1 text-xs text-zinc-400">{recommendation.description}</p>

            {expanded && (
              <div className="mt-4 space-y-3 border-t border-white/[0.08] pt-3">
                <div>
                  <span className="text-xs font-medium text-zinc-500">Impact:</span>
                  <p className="mt-1 text-xs text-zinc-400">{recommendation.impact}</p>
                </div>

                <div>
                  <span className="text-xs font-medium text-zinc-500">Steps:</span>
                  <ol className="mt-1 space-y-1 pl-4">
                    {recommendation.steps.map((step, idx) => (
                      <li key={idx} className="text-xs text-zinc-400 list-decimal">
                        {step}
                      </li>
                    ))}
                  </ol>
                </div>

                {recommendation.devices_affected.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-zinc-500">
                      Devices Affected ({recommendation.devices_affected.length}):
                    </span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {recommendation.devices_affected.slice(0, 5).map((device, idx) => (
                        <span
                          key={idx}
                          className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400"
                        >
                          {device}
                        </span>
                      ))}
                      {recommendation.devices_affected.length > 5 && (
                        <span className="text-xs text-zinc-500">
                          +{recommendation.devices_affected.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="ml-4 rounded p-1 hover:bg-white/[0.05]"
        >
          {expanded ? (
            <ChevronUp size={16} className="text-zinc-400" />
          ) : (
            <ChevronDown size={16} className="text-zinc-400" />
          )}
        </button>
      </div>
    </div>
  );
}

export function SecurityIntelligence() {
  const [riskSummary, setRiskSummary] = useState<RiskSummary | null>(null);
  const [findings, setFindings] = useState<PrioritizedFinding[]>([]);
  const [recommendations, setRecommendations] = useState<SecurityRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadIntelligence();
  }, []);

  async function loadIntelligence() {
    try {
      setLoading(true);
      const [summary, prioritizedFindings, recs] = await Promise.all([
        getRiskSummary(),
        getPrioritizedFindings({ limit: 20 }),
        getRecommendations(),
      ]);

      setRiskSummary(summary);
      setFindings(prioritizedFindings);
      setRecommendations(recs);
    } catch (err) {
      console.error("Failed to load security intelligence:", err);
      setError("Unable to load security intelligence");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <Shield size={48} className="mx-auto mb-4 text-cyan-400 animate-pulse" />
            <p className="text-sm text-zinc-500">Loading security intelligence...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-2 flex items-center gap-2 text-cyan-400">
          <Shield size={18} />
          <span className="text-xs font-medium uppercase tracking-[0.18em]">
            Security Intelligence
          </span>
        </div>

        <h1 className="text-2xl font-semibold text-white">Risk Intelligence & Analysis</h1>
        <p className="mt-2 text-sm text-zinc-500">
          Prioritized findings, contextual risk assessment, and actionable recommendations.
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Risk Summary */}
      {riskSummary && (
        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <div className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4">
            <div className="flex items-center gap-2 text-zinc-400">
              <TrendingUp size={16} />
              <span className="text-sm">Average Risk</span>
            </div>
            <RiskScoreBadge score={riskSummary.average_risk_score} />
          </div>

          <div className="rounded-xl border border-red-500/10 bg-red-500/5 p-4">
            <div className="flex items-center gap-2 text-red-400">
              <AlertTriangle size={16} />
              <span className="text-sm">Critical Issues</span>
            </div>
            <p className="mt-2 text-3xl font-bold text-red-400">
              {riskSummary.critical_vulnerabilities + riskSummary.critical_events}
            </p>
          </div>

          <div className="rounded-xl border border-amber-500/10 bg-amber-500/5 p-4">
            <div className="flex items-center gap-2 text-amber-400">
              <Target size={16} />
              <span className="text-sm">High Priority</span>
            </div>
            <p className="mt-2 text-3xl font-bold text-amber-400">
              {riskSummary.high_vulnerabilities}
            </p>
          </div>

          <div className="rounded-xl border border-emerald-500/10 bg-emerald-500/5 p-4">
            <div className="flex items-center gap-2 text-emerald-400">
              <CheckCircle2 size={16} />
              <span className="text-sm">Active Devices</span>
            </div>
            <p className="mt-2 text-3xl font-bold text-emerald-400">
              {riskSummary.active_devices}
            </p>
          </div>
        </div>
      )}

      {/* Highest Risk Device */}
      {riskSummary?.highest_risk_device && (
        <div className="mb-8 rounded-xl border border-red-500/20 bg-red-500/5 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-red-300">Highest Risk Device</p>
              <p className="mt-1 text-lg text-white">{riskSummary.highest_risk_device}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-zinc-400">Risk Score</p>
              <p className="text-2xl font-bold text-red-400">
                {riskSummary.highest_risk_score.toFixed(1)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Prioritized Findings */}
        <div className="lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Prioritized Findings</h2>
            <span className="text-sm text-zinc-500">{findings.length} findings</span>
          </div>

          {findings.length === 0 ? (
            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-12 text-center">
              <CheckCircle2 size={32} className="mx-auto mb-4 text-emerald-500" />
              <h3 className="text-lg font-medium text-white">No critical findings</h3>
              <p className="mt-2 text-sm text-zinc-500">
                Your security posture looks good right now.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {findings.map((finding) => (
                <FindingCard key={finding.id} finding={finding} />
              ))}
            </div>
          )}
        </div>

        {/* Recommendations */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Recommendations</h2>
            <span className="text-sm text-zinc-500">{recommendations.length} actions</span>
          </div>

          {recommendations.length === 0 ? (
            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-8 text-center">
              <CheckCircle2 size={32} className="mx-auto mb-3 text-emerald-500" />
              <p className="text-sm text-zinc-400">No recommendations</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recommendations.map((rec) => (
                <RecommendationCard key={rec.id} recommendation={rec} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
