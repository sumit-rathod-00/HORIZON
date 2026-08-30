from __future__ import annotations

import asyncio
import ipaddress
import logging
import subprocess
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class NmapScanner:
    """Run controlled Nmap scans without depending on the Windows asyncio subprocess transport."""

    async def scan_host(self, target: str) -> str:
        """Run a basic Nmap service-detection scan against one validated IP address."""
        self._validate_target(target)

        nmap_path = Path(settings.NMAP_PATH)
        if not nmap_path.is_file():
            raise FileNotFoundError("Configured Nmap executable was not found")

        command = [str(nmap_path), "-sV", target.strip()]
        logger.info("Starting Nmap scan for target %s", target.strip())

        # asyncio.create_subprocess_exec() raises NotImplementedError under the
        # Windows event-loop configuration currently used by the application.
        # subprocess.run() is blocking, so execute it in a worker thread to keep
        # the FastAPI event loop responsive while remaining cross-platform.
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
            detail = error.strip() or output.strip() or "no diagnostic output"
            raise RuntimeError(
                f"Nmap exited with code {completed.returncode}: {detail}"
            )

        return output

    @staticmethod
    def _validate_target(target: str) -> None:
        """Only allow a single IPv4/IPv6 address for now."""
        try:
            ipaddress.ip_address(target.strip())
        except ValueError as exc:
            raise ValueError(
                "Invalid scan target. Only a valid IP address is allowed."
            ) from exc
