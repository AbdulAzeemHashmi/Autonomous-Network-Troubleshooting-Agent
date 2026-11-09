"""
Fault Family Index
Maps observed symptoms and OSI layer anomalies to standardized network fault families.
Grounding: SADE (Tseng et al., 2026) fault index and classic Cisco escalation tiers.
"""

from typing import Dict, List, Any

# Canonical fault families supported across NIKA and FaulT-Bench
FAULT_FAMILIES = [
    "link_failure",
    "congestion",
    "routing_misconfiguration",
    "acl_firewall_block",
    "dns_failure",
    "service_failure",
    "hardware_transceiver",
    "healthy"
]

# Explicit symptom-to-family heuristic dictionary
SYMPTOM_MAP: Dict[str, Dict[str, Any]] = {
    "interface_down": {
        "family": "link_failure",
        "layer": "L2",
        "indicators": ["line protocol is down", "state down", "carrier lost", "no-carrier", "link down", "interface eth1 is down", "down / carrier lost"],
        "default_falsification_tool": "show_interface"
    },
    "crc_errors": {
        "family": "hardware_transceiver",
        "layer": "L2",
        "indicators": ["crc errors", "input errors", "runts", "giants", "frame errors", "optical transceiver", "optical power alarm"],
        "default_falsification_tool": "show_interface_errors"
    },
    "packet_loss_high_latency": {
        "family": "congestion",
        "layer": "L3",
        "indicators": ["packet loss", "queue drops", "buffer overrun", "latency inflation", "rtt", "excessive latency", "tail drop"],
        "default_falsification_tool": "check_queue_drops"
    },
    "route_missing": {
        "family": "routing_misconfiguration",
        "layer": "L3",
        "indicators": ["network unreachable", "destination host unreachable", "destination net unreachable", "no route to host", "blackhole", "null0", "bgp idle"],
        "default_falsification_tool": "show_ip_route"
    },
    "traffic_filtered": {
        "family": "acl_firewall_block",
        "layer": "L3",
        "indicators": ["packet filtered", "administratively prohibited", "administratively filtered", "acl firewall", "drop counter > 0", "tcp syn dropped"],
        "default_falsification_tool": "check_firewall_rules"
    },
    "dns_nxdomain": {
        "family": "dns_failure",
        "layer": "service",
        "indicators": ["nxdomain", "server failure", "servfail", "dns resolution", "no servers could be reached"],
        "default_falsification_tool": "query_dns"
    },
    "port_closed": {
        "family": "service_failure",
        "layer": "L4",
        "indicators": ["connection refused", "daemon stopped", "dead/inactive", "dead in status", "socket not listening", "service socket not listening"],
        "default_falsification_tool": "check_socket_status"
    }
}


def lookup_symptom(text: str) -> List[Dict[str, Any]]:
    """Scan raw or summarized text and match against known symptom indicators."""
    lower_text = text.lower()
    matches = []
    for symptom_key, meta in SYMPTOM_MAP.items():
        for indicator in meta["indicators"]:
            if indicator.lower() in lower_text:
                # Discard zero-error matches
                if symptom_key == "crc_errors" and "0 crc errors" in lower_text and not any(k in lower_text for k in ["runts", "giants", "frame errors", "alarm"]):
                    continue
                if symptom_key == "interface_down" and "line protocol is up" in lower_text and "down" not in lower_text.replace("line protocol is up", ""):
                    continue
                matches.append({
                    "symptom_key": symptom_key,
                    "family": meta["family"],
                    "layer": meta["layer"],
                    "matched_indicator": indicator,
                    "falsification_tool": meta["default_falsification_tool"]
                })
                break
    return matches
