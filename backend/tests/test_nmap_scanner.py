import pytest

from app.services.nmap_scanner import NmapScanner


def test_parse_empty_scan_zero_hosts_up() -> None:
    """Test parsing Nmap output when target is down (0 hosts up)."""
    xml = """<?xml version='1.0'?>
    <nmaprun>
      <host>
        <status state='down'/>
      </host>
      <runstats>
        <hosts up='0' down='1' total='1'/>
      </runstats>
    </nmaprun>"""

    results = NmapScanner._parse_xml(xml)

    assert results == []
    assert len(results) == 0


def test_parse_host_up_no_open_ports() -> None:
    """Test parsing Nmap output when host is up but has no open ports."""
    xml = """<?xml version='1.0'?>
    <nmaprun>
      <host>
        <status state='up'/>
        <hostnames><hostname name='test.local'/></hostnames>
        <ports></ports>
      </host>
    </nmaprun>"""

    results = NmapScanner._parse_xml(xml)

    assert results == []
    assert len(results) == 0


def test_parse_host_with_closed_ports_only() -> None:
    """Test parsing when ports exist but are all closed/filtered."""
    xml = """<?xml version='1.0'?>
    <nmaprun>
      <host>
        <status state='up'/>
        <ports>
          <port protocol='tcp' portid='22'>
            <state state='closed'/>
          </port>
          <port protocol='tcp' portid='80'>
            <state state='filtered'/>
          </port>
        </ports>
      </host>
    </nmaprun>"""

    results = NmapScanner._parse_xml(xml)

    # Parser includes all ports with state info
    assert len(results) == 2
    assert results[0].port == 22
    assert results[0].state == "closed"
    assert results[1].port == 80
    assert results[1].state == "filtered"


def test_parse_multiple_open_ports() -> None:
    """Test parsing multiple open ports with service details."""
    xml = """<?xml version='1.0'?>
    <nmaprun>
      <host>
        <status state='up'/>
        <hostnames><hostname name='example.com'/></hostnames>
        <ports>
          <port protocol='tcp' portid='22'>
            <state state='open'/>
            <service name='ssh' product='OpenSSH' version='8.2p1'/>
          </port>
          <port protocol='tcp' portid='80'>
            <state state='open'/>
            <service name='http' product='nginx' version='1.18.0'/>
          </port>
          <port protocol='tcp' portid='443'>
            <state state='open'/>
            <service name='https' product='nginx' version='1.18.0'/>
          </port>
        </ports>
      </host>
    </nmaprun>"""

    results = NmapScanner._parse_xml(xml)

    assert len(results) == 3
    assert results[0].port == 22
    assert results[0].service == "ssh"
    assert results[0].product == "OpenSSH"
    assert results[0].hostname == "example.com"
    assert results[1].port == 80
    assert results[1].service == "http"
    assert results[2].port == 443


def test_parse_port_without_service_info() -> None:
    """Test parsing port with state but no service detection."""
    xml = """<?xml version='1.0'?>
    <nmaprun>
      <host>
        <ports>
          <port protocol='tcp' portid='8080'>
            <state state='open'/>
          </port>
        </ports>
      </host>
    </nmaprun>"""

    results = NmapScanner._parse_xml(xml)

    assert len(results) == 1
    assert results[0].port == 8080
    assert results[0].protocol == "tcp"
    assert results[0].state == "open"
    assert results[0].service is None
    assert results[0].product is None
    assert results[0].version is None
    assert results[0].hostname is None


def test_parse_invalid_xml_raises_error() -> None:
    """Test that malformed XML raises RuntimeError."""
    invalid_xml = "This is not XML at all"

    with pytest.raises(RuntimeError, match="invalid structured output"):
        NmapScanner._parse_xml(invalid_xml)


def test_parse_port_without_state_node_skipped() -> None:
    """Test that ports without state node are skipped."""
    xml = """<?xml version='1.0'?>
    <nmaprun>
      <host>
        <ports>
          <port protocol='tcp' portid='9999'>
            <service name='unknown'/>
          </port>
        </ports>
      </host>
    </nmaprun>"""

    results = NmapScanner._parse_xml(xml)

    assert len(results) == 0


def test_parse_port_without_portid_skipped() -> None:
    """Test that ports without portid attribute are skipped."""
    xml = """<?xml version='1.0'?>
    <nmaprun>
      <host>
        <ports>
          <port protocol='tcp'>
            <state state='open'/>
          </port>
        </ports>
      </host>
    </nmaprun>"""

    results = NmapScanner._parse_xml(xml)

    assert len(results) == 0


def test_validate_target_valid_ipv4() -> None:
    """Test target validation accepts valid IPv4."""
    NmapScanner._validate_target("192.168.1.1")
    NmapScanner._validate_target("10.0.0.1")
    NmapScanner._validate_target("  127.0.0.1  ")  # with whitespace


def test_validate_target_valid_ipv6() -> None:
    """Test target validation accepts valid IPv6."""
    NmapScanner._validate_target("::1")
    NmapScanner._validate_target("2001:db8::1")


def test_validate_target_rejects_hostname() -> None:
    """Test target validation rejects hostnames."""
    with pytest.raises(ValueError, match="Invalid scan target"):
        NmapScanner._validate_target("example.com")


def test_validate_target_rejects_cidr() -> None:
    """Test target validation rejects CIDR ranges."""
    with pytest.raises(ValueError, match="Invalid scan target"):
        NmapScanner._validate_target("192.168.1.0/24")


def test_validate_target_rejects_invalid_input() -> None:
    """Test target validation rejects malformed input."""
    with pytest.raises(ValueError, match="Invalid scan target"):
        NmapScanner._validate_target("not-an-ip")

    with pytest.raises(ValueError, match="Invalid scan target"):
        NmapScanner._validate_target("")
