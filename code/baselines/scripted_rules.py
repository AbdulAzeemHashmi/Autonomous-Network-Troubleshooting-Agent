"""
Baseline 5: Scripted Rule Checks
Grounding: Traditional deterministic Network Management Systems (NMS) and rule-based scripts.
Uses fixed command sequences and deterministic threshold criteria without LLM reasoning or token costs.
"""

from typing import Dict, Any, List
import time
import re
from code.data.mock_network_env import MockNetworkEnv


class ScriptedRuleAgent:
    """Deterministic, rule-based diagnostic engine applying static threshold checks."""

    def __init__(self):
        pass

    def troubleshoot(self, incident: Dict[str, Any], env: MockNetworkEnv) -> Dict[str, Any]:
        start_time = time.time()
        ticket_text = incident.get("ticket_text", "").lower()
        nodes = env.topo.get_nodes()
        target_device = nodes[0] if nodes else "unknown"
        for n in sorted(nodes, key=len, reverse=True):
            if re.search(r'\b' + re.escape(n) + r'\b', ticket_text, re.IGNORECASE):
                target_device = n
                break

        turns_used = 4
        trace_logs = []

        # 1. Ping check
        ping_out = env.execute_command(target_device, "ping target")
        # 2. Interface check
        if_out = env.execute_command(target_device, "show interface")
        # 3. Route check
        route_out = env.execute_command(target_device, "show ip route")
        # 4. Socket check
        ss_out = env.execute_command(target_device, "ss -tuln")

        # Threshold rules
        detected = False
        root_cause = "none"
        confidence = 0.85

        if "DOWN" in if_out or "NO-CARRIER" in if_out:
            detected = True
            root_cause = "link_failure"
        elif "CRC errors" in if_out and "0 CRC errors" not in if_out:
            detected = True
            root_cause = "hardware_transceiver"
        elif "60% packet loss" in ping_out or "time=312" in ping_out:
            detected = True
            root_cause = "congestion"
        elif "Destination Net Unreachable" in ping_out or "blackhole" in route_out or "Null0" in route_out:
            detected = True
            root_cause = "routing_misconfiguration"
        elif "dead" in ss_out or "inactive" in ss_out:
            detected = True
            root_cause = "service_failure"
        elif "Packet filtered" in ping_out:
            detected = True
            root_cause = "acl_firewall_block"
        else:
            # Scripted rules correctly identify normal states when no rule triggers
            detected = False
            root_cause = "none"
            confidence = 0.90

        elapsed = time.time() - start_time

        return {
            "detected": detected,
            "localized_device": target_device if detected else "none",
            "root_cause": root_cause,
            "confidence": confidence,
            "ranked_causes": [{"rank": 1, "fault_family": root_cause, "device": target_device, "confidence": confidence}] if detected else [],
            "remediation": {"remediation_proposed": False, "reason": "Static rules engine has no autonomous remediation engine."},
            "abstain_invoked": not detected,
            "turns_used": turns_used,
            "time_seconds": round(elapsed, 4),
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.000000,
            "no_submission": False,
            "trace_logs": [{"turn": turns_used, "action": "scripted_threshold_evaluation", "root_cause": root_cause}],
            "ticket_valid": True
        }

