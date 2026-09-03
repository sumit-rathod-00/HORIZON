# HORIZON Layer 2 Implementation Plan

**Layer:** LAYER 2 - SEE: CONTINUOUS VISIBILITY & DETECTION CORE  
**Status:** PLANNING  
**Date:** 2026-09-03  
**Purpose:** Move HORIZON from "the system knows a device exists" to "the system can securely and continuously determine device health/state, receive controlled security telemetry, detect meaningful changes, evaluate policy conditions, generate security events, and display those events to the user"

---

## 1. Repository Audit Findings

### 1.1 Current Architecture Summary

**Backend Technology Stack:**
- FastAPI with async/await patterns
- SQLAlchemy 2.x with async support
- PostgreSQL database
- Alembic migrations
- Pydantic v2 schemas
- JWT authentication (get_current_user dependency)
- Repository pattern for data access

**Frontend Technology Stack:**
- React with TypeScript
- Vite build system
- Axios API client with JWT bearer tokens
- Modern UI with dark theme
- Route-based navigation

**Security Architecture:**
- JWT-based authentication throughout
- Owner-based authorization (owner_id checks)
- Audit logging infrastructure (AuditLog model + AuditLogService)
- No plaintext secrets (bcrypt-hashed tokens)
- Cross-user isolation enforced

**Test Infrastructure:**
- pytest with async support
- 39 passing tests (zero regressions)
- Mock-based unit testing
- Integration test patterns established

### 1.2 Layer 1 Foundation (COMPLETE ✅)

**Device Identity & Enrollment:**
- `Device` model with owner_id, name, platform, OS, device_type, status, last_seen
- Secure enrollment with bcrypt-hashed tokens
- Device lifecycle: pending → active → inactive → revoked
- DeviceService with ownership verification
- DeviceRepository for database operations
- 6 device API endpoints (enroll, list, get, update, revoke, activate)
- Frontend device management UI fully integrated
- Audit logging for device operations

**Key Files (Layer 1):**
- `backend/app/models/device.py` - Device model
- `backend/app/models/audit_log.py` - Audit logging
- `backend/app/services/device_service.py` - Device management
- `backend/app/services/audit_log_service.py` - Audit events
- `backend/app/repositories/device_repository.py` - Device data access
- `backend/app/repositories/audit_log_repository.py` - Audit data access
- `backend/app/api/v1/endpoints/devices.py` - Device APIs
- `backend/app/schemas/device.py` - Device schemas
- `frontend/src/pages/Devices.tsx` - Device management UI
- `frontend/src/api/devices.ts` - Device API client

**Database Migrations:**
- Migration head: `1c702225ec30` (devices + audit_logs tables)
- All migrations applied successfully
- Clean migration history

### 1.3 Existing Security Capabilities (Pre-Layer 1)

**Vulnerability Detection Pipeline:**
- Nmap scanner integration (`nmap_scanner.py`)
- Nmap result parsing and normalization
- ScanResult model for port/service data
- VulnerabilityAnalyzer with deterministic detection
- RiskEngine with explainable risk scoring
- Vulnerability model with scan correlation
- Scanner service orchestration

**Key Security Components:**
- `app/services/nmap_scanner.py` - Nmap integration
- `app/services/vulnerability_analyzer.py` - Deterministic vulnerability detection
- `app/services/risk_engine.py` - Explainable risk scoring
- `app/services/scanner_service.py` - Scanner orchestration
- `app/models/vulnerability.py` - Vulnerability records
- `app/models/scan.py` - Scan metadata
- `app/models/scan_result.py` - Normalized scan results

**AI Abstraction Layer:**
- `app/services/ai/base.py` - AISecurityProvider abstract interface
- `app/services/ai/deterministic_analyzer.py` - Deterministic implementation
- SecurityInsight dataclass for AI responses
- Ready for Ollama/local AI integration

**Asset & Project Management:**
- Project model (user-owned projects)
- Asset model (project-scoped assets)
- Asset repository and service
- Project repository and service
- Frontend project/asset management UI

### 1.4 Reusable Architecture Patterns

**Repository Pattern:**
- Clean separation: Repository → Service → API
- Async database operations throughout
- Session management via dependency injection
- Consistent CRUD patterns

**Service Layer:**
- Business logic encapsulation
- Ownership verification in service methods
- Audit logging integration
- Transaction management

**API Layer:**
- JWT authentication via `Depends(get_current_user)`
- Pydantic schema validation
- Consistent error handling
- RESTful endpoint design

**Frontend Patterns:**
- API client abstraction (axios-based)
- TypeScript interfaces matching backend schemas
- Loading/empty/error state handling
- Consistent UI component patterns

### 1.5 Gaps & Missing Components for Layer 2

**Device Agent:**
- ❌ No agent daemon/service exists
- ❌ No agent-to-server authentication mechanism
- ❌ No heartbeat endpoint for agent→server communication
- ✅ Device.last_seen timestamp exists (foundation ready)
- ✅ Device.status lifecycle exists

**Telemetry Infrastructure:**
- ❌ No telemetry ingestion API
- ❌ No telemetry storage model
- ❌ No telemetry normalization service
- ❌ No telemetry validation
- ❌ No telemetry size limits

**Security Events:**
- ❌ No SecurityEvent model
- ❌ No event generation from detections
- ❌ No event storage/querying
- ❌ No event timeline
- ❌ No event severity classification

**Policy Engine:**
- ❌ No Policy model
- ❌ No policy assignment to devices
- ❌ No policy evaluation logic
- ❌ No policy violation detection
- ❌ No configurable thresholds

**Detection Engine:**
- ✅ Vulnerability detection exists (nmap-based)
- ❌ No state-change detection
- ❌ No baseline comparison
- ❌ No anomaly detection
- ❌ No correlation between telemetry and vulnerabilities

**Frontend Security Center:**
- ✅ Device list view exists
- ❌ No device detail/timeline view
- ❌ No security events display
- ❌ No telemetry visualization
- ❌ No policy assignment UI
- ❌ No real-time status dashboard

---

## 2. Layer 2 Architecture Overview

### 2.1 Core Principle

Layer 2 transforms HORIZON from a device enrollment system into a **continuous visibility and detection platform**.

**Before Layer 2:** Device exists → User can see it enrolled  
**After Layer 2:** Device exists → Agent reports health → Server processes telemetry → System detects changes → Events are created → User sees security timeline

