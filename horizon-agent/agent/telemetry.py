"""Telemetry collection and sending."""
import logging
import platform
from datetime import datetime, timezone
from typing import Any

import psutil
import requests


class TelemetrySender:
    """Collects and sends device telemetry."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.verify = config["server"].get("verify_ssl", True)

    def collect_telemetry(self) -> dict[str, Any]:
        """Collect system telemetry."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory
        memory = psutil.virtual_memory()

        # Disk (primary partition)
        disk = psutil.disk_usage("/")

        # Network interfaces
        network_interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == 2:  # IPv4
                    network_interfaces.append({
                        "name": interface,
                        "ip": addr.address,
                        "status": "up",
                    })

        # Active connections
        active_connections = len(psutil.net_connections())

        telemetry = {
            "telemetry_version": "1.0",
            "agent_version": "1.0.0",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "cpu_usage_percent": round(cpu_percent, 2),
            "memory_total_mb": memory.total // (1024 * 1024),
            "memory_used_mb": memory.used // (1024 * 1024),
            "memory_usage_percent": round(memory.percent, 2),
            "disk_total_gb": disk.total // (1024 * 1024 * 1024),
            "disk_used_gb": disk.used // (1024 * 1024 * 1024),
            "disk_usage_percent": round((disk.used / disk.total) * 100, 2),
            "network_interfaces": network_interfaces,
            "active_connections": active_connections,
            "extra_data": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "hostname": platform.node(),
            },
        }

        # Windows-specific: Try to get firewall/AV status
        if platform.system() == "Windows":
            telemetry["firewall_enabled"] = self._check_windows_firewall()
            telemetry["antivirus_enabled"] = self._check_windows_defender()

        return telemetry

    def _check_windows_firewall(self) -> bool | None:
        """Check if Windows firewall is enabled."""
        try:
            import subprocess
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles", "state"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "ON" in result.stdout
        except Exception:
            return None

    def _check_windows_defender(self) -> bool | None:
        """Check if Windows Defender is enabled."""
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", "Get-MpComputerStatus | Select-Object -ExpandProperty AntivirusEnabled"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "True" in result.stdout
        except Exception:
            return None

    def send_telemetry(self) -> dict[str, Any]:
        """Collect and send telemetry to server."""
        device_id = self.config["device"].get("device_id")

        if not device_id:
            self.logger.warning("No device_id yet, skipping telemetry")
            return {}

        enrollment_token = self.config["device"]["enrollment_token"]

        telemetry = self.collect_telemetry()

        url = f"{self.config['server']['url']}/devices/{device_id}/telemetry"

        self.logger.debug(f"Sending telemetry to {url}")

        try:
            response = self.session.post(
                url,
                json=telemetry,
                headers={"X-Enrollment-Token": enrollment_token},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            self.logger.info("Telemetry sent successfully")

            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Telemetry send failed: {e}")
            raise
