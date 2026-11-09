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
        "indicators": ["line protocol is down", "state DOWN", "carrier lost", "NO-CARRIER", "link down"],
        "default_falsification_tool": "show_interface"
    },
    "crc_errors": {
        "family": "hardware_transceiver",
        "layer": "L2",
        "indicators": ["CRC errors", "input errors", "runts", "giants", "frame errors"],
        "default_falsification_tool": "show_interface_errors"
    },
    "packet_loss_high_latency": {
        "family": "congestion",
        "layer": "L3",
        "indicators": ["packet loss > 15%", "queue drops", "buffer overrun", "rtt > 250ms", "tail drop"],
        "default_falsification_tool": "check_queue_drops"
    },
    "route_missing": {
        "family": "routing_misconfiguration",
        "layer": "L3",
        "indicators": ["Network unreachable", "Destination Host Unreachable", "no route to host", "BGP idle", "OSPF init"],
        "default_falsification_tool": "show_ip_route"
    },
    "traffic_filtered": {
        "family": "acl_firewall_block",
        "layer": "L3",
        "indicators": ["Packet filtered", "administratively prohibited", "TCP SYN dropped", "drop counter > 0"],
        "default_falsification_tool": "check_firewall_rules"
    },
    "dns_nxdomain": {
        "family": "dns_failure",
        "layer": "service",
        "indicators": ["NXDOMAIN", "server failure", "connection timed out; no servers could be reached"],
        "default_falsification_tool": "query_dns"
    },
    "port_closed": {
        "family": "service_failure",
        "layer": "L4",
        "indicators": ["Connection refused", "daemon stopped", "dead in status", "socket not listening"],
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
                matches.append({
                    "symptom_key": symptom_key,
                    "family": meta["family"],
                    "layer": meta["layer"],
                    "matched_indicator": indicator,
                    "falsification_tool": meta["default_falsification_tool"]
                })
                break
    return matches
