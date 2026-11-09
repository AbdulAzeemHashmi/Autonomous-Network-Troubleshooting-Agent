"""
Baseline 1: Zero-Shot LLM Agent
Grounding: Evaluates performance without active tool execution.
Receives the incident ticket and topology summary, guessing root cause and device directly.
"""

from typing import Dict, Any
import time
from code.data.mock_network_env import MockNetworkEnv


class ZeroShotAgent:
    """Predicts root cause and device directly from ticket text without running diagnostic commands."""

    def __init__(self, cost_per_1k_input: float = 0.003, cost_per_1k_output: float = 0.015):
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output

    def troubleshoot(self, incident: Dict[str, Any], env: MockNetworkEnv) -> Dict[str, Any]:
        start_time = time.time()
        ticket_text = incident.get("ticket_text", "").lower()
        nodes = env.topo.get_nodes()

        # Input and output token approximations
        input_tokens = len(ticket_text.split()) * 2 + 120
        output_tokens = 60

        # Heuristic zero-shot parsing of ticket claims
        suspected_device = nodes[0] if nodes else "unknown"
        for n in nodes:
            if n.lower() in ticket_text:
                suspected_device = n
                break

        # Without tools, zero-shot believes whatever the ticket says (prone to false alarms on healthy networks)
        if "latency" in ticket_text or "slow" in ticket_text:
            predicted_cause = "congestion"
        elif "down" in ticket_text or "carrier" in ticket_text or "uncommunicative" in ticket_text:
            predicted_cause = "link_failure"
        elif "route" in ticket_text or "unreachable" in ticket_text:
            predicted_cause = "routing_misconfiguration"
        elif "refused" in ticket_text or "daemon" in ticket_text:
            predicted_cause = "service_failure"
        elif "firewall" in ticket_text or "acl" in ticket_text or "block" in ticket_text:
            predicted_cause = "acl_firewall_block"
        elif "crc" in ticket_text or "transceiver" in ticket_text or "optical" in ticket_text:
            predicted_cause = "hardware_transceiver"
        elif "dns" in ticket_text or "resolve" in ticket_text:
            predicted_cause = "dns_failure"
        else:
            predicted_cause = "routing_misconfiguration"

        elapsed = time.time() - start_time
        cost_usd = (input_tokens / 1000.0) * self.cost_per_1k_input + (output_tokens / 1000.0) * self.cost_per_1k_output

        # Zero-shot has no verification tool, so it always reports a fault (never abstains)
        return {
            "detected": True,
            "localized_device": suspected_device,
            "root_cause": predicted_cause,
            "confidence": 0.50,
            "ranked_causes": [{"rank": 1, "fault_family": predicted_cause, "device": suspected_device, "confidence": 0.50}],
            "remediation": {"remediation_proposed": False, "reason": "Zero-shot cannot validate remediation."},
            "abstain_invoked": False,
            "turns_used": 1,
            "time_seconds": round(elapsed, 4),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost_usd, 6),
            "no_submission": False,
            "trace_logs": [{"turn": 1, "action": "zero_shot_inference", "predicted_cause": predicted_cause}],
            "ticket_valid": True
        }
