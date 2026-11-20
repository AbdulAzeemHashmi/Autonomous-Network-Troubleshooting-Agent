"""
Baseline 1: Zero-Shot LLM Agent
Grounding: Evaluates performance without active tool execution.
Receives the incident ticket and topology summary, guessing root cause and device directly using Gemini LLM.
"""

from typing import Dict, Any, Optional
import time
import re
from code.data.mock_network_env import MockNetworkEnv
from code.agent.llm_client import GeminiClient


class ZeroShotAgent:
    """Predicts root cause and device directly from ticket text without running diagnostic commands."""

    def __init__(
        self,
        cost_per_1k_input: float = 0.000075,
        cost_per_1k_output: float = 0.0003,
        llm_client: Optional[GeminiClient] = None,
        use_llm: bool = False
    ):
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        self.llm_client = llm_client
        self.use_llm = use_llm

    def troubleshoot(self, incident: Dict[str, Any], env: MockNetworkEnv) -> Dict[str, Any]:
        start_time = time.time()
        ticket_text = incident.get("ticket_text", "")
        nodes = env.topo.get_nodes()
        topo_summary = env.topo.summarize()

        input_tokens = len(ticket_text.split()) * 2 + 120
        output_tokens = 60

        predicted_cause = None
        suspected_device = None

        # Invoke Gemini LLM if live mode is enabled
        if self.use_llm and self.llm_client:
            prompt = (
                f"You are a network engineer performing zero-shot root cause analysis without tool access.\n"
                f"Ticket: {ticket_text}\n"
                f"Topology Summary: {topo_summary}\n\n"
                f"Choose the suspected device from: {nodes}\n"
                f"Choose the root cause from: [link_failure, congestion, routing_misconfiguration, "
                f"service_failure, acl_firewall_block, hardware_transceiver, dns_failure].\n"
                f"Output strictly JSON:\n"
                f"{{\"suspected_device\": \"device_name\", \"root_cause\": \"fault_family\", \"confidence\": 0.50}}"
            )
            resp = self.llm_client.generate_json(prompt)
            input_tokens = resp.get("input_tokens", input_tokens)
            output_tokens = resp.get("output_tokens", output_tokens)
            parsed = resp.get("parsed_json", {})
            if parsed.get("root_cause") and parsed.get("suspected_device"):
                predicted_cause = parsed["root_cause"]
                suspected_device = parsed["suspected_device"]

        # Deterministic fallback parsing if LLM not used or did not return valid JSON
        if not predicted_cause or not suspected_device:
            t_lower = ticket_text.lower()
            suspected_device = nodes[0] if nodes else "unknown"
            for n in sorted(nodes, key=len, reverse=True):
                if re.search(r'\b' + re.escape(n) + r'\b', t_lower, re.IGNORECASE):
                    suspected_device = n
                    break

            if "latency" in t_lower or "slow" in t_lower:
                predicted_cause = "congestion"
            elif "down" in t_lower or "carrier" in t_lower or "uncommunicative" in t_lower:
                predicted_cause = "link_failure"
            elif "route" in t_lower or "unreachable" in t_lower:
                predicted_cause = "routing_misconfiguration"
            elif "refused" in t_lower or "daemon" in t_lower:
                predicted_cause = "service_failure"
            elif "firewall" in t_lower or "acl" in t_lower or "block" in t_lower:
                predicted_cause = "acl_firewall_block"
            elif "crc" in t_lower or "transceiver" in t_lower or "optical" in t_lower:
                predicted_cause = "hardware_transceiver"
            elif "dns" in t_lower or "resolve" in t_lower:
                predicted_cause = "dns_failure"
            else:
                predicted_cause = "routing_misconfiguration"

        elapsed = time.time() - start_time
        cost_usd = (input_tokens / 1000.0) * self.cost_per_1k_input + (output_tokens / 1000.0) * self.cost_per_1k_output

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
