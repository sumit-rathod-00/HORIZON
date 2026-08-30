# HORIZON Codebase Review Notes

This document records the first foundation review of the HORIZON codebase.

## Confirmed foundation issues to address

- Security resource endpoints must enforce authenticated access and project/asset ownership consistently.
- Scan records currently represent scan metadata/status; they are not yet a real scanner execution pipeline.
- Vulnerability records currently represent findings, but need stronger lifecycle, provenance, risk scoring, and scan relationships before production use.
- Project and asset timestamps should use a consistent timezone-aware strategy.
- Configuration and CORS currently reflect development assumptions and need environment-driven production configuration.
- Development/test-only endpoints must not remain exposed in production.
- Multi-tenant organization isolation is not yet represented as a first-class domain boundary and must be implemented before onboarding multiple businesses.

## Review principle

Do not claim a feature is production-ready merely because CRUD endpoints or database models exist. HORIZON should distinguish inventory management from actual security monitoring, detection, analysis, remediation, and verification.

This review is intentionally recorded before larger feature development so future implementation work can be checked against the real product requirements.
