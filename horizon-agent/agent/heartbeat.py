"""Heartbeat sender for device health monitoring."""
import logging
from datetime import datetime, timezone
from typing import Any

import requests


class HeartbeatSender:
    """Sends heartbeat to HORIZON server."""

    AGENT_VERSION = "1.0.0"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.verify = config["server"].get("verify_ssl", True)

    def send_heartbeat(self) -> dict[str, Any]:
        """Send heartbeat to server."""
        device_id = self.config["device"].get("device_id")
        enrollment_token = self.config["device"]["enrollment_token"]

        payload = {
            "device_id": device_id,
            "enrollment_token": enrollment_token,
            "agent_version": self.AGENT_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
        }

        url = f"{self.config['server']['url']}/devices/heartbeat"
        timeout = self.config["heartbeat"]["timeout_seconds"]

        self.logger.debug(f"Sending heartbeat to {url}")

        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()

            data = response.json()
            self.logger.info(f"Heartbeat sent successfully: {data.get('message', 'OK')}")

            # Save device_id if first heartbeat
            if not device_id and "device_id" in data:
                from agent.config import save_device_id
                from pathlib import Path

                save_device_id(
                    Path("horizon-agent.yaml"),
                    data["device_id"],
                )
                self.config["device"]["device_id"] = data["device_id"]
                self.logger.info(f"Device activated: {data['device_id']}")

            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Heartbeat failed: {e}")
            raise
