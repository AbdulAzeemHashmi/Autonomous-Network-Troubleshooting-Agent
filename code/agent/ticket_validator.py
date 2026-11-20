"""
Phase 1: Ticket Validator
Validates whether the user ticket describes an authentic anomaly or represents an unreliable / false premise.
Grounding: FaulT-Bench (Tseng et al., 2026), Confucius (Wang et al., 2025) input vetting, and Gemini LLM Reasoning.
"""

from typing import Dict, Any, Optional
import os
import re
from code.data.mock_network_env import MockNetworkEnv
from code.agent.llm_client import GeminiClient


class TicketValidator:
    """Evaluates ticket assertions against preliminary reachability probes and Gemini LLM validation."""

    def __init__(self, preprocessor=None, llm_client: Optional[GeminiClient] = None, use_llm: bool = False):
        self.preprocessor = preprocessor
        self.llm_client = llm_client
        self.use_llm = use_llm
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "phase1_ticket_validator.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def validate(
        self,
        ticket_text: str,
        env: MockNetworkEnv,
        topology_summary: str
    ) -> Dict[str, Any]:
        """Probes the network to check whether ticket symptoms can be reproduced."""
        # Extract mentioned device or fallback to topology nodes
        nodes = env.topo.get_nodes()
        suspected_device = None
        for node in sorted(nodes, key=len, reverse=True):
            if re.search(r'\b' + re.escape(node) + r'\b', ticket_text, re.IGNORECASE):
                suspected_device = node
                break

        if not suspected_device:
            suspected_device = nodes[0] if nodes else "unknown"

        # Execute preliminary reachability and interface status checks
        ping_out = env.execute_command(suspected_device, "ping target")
        if self.preprocessor:
            ping_out = self.preprocessor.trim_tool_output(ping_out)

        if_out = env.execute_command(suspected_device, "show interface")
        if self.preprocessor:
            if_out = self.preprocessor.trim_tool_output(if_out)

        # Telemetry evaluation
        has_packet_loss = (
            "100% packet loss" in ping_out or
            "Destination" in ping_out or
            ("packet loss" in ping_out and "0% packet loss" not in ping_out)
        )
        has_latency_spike = False
        if "rtt min/avg/max" in ping_out:
            try:
                stats_line = [l for l in ping_out.split("\n") if "rtt min/avg/max" in l][0]
                avg_rtt = float(stats_line.split("=")[1].split("/")[1])
                has_latency_spike = (avg_rtt > 100.0)
            except Exception:
                pass

        interface_anomaly = (
            "is DOWN" in if_out or
            "line protocol is DOWN" in if_out or
            "NO-CARRIER" in if_out or
            ("CRC errors" in if_out and "0 CRC errors" not in if_out) or
            "ALARM" in if_out
        )

        telemetry_confirms_fault = has_packet_loss or has_latency_spike or interface_anomaly
        telemetry_snippet = f"--- ping ---\n{ping_out}\n--- show interface ---\n{if_out}"

        # If live LLM mode is active and client provided, invoke Gemini using safe string replacement
        llm_verdict = None
        if self.use_llm and self.llm_client and self.prompt_template:
            formatted_prompt = (
                self.prompt_template
                .replace("{ticket_text}", ticket_text)
                .replace("{topology_summary}", topology_summary)
                .replace("{preliminary_telemetry}", telemetry_snippet)
            )
            resp = self.llm_client.generate_json(formatted_prompt)
            if resp.get("parsed_json") and "ticket_valid" in resp["parsed_json"]:
                llm_verdict = resp["parsed_json"]

        if not telemetry_confirms_fault:
            reason = (
                f"Preliminary reachability probes on {suspected_device} showed 0% loss, "
                f"nominal latency, and UP interface state. Reported ticket symptoms could not be reproduced."
            )
            if llm_verdict and "reason" in llm_verdict:
                reason = f"{reason} Gemini LLM Verdict: {llm_verdict['reason']}"
            return {
                "ticket_valid": False,
                "suspected_device": suspected_device,
                "reason": reason,
                "preliminary_telemetry": {
                    "ping": ping_out,
                    "show_interface": if_out
                },
                "llm_evaluation": llm_verdict
            }

        reason = f"Preliminary telemetry on {suspected_device} corroborated ticket symptoms with active anomalies."
        if llm_verdict and "reason" in llm_verdict:
            reason = f"{reason} Gemini LLM Verdict: {llm_verdict['reason']}"

        return {
            "ticket_valid": True,
            "suspected_device": suspected_device,
            "reason": reason,
            "preliminary_telemetry": {
                "ping": ping_out,
                "show_interface": if_out
            },
            "llm_evaluation": llm_verdict
        }
