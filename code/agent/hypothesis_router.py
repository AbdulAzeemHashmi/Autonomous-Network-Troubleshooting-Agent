"""
Phase 3: Hypothesis Router
Routes structured evidence records to candidate fault families with initial confidence ratings.
Grounding: SADE (Tseng et al., 2026) fault-family skill library and BiAn SOP heuristics.
"""

from typing import List, Dict, Any
from code.data.fault_family_index import lookup_symptom, FAULT_FAMILIES


class HypothesisRouter:
    """Translates anomalous evidence records into candidate fault hypotheses."""

    def route_hypotheses(
        self,
        device: str,
        evidence_records: List[Dict[str, Any]],
        ticket_text: str = ""
    ) -> List[Dict[str, Any]]:
        """Maps observed symptoms to fault families and specifies candidate falsification probes."""
        hypotheses = []
        seen_families = set()

        if not evidence_records:
            # If no anomalies in telemetry, candidate hypothesis is healthy
            return [{
                "fault_family": "healthy",
                "device": device,
                "initial_confidence": 0.95,
                "supporting_symptom": "All OSI layers (L2-Service) operating nominally",
                "proposed_falsification_probe": "none"
            }]

        for rec in evidence_records:
            symptom_desc = rec["symptom"]
            matches = lookup_symptom(symptom_desc)
            if not matches:
                # Text fallback matching
                matches = lookup_symptom(rec.get("raw_snippet", ""))

            for m in matches:
                fam = m["family"]
                if fam not in seen_families:
                    seen_families.add(fam)
                    # Determine probe command based on family
                    if fam == "link_failure":
                        probe_cmd = "show interface eth1"
                    elif fam == "congestion":
                        probe_cmd = "check_queue_drops"
                    elif fam == "routing_misconfiguration":
                        probe_cmd = "show ip route"
                    elif fam == "acl_firewall_block":
                        probe_cmd = "check_firewall_rules"
                    elif fam == "service_failure":
                        probe_cmd = "ss -tuln"
                    elif fam == "dns_failure":
                        probe_cmd = "dig api.internal.corp"
                    elif fam == "hardware_transceiver":
                        probe_cmd = "show interface errors"
                    else:
                        probe_cmd = "ping target"

                    hypotheses.append({
                        "fault_family": fam,
                        "device": device,
                        "initial_confidence": 0.70 if rec["severity"] == "high" else 0.50,
                        "supporting_symptom": rec["symptom"],
                        "evidence_snippet": rec.get("raw_snippet", ""),
                        "proposed_falsification_probe": probe_cmd
                    })

        # Fallback if symptom didn't match canonical dictionary
        if not hypotheses and evidence_records:
            hypotheses.append({
                "fault_family": "routing_misconfiguration",
                "device": device,
                "initial_confidence": 0.40,
                "supporting_symptom": evidence_records[0]["symptom"],
                "evidence_snippet": evidence_records[0].get("raw_snippet", ""),
                "proposed_falsification_probe": "show ip route"
            })

        return hypotheses