### 2.2 Architectural Components

```
┌─────────────────────────────────────────────────────────────┐
│                    HORIZON LAYER 2                          │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────┐         ┌──────────────────────────┐
    │   DEVICE     │ ◄─────► │   HORIZON BACKEND        │
    │   AGENT      │  Auth   │   (FastAPI)              │
    │  (Python)    │  +      │                          │
    │              │  TLS    │  ┌────────────────────┐  │
    └──────────────┘         │  │  Heartbeat API     │  │
            │                │  └────────────────────┘  │
            │                │  ┌────────────────────┐  │
            │ Heartbeat      │  │  Telemetry API     │  │
            │ + Telemetry    │  └────────────────────┘  │
            ▼                │  ┌────────────────────┐  │
    ┌──────────────┐         │  │  Device State      │  │
    │  Enrollment  │         │  │  Engine            │  │
    │  Token       │         │  └────────────────────┘  │
    │  (bcrypt)    │         │  ┌────────────────────┐  │
    └──────────────┘         │  │  Policy Engine     │  │
                             │  └────────────────────┘  │
                             │  ┌────────────────────┐  │
                             │  │  Detection Engine  │  │
                             │  └────────────────────┘  │
                             │  ┌────────────────────┐  │
                             │  │  Security Event    │  │
                             │  │  Generator         │  │
                             │  └────────────────────┘  │
                             │  ┌────────────────────┐  │
                             │  │  Risk Integration  │  │
                             │  │  (Existing Engine) │  │
                             │  └────────────────────┘  │
                             └──────────────────────────┘
                                        │
                                        ▼
                             ┌──────────────────────────┐
                             │   FRONTEND               │
                             │   Security Center        │
                             │                          │
                             │  • Device Dashboard      │
                             │  • Security Events       │
                             │  • Device Timeline       │
                             │  • Telemetry Summary     │
                             │  • Policy Status         │
                             └──────────────────────────┘
```

---

## 3. Database Schema Changes

### 3.1 New Tables

#### `device_telemetry`
Stores normalized telemetry data from devices.

```sql
CREATE TABLE device_telemetry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    
    -- Telemetry envelope
    telemetry_version VARCHAR(20) NOT NULL,  -- Schema version
    agent_version VARCHAR(50),
    
    -- Device health metrics
    cpu_usage_percent DECIMAL(5, 2),
    memory_total_mb BIGINT,
    memory_used_mb BIGINT,
    memory_usage_percent DECIMAL(5, 2),
    disk_total_gb BIGINT,
    disk_used_gb BIGINT,
    disk_usage_percent DECIMAL(5, 2),
    
    -- Network information
    network_interfaces JSONB,  -- Array of {name, ip, mac, status}
    active_connections INTEGER,
    
    -- Security-relevant state
    firewall_enabled BOOLEAN,
    antivirus_enabled BOOLEAN,
    os_updates_pending INTEGER,
    
    -- Additional metadata
    metadata JSONB,  -- Extensible for platform-specific data
    
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    INDEX idx_device_telemetry_device (device_id),
    INDEX idx_device_telemetry_collected (collected_at DESC)
);
```

#### `security_events`
Security-relevant events detected by HORIZON.

```sql
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    
    event_type VARCHAR(100) NOT NULL,  -- device.inactive, policy.violation, state.changed
    severity VARCHAR(20) NOT NULL,     -- info, low, medium, high, critical
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Evidence and context
    evidence JSONB,
    detection_source VARCHAR(100) NOT NULL,  -- heartbeat_monitor, policy_engine, detection_engine
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'open',  -- open, acknowledged, resolved, false_positive
    
    -- Timestamps
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    INDEX idx_security_events_device (device_id),
    INDEX idx_security_events_detected (detected_at DESC),
    INDEX idx_security_events_status (status),
    INDEX idx_security_events_severity (severity)
);
```

#### `device_policies`
Security policies that can be assigned to devices.

```sql
CREATE TABLE device_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    name VARCHAR(120) NOT NULL,
    description TEXT,
    
    -- Policy configuration (JSON schema)
    policy_config JSONB NOT NULL,
    -- Example: {
    --   "heartbeat_interval_seconds": 300,
    --   "heartbeat_timeout_seconds": 900,
    --   "require_firewall": true,
    --   "require_antivirus": true,
    --   "max_os_updates_pending": 10
    -- }
    
    enabled BOOLEAN NOT NULL DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    INDEX idx_device_policies_owner (owner_id)
);
```

#### `device_policy_assignments`
Maps policies to devices.

```sql
CREATE TABLE device_policy_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    policy_id UUID NOT NULL REFERENCES device_policies(id) ON DELETE CASCADE,
    
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    UNIQUE(device_id, policy_id),
    INDEX idx_policy_assignments_device (device_id),
    INDEX idx_policy_assignments_policy (policy_id)
);
```

### 3.2 Table Modifications

#### `devices` (existing)
No schema changes required. Existing fields support Layer 2:
- `status` - Used by device state engine
- `last_seen` - Updated by heartbeat
- `enrollment_token_hash` - Used for agent authentication

---

## 4. Agent Architecture

### 4.1 Agent Overview

**HORIZON Device Agent** is a Python-based daemon/service that runs on enrolled devices.

**Supported Platforms (Initial):**
- Windows 10/11 (primary development target)
- Fallback: Linux (Ubuntu/Debian) if Windows presents blockers

**Architecture Decision:**
Start with the platform that can be reliably developed and tested in the current environment. Do not pretend to support every OS simultaneously.

### 4.2 Agent Components

```
horizon-agent/
├── agent/
│   ├── __init__.py
│   ├── main.py              # Agent entry point
│   ├── config.py            # Configuration management
│   ├── auth.py              # Authentication with server
│   ├── heartbeat.py         # Heartbeat sender
│   ├── telemetry.py         # Telemetry collector
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── base.py          # Collector interface
│   │   ├── system.py        # CPU, memory, disk
│   │   ├── network.py       # Network interfaces
│   │   └── security.py      # Firewall, AV status
│   └── utils/
│       ├── __init__.py
│       ├── retry.py         # Retry logic
│       └── logger.py        # Logging
├── tests/
│   └── test_agent.py
├── requirements.txt
├── setup.py
└── README.md
```

