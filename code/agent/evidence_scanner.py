"""
Phase 2: Layered Evidence Scanner
Executes a structured progression of diagnostic probes from L2 through Service layer.
Grounding: SADE (Tseng et al., 2026) Cisco layer-by-layer methodology.
"""

from typing import Dict, List, Any
from code.data.mock_network_env import MockNetworkEnv
from code.data.preprocessing import Preprocessor


class EvidenceScanner:
    """Orchestrates structured OSI-layer telemetry gathering."""

    def __init__(self, preprocessor: Preprocessor = None):
        self.preprocessor = preprocessor or Preprocessor(max_tokens=500)

    def scan_layers(self, device: str, env: MockNetworkEnv) -> Dict[str, Any]:
        """Scans L2, L3, L4, and Service layers on the specified device and extracts evidence."""
        raw_outputs = {}
        evidence_records: List[Dict[str, Any]] = []

        # -----------------------------------------------------------------
        # Layer 2: Data Link Layer
        # -----------------------------------------------------------------
        if_out = env.execute_command(device, "show interface")
        raw_outputs["L2_show_interface"] = self.preprocessor.trim_tool_output(if_out)
        if "DOWN" in if_out or "NO-CARRIER" in if_out:
            evidence_records.append({
                "layer": "L2",
                "symptom": "Interface line protocol down / carrier lost",
                "severity": "high",
                "raw_snippet": "Interface eth1 is DOWN, line protocol is DOWN (NO-CARRIER)"
            })
        elif ("CRC errors" in if_out and "0 CRC errors" not in if_out) or "ALARM" in if_out:
            evidence_records.append({
                "layer": "L2",
                "symptom": "High CRC errors / optical transceiver degradation",
                "severity": "high",
                "raw_snippet": "48291 CRC errors, Rx optical power alarm low"
            })

        mac_out = env.execute_command(device, "show mac address-table")
        raw_outputs["L2_show_mac"] = self.preprocessor.trim_tool_output(mac_out)

        # -----------------------------------------------------------------
        # Layer 3: Network Layer
        # -----------------------------------------------------------------
        ping_out = env.execute_command(device, "ping target")
        raw_outputs["L3_ping"] = self.preprocessor.trim_tool_output(ping_out)
        if "Packet filtered" in ping_out or "Destination Host Prohibited" in ping_out:
            evidence_records.append({
                "layer": "L3",
                "symptom": "Traffic administratively filtered by ACL firewall",
                "severity": "high",
                "raw_snippet": "Packet filtered (Destination Host Prohibited)"
            })
        elif "100% packet loss" in ping_out or "Destination Net Unreachable" in ping_out:
            evidence_records.append({
                "layer": "L3",
                "symptom": "Total packet loss / destination unreachable",
                "severity": "high",
                "raw_snippet": "Destination Net Unreachable (100% loss)"
            })
        elif ("packet loss" in ping_out and "0% packet loss" not in ping_out) or "time=312" in ping_out:
            evidence_records.append({
                "layer": "L3",
                "symptom": "Severe packet loss and latency inflation (>300ms)",
                "severity": "high",
                "raw_snippet": "Packet loss and high RTT latency"
            })

        route_out = env.execute_command(device, "show ip route")
        raw_outputs["L3_show_ip_route"] = self.preprocessor.trim_tool_output(route_out)
        if "blackhole" in route_out or "Null0" in route_out:
            evidence_records.append({
                "layer": "L3",
                "symptom": "Anomalous route entry or blackhole null route",
                "severity": "medium",
                "raw_snippet": "10.0.2.0/24 via Null0 (blackhole misconfiguration)"
            })

        # -----------------------------------------------------------------
        # Layer 4: Transport Layer
        # -----------------------------------------------------------------
        ss_out = env.execute_command(device, "ss -tuln")
        raw_outputs["L4_ss"] = self.preprocessor.trim_tool_output(ss_out)
        if "dead" in ss_out or "inactive" in ss_out:
            evidence_records.append({
                "layer": "L4",
                "symptom": "Required service socket not listening on expected port",
                "severity": "high",
                "raw_snippet": "Process on port 80/443 (nginx) is dead/inactive"
            })

        # -----------------------------------------------------------------
        # Service / Application Layer
        # -----------------------------------------------------------------
        curl_out = env.execute_command(device, "curl http://localhost")
        raw_outputs["Service_curl"] = self.preprocessor.trim_tool_output(curl_out)
        if "Connection refused" in curl_out:
            evidence_records.append({
                "layer": "service",
                "symptom": "TCP connection refused on application port",
                "severity": "high",
                "raw_snippet": "curl: (7) Failed to connect to port 80: Connection refused"
            })
        elif "Connection timed out" in curl_out:
            evidence_records.append({
                "layer": "service",
                "symptom": "Application connection timed out / traffic filtered",
                "severity": "high",
                "raw_snippet": "curl: (28) Connection timed out"
            })

        dns_out = env.execute_command(device, "dig api.internal.corp")
        raw_outputs["Service_dns"] = self.preprocessor.trim_tool_output(dns_out)
        if "timed out" in dns_out or "NXDOMAIN" in dns_out or "SERVFAIL" in dns_out:
            evidence_records.append({
                "layer": "service",
                "symptom": "DNS resolution failure / SERVFAIL",
                "severity": "medium",
                "raw_snippet": ";; connection timed out; Got SERVFAIL / NXDOMAIN"
            })

        return {
            "device": device,
            "evidence_records": evidence_records,
            "raw_outputs": raw_outputs,
            "anomalies_detected": len(evidence_records) > 0
        }
