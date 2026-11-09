"""
Phase 1: Ticket Validator
Validates whether the user ticket describes an authentic anomaly or represents an unreliable / false premise.
Grounding: FaulT-Bench (Tseng et al., 2026) and Confucius (Wang et al., 2025) input vetting.
"""

from typing import Dict, Any
import re
from code.data.mock_network_env import MockNetworkEnv


class TicketValidator:
    """Evaluates ticket assertions against preliminary reachability probes."""

    def __init__(self, preprocessor=None):
        self.preprocessor = preprocessor

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
        for node in nodes:
            if node.lower() in ticket_text.lower():
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
        has_packet_loss = ("100% packet loss" in ping_out or "Destination" in ping_out or ("packet loss" in ping_out and "0% packet loss" not in ping_out))
        has_latency_spike = any(f"time={ms}" in ping_out for ms in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]) and ("time=0." not in ping_out and "time=1." not in ping_out and "time=2." not in ping_out and "time=3." not in ping_out and "time=4." not in ping_out and "time=5." not in ping_out) and ("rtt avg" in ping_out or "mdev" in ping_out)
        # Check explicit high RTT in statistics
        if "rtt min/avg/max" in ping_out:
            try:
                # e.g. rtt min/avg/max/mdev = 312.4/370.2/428.1/57.8 ms
                stats_line = [l for l in ping_out.split("\n") if "rtt min/avg/max" in l][0]
                avg_rtt = float(stats_line.split("=")[1].split("/")[1])
                has_latency_spike = (avg_rtt > 100.0)
            except Exception:
                pass
        interface_anomaly = ("DOWN" in if_out or "NO-CARRIER" in if_out or "CRC errors" in if_out)

        telemetry_confirms_fault = has_packet_loss or has_latency_spike or interface_anomaly

        if not telemetry_confirms_fault:
            return {
                "ticket_valid": False,
                "suspected_device": suspected_device,
                "reason": (
                    f"Preliminary reachability probes on {suspected_device} showed 0% loss, "
                    f"nominal latency, and UP interface state. Reported ticket symptoms could not be reproduced."
                ),
                "preliminary_telemetry": {
                    "ping": ping_out,
                    "show_interface": if_out
                }
            }

        return {
            "ticket_valid": True,
            "suspected_device": suspected_device,
            "reason": f"Preliminary telemetry on {suspected_device} corroborated ticket symptoms with active anomalies.",
            "preliminary_telemetry": {
                "ping": ping_out,
                "show_interface": if_out
            }
        }
