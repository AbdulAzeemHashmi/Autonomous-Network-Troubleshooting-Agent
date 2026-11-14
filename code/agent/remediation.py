"""
Phase 7: Optional Validated Remediation Stub
Proposes safe, minimal remediation plans guarded by pre-flight checks, rollback procedures, and human-in-the-loop gates.
Grounding: Confucius (Wang et al., SIGCOMM 2025) and NIKA mitigation open challenge.
"""

import os
from typing import Dict, Any, Optional

REMEDIATION_TEMPLATES = {
    "link_failure": {
        "action": "interface_restart",
        "command": "ip link set eth1 up",
        "pre_check": "ip link show eth1 | grep DOWN",
        "post_check": "ip link show eth1 | grep UP && ping -c 3 target",
        "rollback": "ip link set eth1 down",
        "risk_level": "low"
    },
    "congestion": {
        "action": "traffic_control_buffer_expansion",
        "command": "tc qdisc change dev eth0 root fq_codel limit 20480p",
        "pre_check": "tc -s qdisc show dev eth0 | grep dropped",
        "post_check": "tc -s qdisc show dev eth0 | grep -v 'dropped [1-9]'",
        "rollback": "tc qdisc change dev eth0 root fq_codel limit 10240p",
        "risk_level": "medium"
    },
    "routing_misconfiguration": {
        "action": "routing_fib_patch",
        "command": "ip route replace 10.0.2.0/24 via 10.0.0.2",
        "pre_check": "ip route show 10.0.2.0/24 | grep -E 'Null0|blackhole|unreachable'",
        "post_check": "ip route get 10.0.2.10 && ping -c 3 10.0.2.10",
        "rollback": "ip route del 10.0.2.0/24 via 10.0.0.2",
        "risk_level": "medium"
    },
    "acl_firewall_block": {
        "action": "firewall_rule_removal",
        "command": "iptables -D FORWARD -d 10.0.1.50 -j DROP",
        "pre_check": "iptables -L FORWARD -v -n | grep DROP",
        "post_check": "curl --connect-timeout 3 http://10.0.1.50:80",
        "rollback": "iptables -I FORWARD 1 -d 10.0.1.50 -j DROP",
        "risk_level": "medium"
    },
    "service_failure": {
        "action": "daemon_service_restart",
        "command": "systemctl restart nginx",
        "pre_check": "systemctl status nginx | grep -E 'failed|inactive'",
        "post_check": "systemctl is-active nginx && ss -tuln | grep :80",
        "rollback": "systemctl stop nginx",
        "risk_level": "low"
    },
    "dns_failure": {
        "action": "resolver_daemon_restart",
        "command": "systemctl restart systemd-resolved",
        "pre_check": "systemctl status systemd-resolved | grep inactive",
        "post_check": "dig @127.0.0.53 api.internal.corp +short",
        "rollback": "systemctl reload systemd-resolved",
        "risk_level": "low"
    },
    "hardware_transceiver": {
        "action": "transceiver_hardware_dispatch",
        "command": "ticket_hardware_team: Replace optical SFP+ transceiver module on eth1",
        "pre_check": "show interface eth1 transceiver | grep ALARM",
        "post_check": "show interface eth1 errors | grep 'CRC 0'",
        "rollback": "none (physical replacement)",
        "risk_level": "high"
    }
}


class RemediationPlanner:
    """Formulates guarded, human-approved remediation plans for confident diagnoses."""

    def __init__(
        self,
        confidence_threshold: float = 0.80,
        prompt_template_path: str = "prompts/phase7_remediation.txt"
    ):
        self.confidence_threshold = confidence_threshold
        self.prompt_template_path = prompt_template_path
        self.prompt_template = ""
        if os.path.exists(prompt_template_path):
            try:
                with open(prompt_template_path, "r", encoding="utf-8") as f:
                    self.prompt_template = f.read()
            except Exception:
                self.prompt_template = ""

    def plan_remediation(
        self,
        rca_result: Dict[str, Any],
        llm_client: Optional[Any] = None,
        use_llm: bool = False
    ) -> Dict[str, Any]:
        """Synthesizes a guarded remediation proposal."""
        if not rca_result.get("detected", False):
            return {
                "remediation_proposed": False,
                "reason": "Network verified healthy (abstain). No remediation action required.",
                "requires_human_approval": False
            }

        confidence = rca_result.get("confidence", 0.0)
        fault_family = rca_result.get("root_cause", "")
        device = rca_result.get("localized_device", "")

        if confidence < self.confidence_threshold:
            return {
                "remediation_proposed": False,
                "confidence_threshold_met": False,
                "reason": f"Confidence ({confidence:.2f}) below safe autonomous threshold ({self.confidence_threshold}). Escalating to human SME.",
                "requires_human_approval": True
            }

        # Check if live LLM generation should provide a customized remediation proposal
        if use_llm and llm_client and self.prompt_template:
            try:
                formatted_prompt = (
                    self.prompt_template
                    .replace("{root_cause}", str(fault_family))
                    .replace("{localized_device}", str(device))
                    .replace("{confidence}", str(confidence))
                    .replace("{evidence}", str(rca_result.get("reasoning_summary", "")))
                )
                resp = llm_client.generate_json(formatted_prompt)
                parsed = resp.get("parsed_json", {})
                if parsed and "action_type" in parsed:
                    return {
                        "remediation_proposed": bool(parsed.get("remediation_proposed", True)),
                        "confidence_threshold_met": True,
                        "fault_family": fault_family,
                        "target_device": device,
                        "action_type": parsed.get("action_type", "config_patch"),
                        "proposed_command": parsed.get("proposed_command", ""),
                        "pre_flight_check": parsed.get("pre_check", ""),
                        "post_flight_check": parsed.get("post_check", ""),
                        "rollback_procedure": parsed.get("rollback_command", ""),
                        "risk_level": parsed.get("risk_level", "medium"),
                        "requires_human_approval": True,
                        "executed_automatically": False,
                        "safety_note": "Remediation plan generated by Gemini LLM; awaiting human operator confirmation."
                    }
            except Exception:
                pass

        tmpl = REMEDIATION_TEMPLATES.get(fault_family)
        if not tmpl:
            return {
                "remediation_proposed": False,
                "reason": f"No pre-approved remediation playbook for fault family '{fault_family}'.",
                "requires_human_approval": True
            }

        return {
            "remediation_proposed": True,
            "confidence_threshold_met": True,
            "fault_family": fault_family,
            "target_device": device,
            "action_type": tmpl["action"],
            "proposed_command": tmpl["command"],
            "pre_flight_check": tmpl["pre_check"],
            "post_flight_check": tmpl["post_check"],
            "rollback_procedure": tmpl["rollback"],
            "risk_level": tmpl["risk_level"],
            "requires_human_approval": True,
            "executed_automatically": False,
            "safety_note": "Remediation plan generated but not executed; awaiting human operator confirmation."
        }