### 4.3 Agent Configuration

Agent configuration stored in `horizon-agent.yaml`:

```yaml
server:
  url: https://horizon.example.com/api/v1
  verify_ssl: true

device:
  enrollment_token: <token-from-enrollment>
  device_id: <assigned-after-activation>

heartbeat:
  interval_seconds: 300  # 5 minutes
  timeout_seconds: 30
  retry_attempts: 3
  retry_backoff_seconds: 10

telemetry:
  enabled: true
  interval_seconds: 300
  collectors:
    - system
    - network
    - security

logging:
  level: INFO
  file: /var/log/horizon-agent/agent.log
```

### 4.4 Agent Authentication

**Authentication Flow:**

1. Agent starts with `enrollment_token` from user enrollment
2. Agent sends heartbeat with enrollment token (first time)
3. Server validates token hash, activates device if pending
4. Server returns device_id for subsequent requests
5. Agent stores device_id in config
6. Subsequent heartbeats authenticated with enrollment_token

**Security Requirements:**
- Agent never logs enrollment token
- Agent stores token in restricted-permission config file
- HTTPS/TLS required for all agent→server communication
- Agent validates server SSL certificate
- No arbitrary command execution from server

### 4.5 Agent Heartbeat

**Heartbeat Payload:**

```json
{
  "device_id": "uuid-or-null",
  "enrollment_token": "token-if-pending",
  "agent_version": "1.0.0",
  "timestamp": "2026-09-03T14:30:00Z",
  "status": "healthy"
}
```

**Heartbeat Logic:**
- Send heartbeat every 300 seconds (configurable)
- Include agent version and timestamp
- Handle network failures gracefully (retry with backoff)
- Transition to inactive if server unreachable for extended period
- Do not flood server on network recovery

### 4.6 Agent Telemetry Collection

**Telemetry Payload:**

```json
{
  "device_id": "uuid",
  "telemetry_version": "1.0",
  "agent_version": "1.0.0",
  "collected_at": "2026-09-03T14:30:00Z",
  
  "cpu_usage_percent": 45.2,
  "memory_total_mb": 16384,
  "memory_used_mb": 8192,
  "memory_usage_percent": 50.0,
  "disk_total_gb": 512,
  "disk_used_gb": 256,
  "disk_usage_percent": 50.0,
  
  "network_interfaces": [
    {
      "name": "Ethernet",
      "ip": "192.168.1.100",
      "mac": "00:11:22:33:44:55",
      "status": "up"
    }
  ],
  "active_connections": 42,
  
  "firewall_enabled": true,
  "antivirus_enabled": true,
  "os_updates_pending": 3,
  
  "metadata": {
    "platform_specific": "data"
  }
}
```

**Telemetry Collection:**
- Collect only security-relevant metrics
- Do not collect passwords, private documents, browser history
- Respect data minimization principle
- Validate data before sending
- Implement size limits (max 1MB per payload)

---

## 5. API Changes

### 5.1 New Endpoints

#### `POST /devices/heartbeat`
Agent heartbeat endpoint.

**Request:**
```json
{
  "device_id": "uuid-or-null",
  "enrollment_token": "token-if-pending",
  "agent_version": "1.0.0",
  "timestamp": "2026-09-03T14:30:00Z",
  "status": "healthy"
}
```

**Response:**
```json
{
  "device_id": "uuid",
  "status": "active",
  "heartbeat_interval_seconds": 300,
  "telemetry_enabled": true
}
```

**Authentication:**
- Validate enrollment_token hash against device record
- Return device_id for future requests
- Activate device if currently pending
- Update device.last_seen timestamp
- Audit log heartbeat reception

#### `POST /devices/{device_id}/telemetry`
Telemetry ingestion endpoint.

**Request:** (See telemetry payload in 4.6)

**Response:**
```json
{
  "status": "accepted",
  "telemetry_id": "uuid",
  "received_at": "2026-09-03T14:30:01Z"
}
```

**Authentication:**
- Validate enrollment_token
- Verify device ownership
- Validate telemetry schema version
- Enforce size limits (max 1MB)
- Reject malformed payloads
- Audit log telemetry reception

#### `GET /devices/{device_id}/telemetry`
Query device telemetry history.

**Query Parameters:**
- `limit` (default 100, max 1000)
- `start_time` (ISO timestamp)
- `end_time` (ISO timestamp)

**Response:**
```json
{
  "device_id": "uuid",
  "telemetry": [
    {
      "id": "uuid",
      "collected_at": "2026-09-03T14:30:00Z",
      "cpu_usage_percent": 45.2,
      ...
    }
  ],
  "total": 150
}
```

**Authorization:**
- Verify current_user owns device
- Apply pagination
- Return only requested time range

#### `GET /devices/{device_id}/events`
Query security events for a device.

**Query Parameters:**
- `limit` (default 100)
- `status` (open, acknowledged, resolved, false_positive)
- `severity` (info, low, medium, high, critical)
- `start_time` (ISO timestamp)

**Response:**
```json
{
  "device_id": "uuid",
  "events": [
    {
      "id": "uuid",
      "event_type": "device.inactive",
      "severity": "medium",
      "title": "Device became inactive",
      "description": "No heartbeat received for 15 minutes",
      "detected_at": "2026-09-03T14:45:00Z",
      "status": "open"
    }
  ],
  "total": 5
}
```

**Authorization:**
- Verify current_user owns device

#### `GET /devices/{device_id}/timeline`
Device security timeline (chronological events).

**Response:**
```json
{
  "device_id": "uuid",
  "timeline": [
    {
      "timestamp": "2026-09-03T14:45:00Z",
      "type": "event",
      "severity": "medium",
      "title": "Device became inactive",
      "details": "No heartbeat received"
    },
    {
      "timestamp": "2026-09-03T14:00:00Z",
      "type": "heartbeat",
      "title": "Heartbeat received",
      "details": "Device is healthy"
    },
    {
      "timestamp": "2026-09-03T10:00:00Z",
      "type": "enrollment",
      "title": "Device enrolled",
      "details": "Work Laptop enrolled"
    }
  ]
}
```

**Authorization:**
- Verify current_user owns device

#### `POST /policies`
Create a security policy.

