"""
Comprehensive Experimental Runner
Grounding: Phase 2 Step 7 (Experimental Design) and Step 8 (Evaluation Metrics).
Runs proposed agent and all 5 baselines across scenarios, topologies, and seeds,
supporting both Gemini LLM live evaluation and fast deterministic simulation.
"""

from typing import List, Dict, Any, Optional
import os
import yaml
import pandas as pd
from tqdm import tqdm

from code.data.loader import IncidentDataset
from code.data.preprocessing import Preprocessor
from code.data.mock_network_env import MockNetworkEnv
from code.agent.orchestrator import TroubleshootingAgent
from code.agent.llm_client import GeminiClient
from code.baselines.zero_shot import ZeroShotAgent
from code.baselines.react_agent import ReActAgent
from code.baselines.coding_agent import CodingAgent
from code.baselines.sade_style import SADEAgent
from code.baselines.scripted_rules import ScriptedRuleAgent
from code.experiments.metrics import MetricCalculator
from code.experiments.statistical_tests import StatisticalAnalyzer


class LLMJudge:
    """Evaluates agent diagnosis using Gemini LLM-as-a-judge or calibrated rubric (1.0 to 5.0 scale)."""

    def __init__(self, llm_client: Optional[GeminiClient] = None, use_llm: bool = False):
        self.llm_client = llm_client
        self.use_llm = use_llm
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "judge.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def evaluate(
        self,
        incident: Dict[str, Any],
        agent_out: Dict[str, Any]
    ) -> Dict[str, float]:
        """Scores outcome correctness, fix quality, and reasoning quality."""
        # Check if live Gemini LLM judge should be invoked with safe string substitution
        if self.use_llm and self.llm_client and self.prompt_template:
            try:
                formatted_prompt = (
                    self.prompt_template
                    .replace("{scenario}", str(incident.get("scenario", "unknown")))
                    .replace("{ground_truth_has_fault}", str(incident.get("ground_truth_has_fault", False)))
                    .replace("{ground_truth_fault_family}", str(incident.get("ground_truth_fault_family", "none")))
                    .replace("{ground_truth_device}", str(incident.get("ground_truth_device", "none")))
                    .replace("{ground_truth_fix}", str(incident.get("ground_truth_fix", "none")))
                    .replace("{ticket_valid}", str(agent_out.get("ticket_valid", True)))
                    .replace("{agent_detected}", str(agent_out.get("detected", False)))
                    .replace("{agent_device}", str(agent_out.get("localized_device", "none")))
                    .replace("{agent_root_cause}", str(agent_out.get("root_cause", "none")))
                    .replace("{agent_remediation}", str(agent_out.get("remediation", {})))
                    .replace("{agent_reasoning}", str(agent_out.get("trace_logs", [])))
                )
                resp = self.llm_client.generate_json(formatted_prompt)
                parsed = resp.get("parsed_json", {})
                if "overall_judge_score" in parsed and "outcome_score" in parsed:
                    return {
                        "outcome_score": float(parsed.get("outcome_score", 3.0)),
                        "fix_score": float(parsed.get("fix_score", 3.0)),
                        "reasoning_score": float(parsed.get("reasoning_score", 3.0)),
                        "overall_judge_score": float(parsed.get("overall_judge_score", 3.0))
                    }
            except Exception:
                pass

        # 1. Outcome correctness rubric
        gt_has_fault = incident["ground_truth_has_fault"]
        detected = agent_out["detected"]

        if not gt_has_fault:
            if not detected:
                outcome_score = 5.0
            else:
                outcome_score = 1.0
        else:
            if not detected:
                outcome_score = 1.0
            else:
                gt_cause = incident["ground_truth_fault_family"]
                gt_dev = incident["ground_truth_device"]
                pred_cause = agent_out["root_cause"]
                pred_dev = agent_out["localized_device"]

                if pred_cause == gt_cause and pred_dev == gt_dev:
                    outcome_score = 5.0
                elif pred_cause == gt_cause:
                    outcome_score = 4.0
                elif pred_dev == gt_dev:
                    outcome_score = 3.0
                else:
                    outcome_score = 2.0

        # 2. Fix quality rubric
        rem = agent_out.get("remediation", {})
        if not gt_has_fault:
            if not rem.get("remediation_proposed", False):
                fix_score = 5.0
            else:
                fix_score = 1.0
        else:
            if rem.get("remediation_proposed", False):
                if rem.get("requires_human_approval", False) and rem.get("pre_flight_check"):
                    fix_score = 5.0
                else:
                    fix_score = 3.5
            else:
                fix_score = 2.5

        # 3. Reasoning quality rubric
        if agent_out.get("abstain_invoked", False) and not gt_has_fault:
            reasoning_score = 5.0
        elif agent_out.get("turns_used", 0) <= 20 and len(agent_out.get("ranked_causes", [])) > 0:
            reasoning_score = 4.5
        elif agent_out.get("no_submission", False):
            reasoning_score = 1.0
        else:
            reasoning_score = 3.5

        overall = round(0.4 * outcome_score + 0.3 * fix_score + 0.3 * reasoning_score, 2)
        return {
            "outcome_score": outcome_score,
            "fix_score": fix_score,
            "reasoning_score": reasoning_score,
            "overall_judge_score": overall
        }


