from __future__ import annotations

import asyncio
import ipaddress


NMAP_PATH = r"C:\Program Files (x86)\Nmap\nmap.exe"


class NmapScanner:
    async def scan_host(self, target: str) -> str:
        """
        Run a basic Nmap service-detection scan
        against a validated IP address.
        """

        self._validate_target(target)

        process = await asyncio.create_subprocess_exec(
            NMAP_PATH,
            "-sV",
            target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        output = stdout.decode(
            "utf-8",
            errors="replace",
        )

        error = stderr.decode(
            "utf-8",
            errors="replace",
        )

        if process.returncode != 0:
            raise RuntimeError(
                f"Nmap scan failed with exit code "
                f"{process.returncode}: {error or output}"
            )

        return output

    @staticmethod
    def _validate_target(target: str) -> None:
        """
        Only allow a single IPv4/IPv6 address for now.
        """

        try:
            ipaddress.ip_address(target)
        except ValueError as exc:
            raise ValueError(
                "Invalid scan target. "
                "Only a valid IP address is allowed."
            ) from exc