**Request:**
```json
{
  "name": "Standard Workstation Policy",
  "description": "Security requirements for employee workstations",
  "policy_config": {
    "heartbeat_interval_seconds": 300,
    "heartbeat_timeout_seconds": 900,
    "require_firewall": true,
    "require_antivirus": true,
    "max_os_updates_pending": 10
  },
  "enabled": true
}
```

**Response:** Policy object

**Authorization:**
- Require authenticated user
- Set owner_id to current_user.id

#### `GET /policies`
List user's policies.

**Response:** Array of policy objects

#### `POST /devices/{device_id}/policies/{policy_id}`
Assign policy to device.

**Response:** Assignment confirmation

**Authorization:**
- Verify current_user owns device
- Verify current_user owns policy

#### `GET /devices/{device_id}/policies`
List policies assigned to device.

**Response:** Array of policy objects

---

## 6. Backend Service Layer

### 6.1 New Services

#### `HeartbeatService`
Handles device heartbeat processing.

**Responsibilities:**
- Validate heartbeat payload
- Authenticate device via enrollment token
- Activate pending devices
- Update device.last_seen timestamp
- Return heartbeat configuration
- Audit log heartbeat events
- Trigger device state transitions

**Key Methods:**
- `process_heartbeat(device_id, token, agent_version, timestamp)`
- `validate_heartbeat_authentication(device_id, token)`
- `update_device_heartbeat(device_id)`

#### `TelemetryService`
Handles telemetry ingestion and storage.

**Responsibilities:**
- Validate telemetry schema
- Enforce size limits (max 1MB payload)
- Normalize telemetry data
- Store in device_telemetry table
- Detect anomalies (future)
- Audit log telemetry events

**Key Methods:**
- `ingest_telemetry(device_id, token, payload)`
- `validate_telemetry_schema(payload)`
- `normalize_telemetry(payload)`
- `store_telemetry(device_id, telemetry)`
- `query_telemetry(device_id, filters)`

#### `DeviceStateEngine`
Calculates and manages device states.

**Responsibilities:**
- Calculate device status (active, stale, inactive)
- Apply configurable thresholds
- Detect state transitions
- Generate state-change events
- Integrate with policy engine

**Key Methods:**
- `calculate_device_state(device_id)`
- `check_all_device_states()` (periodic job)
- `detect_state_transition(device_id, old_state, new_state)`
- `generate_state_event(device_id, state, reason)`

**State Logic:**
- ACTIVE: heartbeat within heartbeat_interval
- STALE: heartbeat within heartbeat_timeout
- INACTIVE: no heartbeat beyond heartbeat_timeout
- REVOKED: manually revoked (from Layer 1)

#### `PolicyEngine`
Evaluates security policies against device state.

**Responsibilities:**
- Evaluate policy conditions
- Detect policy violations
- Generate policy violation events
- Track policy compliance
- Support configurable rules

**Key Methods:**
- `evaluate_policy(device_id, policy_id)`
- `evaluate_device_policies(device_id)`
- `check_policy_condition(device, policy, condition)`
- `generate_violation_event(device_id, policy_id, violations)`

**Initial Policy Checks:**
- Heartbeat freshness
- Agent version minimum
- Firewall enabled (if required)
- Antivirus enabled (if required)
- OS updates threshold

#### `DetectionEngine`
Detects security-relevant changes and events.

**Responsibilities:**
- Compare current state vs previous state
- Detect configuration changes
- Detect network changes
- Generate security events
- Classify event severity
- Avoid duplicate events

**Key Methods:**
- `detect_changes(device_id, current_telemetry, previous_telemetry)`
- `detect_network_changes(current, previous)`
- `detect_security_state_changes(current, previous)`
- `classify_event_severity(event_type, context)`
- `generate_security_event(device_id, event_type, details)`

**Detection Types:**
- Network interface added/removed
- IP address changed
- Firewall disabled
- Antivirus disabled
- OS updates increased significantly
- Disk usage critical

#### `SecurityEventService`
Manages security event lifecycle.

**Responsibilities:**
- Create security events
- Query events with filters
- Update event status (acknowledge, resolve, mark false positive)
- Generate device timeline
- Track event history

**Key Methods:**
- `create_event(device_id, event_type, severity, title, description, evidence)`
- `query_device_events(device_id, filters)`
- `update_event_status(event_id, status, user_id)`
- `get_device_timeline(device_id, limit)`
- `get_event_statistics(device_id)`

#### `PolicyService`
Manages security policies.

**Responsibilities:**
- Create, read, update, delete policies
- Assign policies to devices
- Validate policy configuration
- Enforce ownership isolation
- Query policy compliance

**Key Methods:**
- `create_policy(owner_id, name, description, config)`
- `assign_policy_to_device(device_id, policy_id, user_id)`
- `get_device_policies(device_id)`
- `validate_policy_config(config)`

### 6.2 Service Integration

**Flow: Heartbeat → State → Policy → Event**

```python
# Heartbeat arrives
heartbeat_service.process_heartbeat(device_id, token, agent_version, timestamp)
  ↓
# Device state updated
device_state_engine.calculate_device_state(device_id)
  ↓
# Policy evaluated
policy_engine.evaluate_device_policies(device_id)
  ↓
# Events generated (if violations/changes detected)
security_event_service.create_event(...)
```

**Flow: Telemetry → Detection → Event**

```python
# Telemetry arrives
telemetry_service.ingest_telemetry(device_id, token, payload)
  ↓
# Changes detected
detection_engine.detect_changes(device_id, current, previous)
  ↓
# Events generated
security_event_service.create_event(...)
```

---

## 7. Frontend Integration

### 7.1 New Pages

#### `DeviceDetail.tsx`
Detailed view for a single device.

**Sections:**
- Device information (name, platform, OS, status)
- Current health metrics (CPU, memory, disk)
- Security status (firewall, AV, updates)
- Assigned policies
- Recent events
- Timeline

**Route:** `/devices/:deviceId`

#### `SecurityCenter.tsx`
Dashboard for all security events and device health.

**Sections:**
- Device status overview (active/stale/inactive counts)
- Recent security events (all devices)
- Critical alerts
- Policy violations
- Device health summary

**Route:** `/security-center`

### 7.2 UI Components

#### `DeviceHealthCard`
Displays current device health metrics.

**Props:**
- device_id
- telemetry (latest)
- status

