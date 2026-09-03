"""Configuration management for HORIZON agent."""
import yaml
from pathlib import Path
from typing import Any


def load_config(config_path: Path) -> dict[str, Any]:
    """Load agent configuration from YAML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Validate required fields
    if "server" not in config or "url" not in config["server"]:
        raise ValueError("Configuration must include server.url")

    if "device" not in config or "enrollment_token" not in config["device"]:
        raise ValueError("Configuration must include device.enrollment_token")

    # Set defaults
    config.setdefault("heartbeat", {})
    config["heartbeat"].setdefault("interval_seconds", 300)
    config["heartbeat"].setdefault("timeout_seconds", 30)

    config.setdefault("telemetry", {})
    config["telemetry"].setdefault("enabled", True)
    config["telemetry"].setdefault("interval_seconds", 300)

    config.setdefault("logging", {})
    config["logging"].setdefault("level", "INFO")

    config["server"].setdefault("verify_ssl", True)

    return config


def save_device_id(config_path: Path, device_id: str):
    """Save device ID to configuration after activation."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    config["device"]["device_id"] = device_id

    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)
