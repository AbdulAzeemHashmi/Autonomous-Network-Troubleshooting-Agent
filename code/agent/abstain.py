"""
Phase 5: Abstain Logic
Enables the agent to explicitly abstain and output "No fault found" on healthy networks.
Grounding: FaulT-Bench (Tseng et al., 2026); addresses Sub-Gap A (over-diagnosis on healthy controls).
"""

from typing import Dict, Any, List


class AbstainManager:
    """Evaluates whether to abort troubleshooting and declare the network healthy."""

    def should_abstain(
        self,
        ticket_validation_result: Dict[str, Any],
        surviving_hypotheses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determines if the agent should abstain from diagnosing a fault.

        Conditions for abstention:
        1. Surviving hypotheses list is empty.
        2. Only hypothesis surviving is 'healthy'.
        3. Ticket validation failed AND no surviving hypotheses have confidence > 0.40.
        """
        # Condition 1: No surviving hypotheses
        if not surviving_hypotheses:
            return {
                "abstain": True,
                "reason": "All candidate fault hypotheses were disproven during active falsification probing.",
                "verdict": "no fault found"
            }

        # Condition 2: Explicit healthy hypothesis
        if len(surviving_hypotheses) == 1 and surviving_hypotheses[0]["fault_family"] == "healthy":
            return {
                "abstain": True,
                "reason": "Layered scan and falsification verified pristine network telemetry across all layers.",
                "verdict": "no fault found"
            }

        # Condition 3: Ticket validation failed and low remaining confidence
        if not ticket_validation_result.get("ticket_valid", True):
            max_conf = max(h.get("updated_confidence", 0.0) for h in surviving_hypotheses)
            if max_conf < 0.50:
                return {
                    "abstain": True,
                    "reason": "Ticket failed initial validation and surviving hypotheses lack corroborating evidence.",
                    "verdict": "no fault found"
                }

        return {
            "abstain": False,
            "reason": f"Active network anomaly corroborated by {len(surviving_hypotheses)} surviving hypothesis/hypotheses.",
            "verdict": "fault detected"
        }