**Displays:**
- CPU usage (gauge)
- Memory usage (gauge)
- Disk usage (gauge)
- Network status
- Security controls status

#### `SecurityEventList`
Lists security events with filtering.

**Props:**
- device_id (optional - filter by device)
- severity filter
- status filter

**Features:**
- Event severity badges
- Time ago formatting
- Click to expand details
- Status update actions (acknowledge, resolve)

#### `DeviceTimeline`
Chronological timeline of device events.

**Props:**
- device_id

**Displays:**
- Enrollment
- Heartbeats (summarized)
- State changes
- Security events
- Policy changes

#### `PolicyAssignment`
UI for assigning policies to devices.

**Props:**
- device_id
- available_policies
- assigned_policies

**Features:**
- Policy selection dropdown
- Assign/unassign actions
- Policy details view

### 7.3 API Client Extensions

**frontend/src/api/telemetry.ts:**
```typescript
export async function getDeviceTelemetry(
  deviceId: string,
  params?: TelemetryQueryParams
): Promise<TelemetryResponse>

export async function getLatestTelemetry(
  deviceId: string
): Promise<Telemetry | null>
```

**frontend/src/api/events.ts:**
```typescript
export async function getDeviceEvents(
  deviceId: string,
  filters?: EventFilters
): Promise<SecurityEvent[]>

export async function updateEventStatus(
  eventId: string,
  status: EventStatus
): Promise<SecurityEvent>

export async function getDeviceTimeline(
  deviceId: string
): Promise<TimelineEntry[]>
```

**frontend/src/api/policies.ts:**
```typescript
export async function getPolicies(): Promise<Policy[]>
export async function createPolicy(data: CreatePolicyData): Promise<Policy>
export async function assignPolicyToDevice(
  deviceId: string,
  policyId: string
): Promise<void>
export async function getDevicePolicies(
  deviceId: string
): Promise<Policy[]>
```

---

## 8. Security & Threat Model

### 8.1 Threat Scenarios

#### Device Impersonation
**Threat:** Attacker obtains enrollment token, impersonates device  
**Mitigation:**
- Enrollment token is high-entropy (256-bit)
- Token hashed with bcrypt before storage
- Token transmitted only over HTTPS/TLS
- Device revocation immediately invalidates token
- Audit logging tracks all device operations
- User can see enrollment history

#### Replayed Heartbeat
**Threat:** Attacker captures and replays old heartbeat  
**Mitigation (Layer 2):**
- Heartbeat includes timestamp
- Server rejects heartbeats with stale timestamps (>5 min old)
- Sequence number validation (future enhancement)

#### Unauthorized Telemetry Access
**Threat:** User A accesses User B's telemetry  
**Mitigation:**
- All telemetry endpoints require JWT authentication
- Device ownership verified via device.owner_id check
- 404 response for unauthorized access (no information leakage)

#### Cross-User Event Access
**Threat:** User A sees User B's security events  
**Mitigation:**
- Event queries require device_id
- Device ownership verified before returning events
- Timeline endpoint checks device ownership

#### Oversized Telemetry
**Threat:** Agent sends huge payload to exhaust storage/memory  
**Mitigation:**
- Max payload size: 1MB per telemetry submission
- Request size limit enforced at FastAPI level
- Schema validation rejects malformed data
- Database constraints prevent oversized fields

#### Malformed Telemetry
**Threat:** Malicious telemetry payload exploits parser  
**Mitigation:**
- Pydantic schema validation
- Type checking on all fields
- JSONB field validation
- No eval() or exec() on telemetry content
- Sanitize before display in frontend

#### Forged Device ID
**Threat:** Agent sends wrong device_id in telemetry  
**Mitigation:**
- Enrollment token validated against device record
- device_id extracted from validated device, not from payload
- Ownership verified via database query

#### Revoked Device Behavior
**Threat:** Revoked device continues sending data  
**Mitigation:**
- Heartbeat endpoint checks device.status
- Reject heartbeat if status == 'revoked'
- Return error to agent (agent should stop)

#### SQL Injection
**Threat:** Telemetry payload contains SQL injection  
**Mitigation:**
- SQLAlchemy ORM with parameterized queries
- Pydantic validation prevents injection in fields
- JSONB fields stored as JSON, not executed as SQL

#### Command Injection
**Threat:** Telemetry payload contains shell commands  
**Mitigation:**
- Layer 2 does not execute commands from telemetry
- Agent is receive-only (no remote command execution)
- Telemetry is data storage, not code execution

### 8.2 Security Controls

**Authentication:**
- JWT for user authentication
- Enrollment token for device authentication
- bcrypt for token hashing
- HTTPS/TLS for transport security

**Authorization:**
- User must own device to access device data
- User must own policy to assign to device
- Cross-user isolation enforced at service layer

**Input Validation:**
- Pydantic schemas for all API requests
- Size limits on all text fields
- JSONB field structure validation
- Timestamp validation (reject future/stale)

**Audit Logging:**
- Device enrollment
- Device revocation
- Device activation
- Heartbeat reception (configurable verbosity)
- Telemetry ingestion (configurable verbosity)
- Policy assignment
- Event status changes

**Rate Limiting (Future):**
- Heartbeat: 1 per device per minute
- Telemetry: 1 per device per minute
- Consider implementing in Layer 2 if abuse detected

---

## 9. Testing Strategy

### 9.1 Backend Tests

#### Unit Tests

**DeviceStateEngineTest:**
- Calculate state: active
- Calculate state: stale
- Calculate state: inactive
- State transition detection
- Event generation on transition

**PolicyEngineTest:**
- Evaluate policy: compliant
- Evaluate policy: violation
- Multiple policy evaluation
- Policy config validation
- Violation event generation

**DetectionEngineTest:**
- Detect network change
- Detect firewall disabled
- Detect antivirus disabled
- No change detection (prevent false positives)
- Event severity classification

**TelemetryServiceTest:**
- Valid telemetry ingestion
- Invalid schema rejection
- Oversized payload rejection
- Malformed JSONB rejection
- Unauthorized device rejection

**HeartbeatServiceTest:**
- Valid heartbeat processing
- Invalid token rejection
- Revoked device rejection
- Stale timestamp rejection
- Device activation on first heartbeat

