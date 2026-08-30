from __future__ import annotations

import asyncio
import ipaddress
import logging
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NmapPortResult:
    port: int
    protocol: str
    state: str
    service: str | None
    product: str | None
    version: str | None
    hostname: str | None


@dataclass(frozen=True)
class NmapScanResult:
    raw_output: str
    ports: list[NmapPortResult]


class NmapScanner:
    """Run a controlled Nmap service-detection scan and parse XML output."""

    async def scan_host(self, target: str) -> NmapScanResult:
        self._validate_target(target)

        nmap_path = Path(settings.NMAP_PATH)
        if not nmap_path.is_file():
            raise FileNotFoundError("Configured Nmap executable was not found")

        command = [str(nmap_path), "-sV", "-oX", "-", target.strip()]
        logger.info("Starting Nmap scan for target %s", target.strip())

        completed = await asyncio.to_thread(
            subprocess.run,
            command,
            capture_output=True,
            timeout=settings.NMAP_TIMEOUT_SECONDS,
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        output = completed.stdout or ""
        error = completed.stderr or ""
        if completed.returncode != 0:
            detail = error.strip() or "no diagnostic output"
            raise RuntimeError(f"Nmap exited with code {completed.returncode}: {detail}")

        return NmapScanResult(raw_output=output, ports=self._parse_xml(output))

    @staticmethod
    def _parse_xml(output: str) -> list[NmapPortResult]:
        try:
            root = ET.fromstring(output)
        except ET.ParseError as exc:
            raise RuntimeError("Nmap returned invalid structured output") from exc

        results: list[NmapPortResult] = []
        for host in root.findall("host"):
            hostname_node = host.find("hostnames/hostname")
            hostname = hostname_node.get("name") if hostname_node is not None else None
            for port in host.findall("ports/port"):
                state_node = port.find("state")
                service_node = port.find("service")
                if state_node is None:
                    continue
                portid = port.get("portid")
                protocol = port.get("protocol")
                if not portid or not protocol:
                    continue
                try:
                    port_number = int(portid)
                except ValueError:
                    continue
                results.append(
                    NmapPortResult(
                        port=port_number,
                        protocol=protocol,
                        state=state_node.get("state", "unknown"),
                        service=service_node.get("name") if service_node is not None else None,
                        product=service_node.get("product") if service_node is not None else None,
                        version=service_node.get("version") if service_node is not None else None,
                        hostname=hostname,
                    )
                )
        return results

    @staticmethod
    def _validate_target(target: str) -> None:
        try:
            ipaddress.ip_address(target.strip())
        except ValueError as exc:
            raise ValueError("Invalid scan target. Only a valid IP address is allowed.") from exc
