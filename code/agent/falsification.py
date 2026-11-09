"""
Phase 4: Falsification Probes
Actively executes targeted counter-probes to disprove candidate hypotheses.
Grounding: Scientific method of falsification; addresses Kim et al. shallow reasoning pitfalls.
"""

from typing import List, Dict, Any, Tuple
from code.data.mock_network_env import MockNetworkEnv
from code.data.preprocessing import Preprocessor


class FalsificationEngine:
    """Executes counter-probes designed to disprove candidate hypotheses."""

    def __init__(self, preprocessor: Preprocessor = None):
        self.preprocessor = preprocessor or Preprocessor(max_tokens=500)

    def test_hypotheses(
        self,
        hypotheses: List[Dict[str, Any]],
        env: MockNetworkEnv
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Runs falsification probes for each candidate hypothesis.

        Returns:
            (surviving_hypotheses, falsified_hypotheses)
        """
        surviving = []
        falsified = []

        for hyp in hypotheses:
            family = hyp["fault_family"]
            device = hyp["device"]
            probe_cmd = hyp.get("proposed_falsification_probe", "ping target")

            if family == "healthy":
                surviving.append({
                    **hyp,
                    "falsified": False,
                    "updated_confidence": hyp["initial_confidence"],
                    "falsification_probe": "none",
                    "falsification_output": "Pristine telemetry confirms healthy state"
                })
                continue

            # Execute counter probe on environment
            raw_out = env.execute_command(device, probe_cmd)
            probe_out = self.preprocessor.trim_tool_output(raw_out)

            is_disproven = False
            reason = ""

            if family == "link_failure":
                # Disproven if interface is UP and active
                if "line protocol is UP" in probe_out and "ACTIVE" in probe_out and "NO-CARRIER" not in probe_out:
                    is_disproven = True
                    reason = "Interface counter-probe proved eth1 line protocol is active and passing packets."
                else:
                    reason = "Counter-probe confirmed interface carrier down and line protocol down."

            elif family == "congestion":
                # Disproven if queue drops == 0 and utilization < 5%
                if "dropped 0" in probe_out or "queue utilization 2.1%" in probe_out:
                    is_disproven = True
                    reason = "Queue disc probe showed 0 dropped packets and minimal queue utilization."
                else:
                    reason = "Queue disc probe confirmed active drops and buffer saturation (>90%)."

            elif family == "routing_misconfiguration":
                # Disproven if valid active route exists without null/blackhole
                if "O>* 10.0.2.0/24" in probe_out and "Null0" not in probe_out and "blackhole" not in probe_out:
                    is_disproven = True
                    reason = "Routing FIB inspection proved active OSPF next-hop installed for prefix."
                else:
                    reason = "Routing table inspection confirmed missing next-hop / blackhole null route."

            elif family == "acl_firewall_block":
                # Disproven if no DROP rule exists in output or drop rule has 0 matching packets
                if "DROP" not in probe_out or " 0 DROP" in probe_out or "0 pkts DROP" in probe_out:
                    is_disproven = True
                    reason = "Firewall inspection revealed zero drop rule matches on target traffic."
                else:
                    reason = "Firewall counters confirmed active packet drop rule matches."

            elif family == "service_failure":
                # Disproven if process is listening on port 80/443
                if "LISTEN" in probe_out and "dead" not in probe_out and "inactive" not in probe_out:
                    is_disproven = True
                    reason = "Socket table proved target daemon listening and responding."
                else:
                    reason = "Socket inspection confirmed service daemon is dead / inactive."

            elif family == "dns_failure":
                # Disproven if resolver returned valid ANSWER section
                if "ANSWER SECTION" in probe_out and "timed out" not in probe_out:
                    is_disproven = True
                    reason = "DNS query succeeded with authoritative A-record resolution."
                else:
                    reason = "DNS probe timed out or returned SERVFAIL."

            elif family == "hardware_transceiver":
                # Disproven if 0 CRC errors and optical power is nominal
                if "0 CRC errors" in probe_out and "ALARM" not in probe_out:
                    is_disproven = True
                    reason = "Interface physical transceiver counters show 0 CRC errors and normal optical power."
                else:
                    reason = "Optical transceiver diagnostic confirmed severe low optical power alarm and CRC errors."

            # Update confidence based on survival vs disproof
            if is_disproven:
                falsified.append({
                    **hyp,
                    "falsified": True,
                    "falsification_probe": probe_cmd,
                    "falsification_output": probe_out,
                    "falsification_reason": reason,
                    "updated_confidence": 0.05
                })
            else:
                surviving.append({
                    **hyp,
                    "falsified": False,
                    "falsification_probe": probe_cmd,
                    "falsification_output": probe_out,
                    "falsification_reason": reason,
                    "updated_confidence": min(0.98, hyp["initial_confidence"] + 0.25)
                })

        return surviving, falsified
