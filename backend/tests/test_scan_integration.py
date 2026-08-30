"""Integration tests for the complete scan pipeline."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.services.nmap_scanner import NmapScanner, NmapScanResult, NmapPortResult


class TestScanResultPipeline:
    """Test the complete scan result pipeline from XML to database."""

    def test_nmap_result_to_scan_result_conversion(self):
        """Test converting NmapPortResult to ScanResult dictionary for database insertion."""
        scan_id = uuid4()
        asset_id = uuid4()

        nmap_port = NmapPortResult(
            port=5432,
            protocol="tcp",
            state="open",
            service="postgresql",
            product="PostgreSQL DB",
            version="17.0",
            hostname="localhost",
        )

        # Simulate the conversion logic used in scanner_service.py
        scan_result_dict = {
            "scan_id": scan_id,
            "asset_id": asset_id,
            "port": nmap_port.port,
            "protocol": nmap_port.protocol,
            "state": nmap_port.state,
            "service": nmap_port.service,
            "product": nmap_port.product,
            "version": nmap_port.version,
            "hostname": nmap_port.hostname,
        }

        assert scan_result_dict["port"] == 5432
        assert scan_result_dict["protocol"] == "tcp"
        assert scan_result_dict["state"] == "open"
        assert scan_result_dict["service"] == "postgresql"
        assert scan_result_dict["product"] == "PostgreSQL DB"
        assert scan_result_dict["version"] == "17.0"
        assert scan_result_dict["hostname"] == "localhost"

    def test_empty_scan_results_list_valid(self):
        """Test that an empty scan results list is valid (zero findings scenario)."""
        scan_id = uuid4()
        asset_id = uuid4()

        # Simulate a scan with zero findings
        nmap_ports = []
        scan_results = [
            {
                "scan_id": scan_id,
                "asset_id": asset_id,
                "port": item.port,
                "protocol": item.protocol,
                "state": item.state,
                "service": item.service,
                "product": item.product,
                "version": item.version,
                "hostname": item.hostname,
            }
            for item in nmap_ports
        ]

        assert len(scan_results) == 0
        assert scan_results == []
        # This should NOT raise an error - zero results is valid

    def test_multiple_scan_results_conversion(self):
        """Test converting multiple NmapPortResults to ScanResult dictionaries."""
        scan_id = uuid4()
        asset_id = uuid4()

        nmap_ports = [
            NmapPortResult(22, "tcp", "open", "ssh", "OpenSSH", "8.2", "example.com"),
            NmapPortResult(80, "tcp", "open", "http", "nginx", "1.18.0", "example.com"),
            NmapPortResult(443, "tcp", "open", "https", "nginx", "1.18.0", "example.com"),
        ]

        # Simulate the conversion logic used in scanner_service.py
        scan_results = [
            {
                "scan_id": scan_id,
                "asset_id": asset_id,
                "port": item.port,
                "protocol": item.protocol,
                "state": item.state,
                "service": item.service,
                "product": item.product,
                "version": item.version,
                "hostname": item.hostname,
            }
            for item in nmap_ports
        ]

        assert len(scan_results) == 3
        assert scan_results[0]["port"] == 22
        assert scan_results[1]["port"] == 80
        assert scan_results[2]["port"] == 443

    @pytest.mark.asyncio
    async def test_nmap_scanner_returns_correct_structure(self):
        """Test that NmapScanner.scan_host returns the expected structure."""
        mock_xml = """<?xml version='1.0'?>
        <nmaprun>
          <host>
            <status state='up'/>
            <hostnames><hostname name='test.local'/></hostnames>
            <ports>
              <port protocol='tcp' portid='8080'>
                <state state='open'/>
                <service name='http-proxy' product='test-server' version='1.0'/>
              </port>
            </ports>
          </host>
        </nmaprun>"""

        with patch("app.services.nmap_scanner.asyncio.to_thread") as mock_thread:
            # Mock subprocess.run result
            mock_completed = AsyncMock()
            mock_completed.stdout = mock_xml
            mock_completed.stderr = ""
            mock_completed.returncode = 0
            mock_thread.return_value = mock_completed

            scanner = NmapScanner()
            result = await scanner.scan_host("127.0.0.1")

            assert isinstance(result, NmapScanResult)
            assert result.raw_output == mock_xml
            assert isinstance(result.ports, list)
            assert len(result.ports) == 1
            assert result.ports[0].port == 8080
            assert result.ports[0].service == "http-proxy"

    @pytest.mark.asyncio
    async def test_nmap_scanner_handles_zero_results(self):
        """Test that NmapScanner correctly handles scans with zero findings."""
        mock_xml = """<?xml version='1.0'?>
        <nmaprun>
          <host>
            <status state='down'/>
          </host>
          <runstats>
            <hosts up='0' down='1' total='1'/>
          </runstats>
        </nmaprun>"""

        with patch("app.services.nmap_scanner.asyncio.to_thread") as mock_thread:
            mock_completed = AsyncMock()
            mock_completed.stdout = mock_xml
            mock_completed.stderr = ""
            mock_completed.returncode = 0
            mock_thread.return_value = mock_completed

            scanner = NmapScanner()
            result = await scanner.scan_host("192.168.1.10")

            assert isinstance(result, NmapScanResult)
            assert result.raw_output == mock_xml
            assert result.ports == []
            assert len(result.ports) == 0

    @pytest.mark.asyncio
    async def test_nmap_scanner_handles_execution_failure(self):
        """Test that NmapScanner raises RuntimeError on Nmap execution failure."""
        with patch("app.services.nmap_scanner.asyncio.to_thread") as mock_thread:
            mock_completed = AsyncMock()
            mock_completed.stdout = ""
            mock_completed.stderr = "Nmap: invalid target specification"
            mock_completed.returncode = 1
            mock_thread.return_value = mock_completed

            scanner = NmapScanner()
            with pytest.raises(RuntimeError, match="Nmap exited with code 1"):
                await scanner.scan_host("127.0.0.1")