class ExperimentRunner:
    """Orchestrates comprehensive benchmark experiments across all agent models."""

    def __init__(
        self,
        config_path: str = "configs/experiment_config.yaml",
        use_live_llm: bool = False,
        gemini_api_key: Optional[str] = None,
        gemini_model: str = "gemini-1.5-flash"
    ):
        self.config_path = config_path
        self.config = self._load_config()
        self.dataset_mgr = IncidentDataset(splits_path=self.config.get("paths", {}).get("splits_file"))
        self.preprocessor = Preprocessor(max_tokens=self.config.get("evidence_filtering", {}).get("max_output_tokens", 500))

        # Initialize Gemini LLM client
        self.use_live_llm = use_live_llm or self.config.get("llm", {}).get("use_live_llm", False)
        api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")
        model = gemini_model or self.config.get("llm", {}).get("model", "gemini-1.5-flash")
        self.llm_client = GeminiClient(api_key=api_key, model_name=model)
        self.judge = LLMJudge(llm_client=self.llm_client, use_llm=self.use_live_llm)

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {"turn_budget": 20, "default_seed": 42}

    def run_benchmark(
        self,
        num_incidents: int = 150,
        output_csv: str = "results/raw_runs.csv",
        seed: int = 42
    ) -> pd.DataFrame:
        """Executes full benchmark suite for proposed agent and all 5 baselines."""
        print(f"[+] Generating benchmark corpus of {num_incidents} incidents (including healthy controls)...")
        raw_incidents = self.dataset_mgr.generate_benchmark_dataset(total_target=num_incidents, healthy_ratio=0.25)

        # Audit fault injections
        valid_incidents, _ = self.preprocessor.audit_fault_injections(
            raw_incidents,
            output_csv_path="results/fault_audit.csv"
        )
        print(f"[+] Verified {len(valid_incidents)} of {len(raw_incidents)} incidents passed fault injection audit.")

        # Initialize models
        models = {
            "Proposed_7Phase_Agent": TroubleshootingAgent(
                turn_budget=self.config.get("turn_budget", 20),
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            ),
            "Baseline_SADE_Style": SADEAgent(
                turn_budget=self.config.get("turn_budget", 20),
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            ),
            "Baseline_ReAct": ReActAgent(turn_budget=self.config.get("turn_budget", 20)),
            "Baseline_Generic_Coding": CodingAgent(turn_budget=self.config.get("turn_budget", 20)),
            "Baseline_Zero_Shot": ZeroShotAgent(
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            ),
            "Baseline_Scripted_Rules": ScriptedRuleAgent()
        }

        all_records = []
        run_counter = 1

        print("[+] Commencing experimental evaluation runs...")
        for inc in tqdm(valid_incidents, desc="Incidents"):
            env = MockNetworkEnv(
                scenario=inc["scenario"],
                topology_size=inc["topology_size"],
                fault_injected=inc["ground_truth_has_fault"],
                fault_family=inc["ground_truth_fault_family"],
                faulty_device=inc["ground_truth_device"]
            )

            for model_name, model_inst in models.items():
                agent_res = model_inst.troubleshoot(inc, env)
                judge_scores = self.judge.evaluate(inc, agent_res)

                record = {
                    "run_id": f"RUN-{run_counter:06d}",
                    "model_name": model_name,
                    "incident_id": inc["incident_id"],
                    "scenario": inc["scenario"],
                    "topology_size": inc["topology_size"],
                    "split": inc["split"],
                    "dataset_source": inc.get("dataset_source", "NIKA"),
                    "is_healthy_control": inc["ground_truth_has_fault"] == False,
                    "ground_truth_has_fault": inc["ground_truth_has_fault"],
                    "ground_truth_fault_family": inc["ground_truth_fault_family"],
                    "ground_truth_device": inc["ground_truth_device"],
                    "detected": agent_res["detected"],
                    "localized_device": agent_res["localized_device"],
                    "root_cause": agent_res["root_cause"],
                    "confidence": agent_res["confidence"],
                    "remediation_proposed": agent_res.get("remediation", {}).get("remediation_proposed", False),
                    "abstain_invoked": agent_res.get("abstain_invoked", False),
                    "turns_used": agent_res.get("turns_used", 0),
                    "time_seconds": agent_res.get("time_seconds", 0.0),
                    "input_tokens": agent_res.get("input_tokens", 0),
                    "output_tokens": agent_res.get("output_tokens", 0),
                    "cost_usd": agent_res.get("cost_usd", 0.0),
                    "no_submission": agent_res.get("no_submission", False),
                    "ticket_valid": agent_res.get("ticket_valid", True),
                    "outcome_score": judge_scores["outcome_score"],
                    "fix_score": judge_scores["fix_score"],
                    "reasoning_score": judge_scores["reasoning_score"],
                    "overall_judge_score": judge_scores["overall_judge_score"]
                }

                all_records.append(record)
                run_counter += 1

        df_runs = pd.DataFrame(all_records)
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df_runs.to_csv(output_csv, index=False)
        print(f"[+] Completed {len(df_runs)} experimental runs. Saved raw records to {output_csv}.")

        # Compute summary metrics and statistical significance
        calc = MetricCalculator()
        summary_df = calc.compute_summary_table(df_runs)
        summary_df.to_csv("results/metrics_summary.csv", index=False)
        print("[+] Saved aggregate summary metrics to results/metrics_summary.csv.")

        stats_analyzer = StatisticalAnalyzer()
        sig_df = stats_analyzer.run_significance_suite(df_runs)
        sig_df.to_csv("results/statistical_tests.csv", index=False)
        print("[+] Saved paired Wilcoxon statistical significance tests to results/statistical_tests.csv.")

        return df_runs
