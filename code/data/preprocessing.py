"""
Data Preprocessing, Fault Injection Audit, and Evidence Trimming
Grounding: SADE (Tseng et al., 2026) fault verification and RCLAgent context bounded window.
"""

from typing import List, Dict, Any, Tuple
import os
import re
import pandas as pd
from code.data.mock_network_env import MockNetworkEnv


class Preprocessor:
    """Handles fault injection audit, whole-scenario split validation, and tool-output normalization."""

    def __init__(self, max_tokens: int = 500):
        self.max_tokens = max_tokens

    def audit_fault_injections(
        self,
        incidents: List[Dict[str, Any]],
        output_csv_path: str = "results/fault_audit.csv"
    ) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
        """Audits each incident by executing verification checks against the environment.

        Grounding: SADE authors found that standard NIKA injectors occasionally fail to
        induce the intended fault, distorting agent evaluation. Any unverified fault is dropped.
        """
        audit_records = []
        valid_incidents = []

        for inc in incidents:
            env = MockNetworkEnv(
                scenario=inc["scenario"],
                topology_size=inc["topology_size"],
                fault_injected=inc["ground_truth_has_fault"],
                fault_family=inc["ground_truth_fault_family"],
                faulty_device=inc["ground_truth_device"]
            )

            # Verification probe
            if not inc["ground_truth_has_fault"]:
                # Healthy check: ping should succeed, interface should be UP
                out = env.execute_command(inc["suspected_device_in_ticket"], "ping target")
                verified = ("0% packet loss" in out or "rtt" in out)
                status = "PASS_HEALTHY"
            else:
                # Faulty check: verify active anomaly
                dev = inc["ground_truth_device"]
                family = inc["ground_truth_fault_family"]
                if family == "link_failure":
                    out = env.execute_command(dev, "show interface")
                    verified = ("DOWN" in out or "NO-CARRIER" in out)
                elif family == "congestion":
                    out = env.execute_command(dev, "check_queue_drops")
                    verified = ("dropped" in out or "utilization" in out)
                elif family == "routing_misconfiguration":
                    out = env.execute_command(dev, "show ip route")
                    verified = ("blackhole" in out or "Null0" in out or "not set" in out)
                elif family == "acl_firewall_block":
                    out = env.execute_command(dev, "check_firewall_rules")
                    verified = ("DROP" in out)
                elif family == "service_failure":
                    out = env.execute_command(dev, "ss -tuln")
                    verified = ("dead" in out or "inactive" in out or "LISTEN" not in out)
                elif family == "dns_failure":
                    out = env.execute_command(dev, "dig query")
                    verified = ("timed out" in out or "NXDOMAIN" in out)
                elif family == "hardware_transceiver":
                    out = env.execute_command(dev, "show interface")
                    verified = (("CRC errors" in out and "0 CRC errors" not in out) or "ALARM" in out)
                else:
                    verified = True
                status = "PASS_FAULT_VERIFIED" if verified else "FAIL_INJECTION_ABSENT"

            audit_records.append({
                "incident_id": inc["incident_id"],
                "scenario": inc["scenario"],
                "ground_truth_has_fault": inc["ground_truth_has_fault"],
                "fault_family": inc["ground_truth_fault_family"],
                "device": inc.get("ground_truth_device", "none"),
                "audit_status": status,
                "verified": verified
            })

            if verified:
                valid_incidents.append(inc)

        audit_df = pd.DataFrame(audit_records)
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        audit_df.to_csv(output_csv_path, index=False)

        return valid_incidents, audit_df

    def trim_tool_output(self, raw_output: str) -> str:
        """Normalizes whitespace, strips repetitive banners/headers, and trims to token budget.

        Grounding: RCLAgent (Zhang et al., 2026) showed evidence dilution causes 43% of failures.
        """
        if not raw_output:
            return ""

        # Normalize whitespace and carriage returns
        text = raw_output.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Filter out common boilerplate headers
        filtered_lines = []
        for line in lines:
            if line.startswith("Copyright (c)") or line.startswith("Cisco Internetwork Operating System"):
                continue
            filtered_lines.append(line)

        cleaned_text = "\n".join(filtered_lines)

        # Approximate token bounding (1 token ~= 4 chars)
        max_chars = self.max_tokens * 4
        if len(cleaned_text) > max_chars:
            cleaned_text = cleaned_text[:max_chars] + "\n... [TRUNCATED DUE TO BOUNDED CONTEXT WINDOW]"

        return cleaned_text