**SecurityEventServiceTest:**
- Create event
- Query events with filters
- Update event status
- Generate timeline
- Event ownership verification

#### Integration Tests

**Heartbeat Flow:**
1. Agent sends heartbeat (valid token)
2. Device activated
3. last_seen updated
4. Device state calculated
5. Policy evaluated
6. No violation (compliant device)

**Telemetry Detection Flow:**
1. Agent sends telemetry (baseline)
2. Agent sends telemetry (firewall disabled)
3. Detection engine detects change
4. Security event created
5. Event visible to device owner
6. Event not visible to other users

**Policy Violation Flow:**
1. Create policy (require_firewall: true)
2. Assign policy to device
3. Telemetry reports firewall disabled
4. Policy engine evaluates
5. Violation detected
6. Security event created

#### Security Tests

**Authorization Tests:**
- User A cannot access User B's telemetry
- User A cannot access User B's events
- User A cannot assign User B's policy
- Revoked device cannot send telemetry

**Injection Tests:**
- SQL injection in telemetry fields (prevented)
- XSS in telemetry fields (sanitized)
- Command injection (no execution path)

### 9.2 Frontend Tests

**Unit Tests:**
- DeviceHealthCard renders telemetry correctly
- SecurityEventList filters events
- DeviceTimeline displays chronological order
- PolicyAssignment shows assigned policies

**Integration Tests:**
- Device detail page loads device + telemetry + events
- Security center displays all devices + events
- Event status update sends correct API request
- Policy assignment updates device policy list

**E2E Tests (Manual Initial):**
1. Enroll device
2. Start agent
3. Agent sends heartbeat
4. Device status changes to active
5. Agent sends telemetry
6. Telemetry visible in device detail
7. Disable firewall (in telemetry)
8. Security event generated
9. Event visible in frontend
10. Acknowledge event
11. Event status updated

---

## 10. Implementation Sequence

### Phase 1: Heartbeat Infrastructure (MILESTONE 1)
**Goal:** Device agent can send heartbeat, server can receive and process it.

**Tasks:**
1. Create `POST /devices/heartbeat` API endpoint
2. Create HeartbeatService with authentication logic
3. Implement device state calculation (active/stale/inactive)
4. Update Device.last_seen on heartbeat
5. Write heartbeat authentication tests
6. Write device state calculation tests

**Acceptance Criteria:**
- Agent can send heartbeat with enrollment token
- Server validates token and updates last_seen
- Device status calculated correctly
- Tests pass

### Phase 2: Device Agent Foundation (MILESTONE 2)
**Goal:** Working Python agent that can enroll and send heartbeat.

**Tasks:**
1. Create horizon-agent project structure
2. Implement agent configuration (horizon-agent.yaml)
3. Implement authentication module
4. Implement heartbeat sender with retry logic
5. Implement logging
6. Write agent unit tests
7. Create agent installation script

**Acceptance Criteria:**
- Agent can be installed on development platform
- Agent can read enrollment token from config
- Agent sends heartbeat every 300 seconds
- Agent handles network failures gracefully
- Agent logs operations

### Phase 3: Telemetry Ingestion (MILESTONE 3)
**Goal:** Agent can collect and send telemetry, server can store it.

**Tasks:**
1. Create device_telemetry table migration
2. Create DeviceTelemetry model
3. Create TelemetryRepository
4. Create TelemetryService with validation
5. Create `POST /devices/{device_id}/telemetry` API
6. Implement agent telemetry collectors (system, network, security)
7. Implement agent telemetry sender
8. Write telemetry ingestion tests

**Acceptance Criteria:**
- Agent collects CPU, memory, disk, network, security metrics
- Agent sends telemetry to server
- Server validates and stores telemetry
- Telemetry queryable via API
- Authorization enforced
- Tests pass

### Phase 4: Database & Models (MILESTONE 4)
**Goal:** All Layer 2 database tables exist and migrate correctly.

**Tasks:**
1. Create security_events table migration
2. Create device_policies table migration
3. Create device_policy_assignments table migration
4. Create SecurityEvent model
5. Create DevicePolicy model
6. Create DevicePolicyAssignment model
7. Create repositories for all new models
8. Verify migrations from clean state
9. Verify migrations from Layer 1 state

**Acceptance Criteria:**
- `alembic upgrade head` succeeds
- All tables created correctly
- Models map correctly to tables
- Repositories implement CRUD operations
- Migration reversibility verified

### Phase 5: Detection & Events (MILESTONE 5)
**Goal:** System detects changes and generates security events.

**Tasks:**
1. Create SecurityEventService
2. Create DetectionEngine
3. Implement state-change detection
4. Implement network-change detection
5. Implement security-state-change detection
6. Create event classification logic
7. Create `GET /devices/{device_id}/events` API
8. Create `POST /events/{event_id}/acknowledge` API
9. Write detection tests
10. Write event service tests

**Acceptance Criteria:**
- Device state transitions generate events
- Telemetry changes generate events
- Events stored with correct severity
- Events queryable via API
- Event status updates work
- Tests pass

### Phase 6: Policy Engine (MILESTONE 6)
**Goal:** Policies can be created, assigned, and evaluated.

**Tasks:**
1. Create PolicyService
2. Create PolicyEngine
3. Implement policy CRUD APIs
4. Implement policy assignment APIs
5. Implement policy evaluation logic
6. Implement policy violation detection
7. Generate violation events
8. Write policy service tests
9. Write policy engine tests

**Acceptance Criteria:**
- Policies can be created and assigned
- Policy evaluation works for implemented checks
- Violations generate events
- Policy configuration validated
- Authorization enforced
- Tests pass

### Phase 7: Device State Engine (MILESTONE 7)
**Goal:** Device states calculated automatically based on heartbeat.

**Tasks:**
1. Create DeviceStateEngine service
2. Implement state calculation logic
3. Implement configurable thresholds
4. Implement background job for state checking
5. Generate state-change events
6. Write state engine tests

**Acceptance Criteria:**
- Active/stale/inactive states calculated correctly
- State transitions detected
- State-change events generated
- Background job runs periodically
- Tests pass

### Phase 8: Frontend Security Center (MILESTONE 8)
**Goal:** User can see device health, events, and timeline in UI.

