"""
Comprehensive Experimental Runner
Grounding: Phase 2 Step 7 (Experimental Design) and Step 8 (Evaluation Metrics).
Runs proposed agent and all 5 baselines across scenarios, topologies, and seeds.
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
from code.baselines.zero_shot import ZeroShotAgent
from code.baselines.react_agent import ReActAgent
from code.baselines.coding_agent import CodingAgent
from code.baselines.sade_style import SADEAgent
from code.baselines.scripted_rules import ScriptedRuleAgent
from code.experiments.metrics import MetricCalculator
from code.experiments.statistical_tests import StatisticalAnalyzer


class LLMJudge:
    """Simulates the FaulT-Bench & SADE LLM-as-a-judge rubric (1.0 to 5.0 scale)."""

    @staticmethod
    def evaluate(
        incident: Dict[str, Any],
        agent_out: Dict[str, Any]
    ) -> Dict[str, float]:
        """Scores outcome correctness, fix quality, and reasoning quality."""
        # 1. Outcome correctness
        gt_has_fault = incident["ground_truth_has_fault"]
        detected = agent_out["detected"]

        if not gt_has_fault:
            if not detected:
                # Correctly identified healthy
                outcome_score = 5.0
            else:
                # False alarm
                outcome_score = 1.0
        else:
            if not detected:
                # Missed genuine fault
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

        # 2. Fix quality
        rem = agent_out.get("remediation", {})
        if not gt_has_fault:
            if not rem.get("remediation_proposed", False):
                fix_score = 5.0
            else:
                fix_score = 1.0  # Erroneous remediation proposed on healthy network
        else:
            if rem.get("remediation_proposed", False):
                if rem.get("requires_human_approval", False) and rem.get("pre_flight_check"):
                    fix_score = 5.0
                else:
                    fix_score = 3.5
            else:
                fix_score = 2.5  # No fix proposed for fault

        # 3. Reasoning quality
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

    def __init__(self, config_path: str = "configs/experiment_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.dataset_mgr = IncidentDataset(splits_path=self.config.get("paths", {}).get("splits_file"))
        self.preprocessor = Preprocessor(max_tokens=self.config.get("evidence_filtering", {}).get("max_output_tokens", 500))
        self.judge = LLMJudge()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
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
            "Proposed_7Phase_Agent": TroubleshootingAgent(turn_budget=self.config.get("turn_budget", 20)),
            "Baseline_SADE_Style": SADEAgent(turn_budget=self.config.get("turn_budget", 20)),
            "Baseline_ReAct": ReActAgent(turn_budget=self.config.get("turn_budget", 20)),
            "Baseline_Generic_Coding": CodingAgent(turn_budget=self.config.get("turn_budget", 20)),
            "Baseline_Zero_Shot": ZeroShotAgent(),
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
                    "abstain_invoked": agent_res.get("abstain_invoked", False),
                    "remediation_proposed": agent_res.get("remediation", {}).get("remediation_proposed", False),
                    "turns_used": agent_res["turns_used"],
                    "time_seconds": agent_res["time_seconds"],
                    "input_tokens": agent_res["input_tokens"],
                    "output_tokens": agent_res["output_tokens"],
                    "cost_usd": agent_res["cost_usd"],
                    "no_submission": agent_res["no_submission"],
                    **judge_scores
                }
                all_records.append(record)
                run_counter += 1

        runs_df = pd.DataFrame(all_records)
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        runs_df.to_csv(output_csv, index=False)
        print(f"[+] Completed {len(runs_df)} experimental runs. Saved raw records to {output_csv}.")

        # Generate summary metrics
        self.generate_metrics_and_stats(runs_df)

        return runs_df

    def generate_metrics_and_stats(
        self,
        runs_df: pd.DataFrame,
        summary_csv: str = "results/metrics_summary.csv",
        stats_csv: str = "results/statistical_tests.csv"
    ):
        """Computes summary metrics, 95% CIs, and Wilcoxon signed-rank tests."""
        summary_rows = []
        for model_name, group in runs_df.groupby("model_name"):
            metrics = MetricCalculator.compute_all_metrics(group)
            # Add 95% bootstrap CI for RCA F1 and detection
            f1_scores = [1.0 if r["ground_truth_fault_family"] == r["root_cause"] else 0.0 for _, r in group.iterrows()]
            m_f1, f1_low, f1_high = StatisticalAnalyzer.bootstrap_confidence_interval(f1_scores)

            summary_rows.append({
                "model_name": model_name,
                **metrics,
                "rca_acc_mean": m_f1,
                "rca_acc_ci_lower": f1_low,
                "rca_acc_ci_upper": f1_high
            })

        summary_df = pd.DataFrame(summary_rows)
        # Sort so Proposed Agent is on top
        summary_df["sort_key"] = summary_df["model_name"].apply(lambda x: 0 if "Proposed" in x else 1)
        summary_df = summary_df.sort_values(by=["sort_key", "rca_f1_macro"], ascending=[True, False]).drop(columns=["sort_key"])
        summary_df.to_csv(summary_csv, index=False)
        print(f"[+] Saved aggregate summary metrics to {summary_csv}.")

        # Paired Wilcoxon Signed-Rank tests
        proposed_df = runs_df[runs_df["model_name"] == "Proposed_7Phase_Agent"].sort_values(by="incident_id")
        proposed_scores = (proposed_df["ground_truth_fault_family"] == proposed_df["root_cause"]).astype(int).tolist()

        stat_rows = []
        for model_name in runs_df["model_name"].unique():
            if model_name == "Proposed_7Phase_Agent":
                continue
            base_df = runs_df[runs_df["model_name"] == model_name].sort_values(by="incident_id")
            base_scores = (base_df["ground_truth_fault_family"] == base_df["root_cause"]).astype(int).tolist()

            wilc = StatisticalAnalyzer.paired_wilcoxon_test(proposed_scores, base_scores)
            stat_rows.append({
                "comparison": f"Proposed_7Phase_Agent vs {model_name}",
                **wilc
            })

        stat_df = pd.DataFrame(stat_rows)
        stat_df.to_csv(stats_csv, index=False)
        print(f"[+] Saved paired Wilcoxon statistical significance tests to {stats_csv}.")
