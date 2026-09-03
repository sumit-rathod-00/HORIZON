# HORIZON Device Agent

Python-based device agent for HORIZON cybersecurity platform.

## Installation

```bash
pip install -r requirements.txt
python -m agent.main --config horizon-agent.yaml
```

## Configuration

Create `horizon-agent.yaml`:

```yaml
server:
  url: http://localhost:8000/api/v1
  verify_ssl: false

device:
  enrollment_token: <your-token-from-enrollment>
  device_id: null  # Will be set after first heartbeat

heartbeat:
  interval_seconds: 300
  timeout_seconds: 30

telemetry:
  enabled: true
  interval_seconds: 300

logging:
  level: INFO
```

## Running

```bash
python -m agent.main
```

## Windows Service (Future)

The agent can be installed as a Windows service for continuous operation.

## Security

- Enrollment token is required for authentication
- All communication uses HTTPS in production
- Token should be stored securely (file permissions restricted)
- No arbitrary command execution from server