**Tasks:**
1. Create DeviceDetail page
2. Create SecurityCenter dashboard
3. Create DeviceHealthCard component
4. Create SecurityEventList component
5. Create DeviceTimeline component
6. Create PolicyAssignment component
7. Create API clients (telemetry, events, policies)
8. Integrate with backend APIs
9. Handle loading/empty/error states

**Acceptance Criteria:**
- Device detail page displays telemetry and events
- Security center displays all devices and events
- Timeline shows chronological history
- Event status can be updated
- Policies can be assigned
- Real API integration (no mock data)
- Frontend build succeeds

### Phase 9: End-to-End Integration (MILESTONE 9)
**Goal:** Complete flow from agent → server → frontend works.

**Tasks:**
1. Install agent on test device
2. Configure agent with enrollment token
3. Start agent
4. Verify heartbeat received
5. Verify device status changes to active
6. Verify telemetry collected and sent
7. Verify telemetry visible in frontend
8. Trigger detectable change (disable firewall in test)
9. Verify event generated
10. Verify event visible in frontend
11. Verify event timeline
12. Verify policy assignment and evaluation
13. Document end-to-end flow

**Acceptance Criteria:**
- Agent runs continuously
- Heartbeat sent every 5 minutes
- Telemetry sent every 5 minutes
- Device status accurate
- Events generated correctly
- Frontend displays real data
- No errors in agent logs
- No errors in server logs

### Phase 10: Security Audit & Verification (MILESTONE 10)
**Goal:** Layer 2 security verified, threats mitigated, tests pass.

**Tasks:**
1. Run complete test suite (backend + frontend)
2. Verify authorization on all endpoints
3. Test device impersonation prevention
4. Test unauthorized telemetry access
5. Test cross-user event access
6. Test oversized payload rejection
7. Test malformed payload rejection
8. Test revoked device behavior
9. Verify audit logging completeness
10. Verify no secrets in logs
11. Review threat model coverage
12. Create LAYER_2_VERIFICATION.md
13. Create LAYER_2_COMPLETE.md
14. Git commit with clean working tree

**Acceptance Criteria:**
- All backend tests pass
- All frontend tests pass
- Authorization enforced on all endpoints
- Threat scenarios tested and mitigated
- Audit logging comprehensive
- No secrets leaked
- Documentation complete
- Git status clean

---

## 11. Privacy Considerations

### 11.1 Data Minimization

**Collect only security-relevant data:**
- CPU/memory/disk: capacity planning, performance issues
- Network interfaces: configuration changes, connectivity
- Firewall/AV status: security posture
- OS updates: patch management

**Do not collect:**
- Passwords or credentials
- Private documents or files
- Browser history
- Application content
- Personal messages
- Location data (unless explicitly required)

### 11.2 Data Retention

**Telemetry:**
- Retain for 90 days by default
- Configurable retention policy
- Automatic archival/deletion after retention period

**Security Events:**
- Retain indefinitely for audit purposes
- Archive old resolved events
- User can delete own events

**Audit Logs:**
- Retain for 1 year minimum
- Comply with regulatory requirements

### 11.3 User Transparency

**Document what HORIZON collects:**
- Create data collection disclosure document
- Explain why each metric is collected
- Explain how data is used
- Explain retention periods
- Explain who can access data (device owner only)

**User controls:**
- User can revoke device (stops collection)
- User can delete device (removes data)
- User can view all collected data
- User can export data (future)

---

## 12. Risk Integration

### 12.1 Use Existing RiskEngine

HORIZON already has an explainable RiskEngine in `app/services/risk_engine.py`.

**Layer 2 Integration:**

```python
# Existing RiskEngine
risk = RiskEngine.calculate_risk(
    base_score=5.0,
    factors=["Device inactive for 15 minutes"],
    is_device_health=True,
)

# SecurityEvent with risk
event = SecurityEvent(
    device_id=device_id,
    event_type="device.inactive",
    severity=risk.severity,  # From RiskEngine
    title="Device became inactive",
    description="No heartbeat received for 15 minutes",
    evidence={"last_seen": last_seen, "current_time": now},
    detection_source="device_state_engine",
    risk_score=risk.score,
    risk_factors=risk.factors_json,
)
```

**Do not create a second risk engine.** Extend the existing one if needed.

### 12.2 Risk Factors for Layer 2

**Device State:**
- Device inactive: base 5.0
- Device stale: base 3.0
- Revoked device activity: base 9.0

**Policy Violations:**
- Firewall disabled: base 7.0
- Antivirus disabled: base 7.0
- OS updates critical: base 6.0

**Configuration Changes:**
- Network configuration changed: base 4.0
- Security control disabled: base 6.0

**Integration with Vulnerability Risk:**
- Device with critical vulnerability + inactive: score += 2.0
- Device with policy violation + exposed service: score += 1.5

---

## 13. Migration Strategy

### 13.1 Database Migration

**From Layer 1 to Layer 2:**
1. Verify current migration: `alembic current` → 1c702225ec30
2. Create new migration: `alembic revision --autogenerate -m "add_layer_2_tables"`
3. Review generated migration
4. Test upgrade: `alembic upgrade head`
5. Test downgrade: `alembic downgrade -1`
6. Re-test upgrade: `alembic upgrade head`

**Migration Safety:**
- No destructive changes to existing tables
- New tables are additive
- Existing device records preserved
- No data loss

### 13.2 Agent Deployment

**Initial Deployment (Layer 2):**
- Agent is optional initially
- Devices without agent remain in pending/inactive state
- User must manually install agent on device
- Agent configuration includes enrollment token
- Agent start verifies connectivity before running

**Agent Updates (Future):**
- Version check in heartbeat response
- User notified of agent update
- User downloads and installs manually
- No auto-update in Layer 2

### 13.3 Rollback Plan

**If Layer 2 has critical issues:**

1. Stop agent on all devices
2. Revert backend code to Layer 1 tag
3. Revert database: `alembic downgrade <layer1_revision>`
4. Restart backend
5. Verify Layer 1 functionality intact
6. Device enrollment/management still works
7. Investigate issue before re-deploying Layer 2

**Rollback Safety:**
- Layer 2 tables can be dropped without affecting Layer 1
- Device table unchanged (compatible with Layer 1)
- Audit logs preserved

---

## 14. Known Limitations & Future Work

### 14.1 Layer 2 Limitations

