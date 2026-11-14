"""
Metrics Computation Module
Grounding: Phase 2 Step 8 Methodology (9 Metric Groups).
Calculates Detection Accuracy, Localization Accuracy, RCA F1, False Positive Rate (FPR),
Steps, Time, Token Usage, Cost (USD), No-Submission Rate, LLM Judge Score, and Transfer Score.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score


class MetricCalculator:
    """Computes all 9 canonical metric groups across troubleshooting runs."""

    @staticmethod
    def compute_all_metrics(runs_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates aggregate metrics from a raw runs dataframe."""
        total_runs = len(runs_df)
        if total_runs == 0:
            return {}

        # 1. Detection Accuracy: did agent correctly distinguish fault vs healthy?
        correct_detection = (
            (runs_df["ground_truth_has_fault"] == runs_df["detected"])
        ).sum()
        detection_accuracy = float(correct_detection / total_runs)

        # 2. Localization Accuracy: on incidents that actually had a fault, was device exact?
        faulty_runs = runs_df[runs_df["ground_truth_has_fault"] == True]
        if len(faulty_runs) > 0:
            correct_loc = (faulty_runs["ground_truth_device"] == faulty_runs["localized_device"]).sum()
            localization_accuracy = float(correct_loc / len(faulty_runs))
        else:
            localization_accuracy = 1.0

        # 3. RCA F1: multiclass macro/micro F1 over fault family classifications
        y_true = runs_df["ground_truth_fault_family"].fillna("none").astype(str).tolist()
        y_pred = runs_df["root_cause"].fillna("none").astype(str).tolist()
        rca_f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        rca_f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

        # 4. False-Positive Rate on Healthy Cases (KEY NEW METRIC - Sub-Gap A)
        healthy_runs = runs_df[runs_df["ground_truth_has_fault"] == False]
        if len(healthy_runs) > 0:
            false_alarms = (healthy_runs["detected"] == True).sum()
            false_positive_rate = float(false_alarms / len(healthy_runs))
        else:
            false_positive_rate = 0.0

        # 5. Steps and Time
        mean_steps = float(runs_df["turns_used"].mean())
        mean_time_seconds = float(runs_df["time_seconds"].mean())

        # 6. Tokens and Cost
        mean_input_tokens = float(runs_df["input_tokens"].mean())
        mean_output_tokens = float(runs_df["output_tokens"].mean())
        mean_cost_usd = float(runs_df["cost_usd"].mean())

        # 7. No-Submission Rate
        no_subs = runs_df["no_submission"].sum()
        no_submission_rate = float(no_subs / total_runs)

        # 8. Judge Score (1.0 to 5.0 scale)
        mean_judge_score = float(runs_df["overall_judge_score"].mean()) if "overall_judge_score" in runs_df else 0.0

        # 9. Transfer Score (Sub-Gap C: held-out performance / development performance)
        dev_runs = runs_df[runs_df["split"] == "development"]
        held_out_runs = runs_df[runs_df["split"] == "held_out"]

        if len(dev_runs) > 0 and len(held_out_runs) > 0:
            dev_f1 = float(f1_score(
                dev_runs["ground_truth_fault_family"].astype(str),
                dev_runs["root_cause"].astype(str),
                average="macro",
                zero_division=0
            ))
            held_f1 = float(f1_score(
                held_out_runs["ground_truth_fault_family"].astype(str),
                held_out_runs["root_cause"].astype(str),
                average="macro",
                zero_division=0
            ))
            transfer_score = float(held_f1 / dev_f1) if dev_f1 > 0 else 1.0
        else:
            dev_f1 = rca_f1_macro
            held_f1 = rca_f1_macro
            transfer_score = 1.0

        return {
            "total_runs": total_runs,
            "detection_accuracy": round(detection_accuracy, 4),
            "localization_accuracy": round(localization_accuracy, 4),
            "rca_f1_macro": round(rca_f1_macro, 4),
            "rca_f1_weighted": round(rca_f1_weighted, 4),
            "false_positive_rate": round(false_positive_rate, 4),
            "mean_steps": round(mean_steps, 2),
            "mean_time_seconds": round(mean_time_seconds, 3),
            "mean_input_tokens": round(mean_input_tokens, 1),
            "mean_output_tokens": round(mean_output_tokens, 1),
            "mean_cost_usd": round(mean_cost_usd, 6),
            "no_submission_rate": round(no_submission_rate, 4),
            "mean_judge_score": round(mean_judge_score, 2),
            "dev_f1": round(dev_f1, 4),
            "held_out_f1": round(held_f1, 4),
            "transfer_score": round(transfer_score, 4)
        }

    @classmethod
    def compute_summary_table(cls, runs_df: pd.DataFrame) -> pd.DataFrame:
        """Groups raw runs by model_name and computes summary metric rows."""
        summary_rows = []
        for model_name, m_df in runs_df.groupby("model_name"):
            metrics = cls.compute_all_metrics(m_df)
            metrics["model_name"] = model_name
            summary_rows.append(metrics)
        df_summary = pd.DataFrame(summary_rows)
        if not df_summary.empty:
            cols = ["model_name"] + [c for c in df_summary.columns if c != "model_name"]
            return df_summary[cols]
        return df_summary
