from __future__ import annotations

import asyncio
import ipaddress
from pathlib import Path

from app.core.config import settings


class NmapScanner:
    async def scan_host(self, target: str) -> str:
        """
        Run a basic Nmap service-detection scan against a validated IP address.
        """
        self._validate_target(target)

        nmap_path = Path(settings.NMAP_PATH)
        if not nmap_path.is_file():
            raise FileNotFoundError(
                f"Nmap executable was not found at configured path: {nmap_path}"
            )

        process = await asyncio.create_subprocess_exec(
            str(nmap_path),
            "-sV",
            target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        output = stdout.decode("utf-8", errors="replace")
        error = stderr.decode("utf-8", errors="replace")

        if process.returncode != 0:
            detail = error.strip() or output.strip() or "no diagnostic output"
            raise RuntimeError(
                f"Nmap exited with code {process.returncode}: {detail}"
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