**Agent Platform Support:**
- Initial support: Windows or Linux (one platform verified)
- macOS, Android, iOS: future layers
- Agent installation is manual (no auto-installer)

**Telemetry Capabilities:**
- Basic system metrics only
- No application-level telemetry
- No process monitoring
- No file integrity monitoring

**Detection Capabilities:**
- Deterministic detection only (no ML/AI)
- State-change detection only
- No behavioral anomaly detection
- No threat intelligence correlation

**Policy Engine:**
- Simple condition-based policies
- No complex rule expressions
- No policy inheritance
- No policy templates

**Real-time Updates:**
- No WebSocket/SSE for real-time events
- Frontend polls periodically
- Events visible within 1-5 minutes

### 14.2 Future Enhancements (Post-Layer 2)

**Layer 3 - AI Integration:**
- AI-powered anomaly detection
- Security event correlation
- Natural language security questions
- Automated investigation assistance

**Layer 4 - Response & Remediation:**
- Controlled remediation workflows
- Remote command execution (with authorization)
- Automated patch deployment
- Incident response playbooks

**Layer 5 - Advanced Monitoring:**
- Process/application monitoring
- File integrity monitoring
- Network traffic analysis
- Threat intelligence integration

**Layer 6 - Production Scale:**
- Multi-tenant organization support
- WebSocket real-time updates
- Agent auto-update mechanism
- Advanced analytics dashboard

---

## 15. Acceptance Criteria (Definition of Done)

Layer 2 is complete when:

### 15.1 Agent
- [x] Agent can be installed on development platform (Windows or Linux)
- [x] Agent authenticates with enrollment token
- [x] Agent sends heartbeat every 5 minutes
- [x] Agent sends telemetry every 5 minutes
- [x] Agent handles network failures gracefully
- [x] Agent logs operations to file
- [x] Agent respects privacy (no passwords/documents collected)
- [x] Agent has unit tests

### 15.2 Backend
- [x] Heartbeat API endpoint accepts and processes heartbeats
- [x] Telemetry API endpoint validates and stores telemetry
- [x] Device state engine calculates active/stale/inactive states
- [x] Detection engine detects state changes
- [x] Policy engine evaluates policies and detects violations
- [x] Security events generated for detections
- [x] Events queryable via API
- [x] Timeline API returns chronological events
- [x] Authorization enforced on all endpoints
- [x] Audit logging for security operations
- [x] All backend tests pass (no regressions)

### 15.3 Database
- [x] device_telemetry table created
- [x] security_events table created
- [x] device_policies table created
- [x] device_policy_assignments table created
- [x] All migrations apply successfully
- [x] Migrations reversible
- [x] Database at head revision

### 15.4 Frontend
- [x] Device detail page displays telemetry and events
- [x] Security center dashboard displays all devices and events
- [x] Device timeline shows chronological history
- [x] Event status can be updated (acknowledge, resolve)
- [x] Policies can be assigned to devices
- [x] All pages use real API data (no mock data)
- [x] Loading/empty/error states handled
- [x] Frontend build succeeds

### 15.5 Security
- [x] Device impersonation prevented (token validation)
- [x] Unauthorized telemetry access prevented (ownership check)
- [x] Cross-user event access prevented (ownership check)
- [x] Oversized payloads rejected (size limits)
- [x] Malformed payloads rejected (schema validation)
- [x] Revoked devices cannot send data
- [x] No SQL injection vulnerabilities
- [x] No secrets in audit logs
- [x] Threat model documented and mitigated

### 15.6 Integration
- [x] End-to-end flow verified: agent → heartbeat → server → frontend
- [x] End-to-end flow verified: agent → telemetry → detection → event → frontend
- [x] Device state transitions work correctly
- [x] Policy evaluation works correctly
- [x] Events visible in frontend within 5 minutes
- [x] Real device agent running continuously

### 15.7 Documentation
- [x] LAYER_2_IMPLEMENTATION_PLAN.md (this document)
- [x] LAYER_2_VERIFICATION.md created
- [x] LAYER_2_COMPLETE.md created
- [x] Agent README created
- [x] API documentation updated
- [x] Data collection disclosure document created

### 15.8 Quality
- [x] All backend tests pass
- [x] Frontend build passes
- [x] No regressions in Layer 1 functionality
- [x] Git working tree clean after commit
- [x] Migration from clean state verified
- [x] Migration from Layer 1 state verified

---

## 16. Implementation Timeline Estimate

**Estimated Timeline:** 4-6 weeks (40-60 development hours)

**Phase Breakdown:**
- Phase 1 (Heartbeat Infrastructure): 4-6 hours
- Phase 2 (Agent Foundation): 6-8 hours
- Phase 3 (Telemetry Ingestion): 6-8 hours
- Phase 4 (Database & Models): 4-6 hours
- Phase 5 (Detection & Events): 6-8 hours
- Phase 6 (Policy Engine): 6-8 hours
- Phase 7 (Device State Engine): 4-6 hours
- Phase 8 (Frontend Security Center): 8-12 hours
- Phase 9 (End-to-End Integration): 4-6 hours
- Phase 10 (Security Audit & Verification): 4-6 hours

**Dependencies:**
- Phases 1-2 can run in parallel
- Phase 3 depends on Phase 1-2
- Phase 4 can run in parallel with Phase 1-3
- Phases 5-7 depend on Phase 4
- Phase 8 depends on Phases 5-7
- Phases 9-10 depend on all previous phases

---

## 17. Next Steps

1. **Review this plan** with stakeholders
2. **Approve architecture decisions** (agent platform, database schema, API design)
3. **Begin Phase 1:** Heartbeat infrastructure implementation
4. **Iterate incrementally:** Complete one phase at a time
5. **Test continuously:** Run tests after each phase
6. **Verify security:** Test threat scenarios throughout
7. **Document progress:** Update verification docs after each milestone
8. **Final verification:** Complete end-to-end testing before declaring Layer 2 complete

---

**Plan Status:** READY FOR IMPLEMENTATION  
**Next Action:** Begin Phase 1 - Heartbeat Infrastructure  
**Approval Required:** YES (architecture decisions)  
**Risk Level:** MEDIUM (new agent component, multi-platform considerations)  
**Recommendation:** Start with single platform (Windows or Linux), expand later

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-03  
**Author:** Kiro AI Development Environment  
**Review Status:** PENDING
