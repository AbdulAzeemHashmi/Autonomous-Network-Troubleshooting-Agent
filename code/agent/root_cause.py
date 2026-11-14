"""
Phase 6: Root Cause Synthesis
Synthesizes verified evidence into a ranked list of root causes with calibrated confidence scores.
Grounding: BiAn (Wang et al., 2025) and RCLAgent (Zhang et al., 2026).
"""

import os
import json
from typing import List, Dict, Any, Optional


class RootCauseSynthesizer:
    """Produces the final ranked root-cause analysis."""

    def __init__(self, prompt_template_path: str = "prompts/phase6_root_cause.txt"):
        self.prompt_template_path = prompt_template_path
        self.prompt_template = ""
        if os.path.exists(prompt_template_path):
            try:
                with open(prompt_template_path, "r", encoding="utf-8") as f:
                    self.prompt_template = f.read()
            except Exception:
                self.prompt_template = ""

    def synthesize(
        self,
        surviving_hypotheses: List[Dict[str, Any]],
        abstain_result: Dict[str, Any],
        device: str,
        ticket_text: str = "",
        llm_client: Optional[Any] = None,
        use_llm: bool = False
    ) -> Dict[str, Any]:
        """Aggregates surviving hypotheses into ranked root causes."""
        if abstain_result.get("abstain", False):
            return {
                "detected": False,
                "localized_device": "none",
                "root_cause": "none",
                "confidence": 0.98,
                "ranked_causes": [],
                "reasoning_summary": abstain_result.get("reason", "No fault found on network.")
            }

        # Sort surviving hypotheses by descending confidence
        sorted_hyps = sorted(
            surviving_hypotheses,
            key=lambda x: x.get("updated_confidence", 0.0),
            reverse=True
        )

        ranked_causes = []
        for i, hyp in enumerate(sorted_hyps[:3]):
            ranked_causes.append({
                "rank": i + 1,
                "fault_family": hyp["fault_family"],
                "device": hyp.get("device", device),
                "confidence": round(hyp.get("updated_confidence", 0.0), 3),
                "evidence": hyp.get("falsification_reason") or hyp.get("supporting_symptom", "")
            })

        top_cause = ranked_causes[0] if ranked_causes else None

        # Check if live LLM synthesis should enhance the output
        if use_llm and llm_client and self.prompt_template:
            try:
                formatted_prompt = (
                    self.prompt_template
                    .replace("{ticket_text}", str(ticket_text))
                    .replace("{device}", str(device))
                    .replace("{surviving_hypotheses}", json.dumps(ranked_causes))
                )
                resp = llm_client.generate_json(formatted_prompt)
                parsed = resp.get("parsed_json", {})
                if parsed and "root_cause" in parsed:
                    return {
                        "detected": bool(parsed.get("detected", True)),
                        "localized_device": parsed.get("localized_device", top_cause["device"] if top_cause else device),
                        "root_cause": parsed.get("root_cause", top_cause["fault_family"] if top_cause else "unknown"),
                        "confidence": float(parsed.get("confidence", top_cause["confidence"] if top_cause else 0.5)),
                        "ranked_causes": parsed.get("ranked_causes", ranked_causes),
                        "reasoning_summary": parsed.get("reasoning_summary", "LLM-synthesized diagnosis.")
                    }
            except Exception:
                pass

        return {
            "detected": True,
            "localized_device": top_cause["device"] if top_cause else device,
            "root_cause": top_cause["fault_family"] if top_cause else "unknown",
            "confidence": top_cause["confidence"] if top_cause else 0.5,
            "ranked_causes": ranked_causes,
            "reasoning_summary": (
                f"Root cause identified as {top_cause['fault_family']} on device {top_cause['device']} "
                f"with confidence {top_cause['confidence']}. Evidence: {top_cause['evidence']}"
            ) if top_cause else "Uncertain diagnosis"
        }

