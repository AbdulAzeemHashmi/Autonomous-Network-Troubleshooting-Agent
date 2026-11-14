"""
Component Ablation Studies Module
Grounding: Phase 2 Step 10 Methodology (Ablation and Component Analysis).
Evaluates the contribution of individual architectural components:
1. Full Proposed Agent
2. Ablation: No Phase Gating (free-form unguided single prompt)
3. Ablation: No Skills (remove fault-family skill library)
4. Ablation: No Falsification (skip active falsification counter-probes)
5. Ablation: No Abstain Option (force agent to always declare a fault)
6. Ablation: No Evidence Filtering (feed raw un-trimmed tool output)
"""

from typing import List, Dict, Any, Optional
import os
import pandas as pd
from tqdm import tqdm

from code.data.loader import IncidentDataset
from code.data.preprocessing import Preprocessor
from code.data.mock_network_env import MockNetworkEnv
from code.agent.orchestrator import TroubleshootingAgent
from code.agent.llm_client import GeminiClient
from code.experiments.metrics import MetricCalculator
from code.experiments.runner import LLMJudge


class AblationStudy:
    """Executes systematic component removal to quantify architectural contributions."""

    def __init__(
        self,
        num_incidents: int = 60,
        seed: int = 42,
        use_live_llm: bool = False,
        gemini_api_key: Optional[str] = None,
        gemini_model: str = "gemini-1.5-flash"
    ):
        self.num_incidents = num_incidents
        self.seed = seed
        self.use_live_llm = use_live_llm
        self.dataset_mgr = IncidentDataset()
        self.llm_client = GeminiClient(api_key=gemini_api_key, model_name=gemini_model)
        self.judge = LLMJudge(llm_client=self.llm_client, use_llm=self.use_live_llm)

    def run_ablations(
        self,
        output_csv: str = "results/ablation_results.csv"
    ) -> pd.DataFrame:
        """Runs the 6 ablation variants on the benchmark corpus."""
        print(f"[+] Generating ablation corpus ({self.num_incidents} incidents)...")
        incidents = self.dataset_mgr.generate_benchmark_dataset(
            total_target=self.num_incidents,
            healthy_ratio=0.30
        )

        variants = {
            "Full_Proposed_Agent": TroubleshootingAgent(
                enable_ticket_validation=True,
                enable_falsification=True,
                enable_abstain=True,
                enable_evidence_filtering=True,
                enable_skills=True,
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            ),
            "Ablation_No_Phase_Gating": TroubleshootingAgent(
                enable_ticket_validation=False,
                enable_falsification=False,
                enable_abstain=False,
                enable_evidence_filtering=False,
                enable_skills=False,
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            ),
            "Ablation_No_Skills": TroubleshootingAgent(
                enable_ticket_validation=True,
                enable_falsification=True,
                enable_abstain=True,
                enable_evidence_filtering=True,
                enable_skills=False,
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            ),
            "Ablation_No_Falsification": TroubleshootingAgent(
                enable_ticket_validation=True,
                enable_falsification=False,
                enable_abstain=True,
                enable_evidence_filtering=True,
                enable_skills=True,
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            ),
            "Ablation_No_Abstain": TroubleshootingAgent(
                enable_ticket_validation=True,
                enable_falsification=True,
                enable_abstain=False,
                enable_evidence_filtering=True,
                enable_skills=True,
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            ),
            "Ablation_No_Evidence_Filtering": TroubleshootingAgent(
                enable_ticket_validation=True,
                enable_falsification=True,
                enable_abstain=True,
                enable_evidence_filtering=False,
                enable_skills=True,
                llm_client=self.llm_client,
                use_llm=self.use_live_llm
            )
        }

        all_runs = []
        print("[+] Commencing ablation experimental runs...")
        for inc in tqdm(incidents, desc="Ablation Incidents"):
            env = MockNetworkEnv(
                scenario=inc["scenario"],
                topology_size=inc["topology_size"],
                fault_injected=inc["ground_truth_has_fault"],
                fault_family=inc["ground_truth_fault_family"],
                faulty_device=inc["ground_truth_device"]
            )

            for variant_name, agent_inst in variants.items():
                agent_res = agent_inst.troubleshoot(inc, env)
                judge_scores = self.judge.evaluate(inc, agent_res)

                all_runs.append({
                    "variant": variant_name,
                    "incident_id": inc["incident_id"],
                    "is_healthy_control": inc["ground_truth_has_fault"] == False,
                    "ground_truth_has_fault": inc["ground_truth_has_fault"],
                    "ground_truth_fault_family": inc["ground_truth_fault_family"],
                    "ground_truth_device": inc["ground_truth_device"],
                    "detected": agent_res["detected"],
                    "localized_device": agent_res["localized_device"],
                    "root_cause": agent_res["root_cause"],
                    "confidence": agent_res["confidence"],
                    "turns_used": agent_res["turns_used"],
                    "time_seconds": agent_res["time_seconds"],
                    "input_tokens": agent_res["input_tokens"],
                    "output_tokens": agent_res["output_tokens"],
                    "cost_usd": agent_res["cost_usd"],
                    "abstain_invoked": agent_res["abstain_invoked"],
                    "no_submission": agent_res["no_submission"],
                    "split": inc["split"],
                    "overall_judge_score": judge_scores["overall_judge_score"]
                })

        df_ablation = pd.DataFrame(all_runs)

        # Aggregate ablation metrics
        rows = []
        for variant_name, v_df in df_ablation.groupby("variant"):
            metrics = MetricCalculator.compute_all_metrics(v_df)
            metrics["variant"] = variant_name
            rows.append(metrics)

        summary_df = pd.DataFrame(rows)
        # Order columns
        cols = ["variant"] + [c for c in summary_df.columns if c != "variant"]
        summary_df = summary_df[cols]

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        summary_df.to_csv(output_csv, index=False)
        print(f"[+] Ablation studies complete. Saved summary to {output_csv}.")
        return summary_df
