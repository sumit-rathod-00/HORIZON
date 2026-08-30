from app.services.nmap_scanner import NmapScanner


def test_parse_nmap_xml_extracts_service_details() -> None:
    xml = """<?xml version='1.0'?>
    <nmaprun>
      <host>
        <hostnames><hostname name='localhost'/></hostnames>
        <ports>
          <port protocol='tcp' portid='5432'>
            <state state='open'/>
            <service name='postgresql' product='PostgreSQL DB' version='17.0'/>
          </port>
        </ports>
      </host>
    </nmaprun>"""

    results = NmapScanner._parse_xml(xml)

    assert len(results) == 1
    result = results[0]
    assert result.port == 5432
    assert result.protocol == "tcp"
    assert result.state == "open"
    assert result.service == "postgresql"
    assert result.product == "PostgreSQL DB"
    assert result.version == "17.0"
    assert result.hostname == "localhost"
