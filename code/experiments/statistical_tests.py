"""
Statistical Significance and Confidence Intervals Module
Grounding: Phase 2 Step 9 Methodology.
Computes 95% bootstrap confidence intervals and paired Wilcoxon signed-rank tests (following RCLAgent).
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


class StatisticalAnalyzer:
    """Performs non-parametric statistical tests and bootstrap CI estimation."""

    @staticmethod
    def bootstrap_confidence_interval(
        data: List[float],
        n_bootstraps: int = 1000,
        ci: float = 0.95,
        seed: int = 42
    ) -> Tuple[float, float, float]:
        """Computes bootstrap mean and lower/upper bounds at (1 - ci)/2 and 1 - (1 - ci)/2 percentiles."""
        if not data or len(data) == 0:
            return 0.0, 0.0, 0.0

        arr = np.array(data)
        if len(arr) == 1 or np.all(arr == arr[0]):
            val = float(arr[0])
            return val, val, val

        rng = np.random.RandomState(seed)
        boot_means = []
        n = len(arr)
        for _ in range(n_bootstraps):
            sample = rng.choice(arr, size=n, replace=True)
            boot_means.append(np.mean(sample))

        alpha = (1.0 - ci) / 2.0
        lower = float(np.percentile(boot_means, alpha * 100))
        upper = float(np.percentile(boot_means, (1.0 - alpha) * 100))
        mean_val = float(np.mean(arr))
        return round(mean_val, 4), round(lower, 4), round(upper, 4)

    @staticmethod
    def paired_wilcoxon_test(
        proposed_scores: List[float],
        baseline_scores: List[float]
    ) -> Dict[str, Any]:
        """Runs two-sided paired Wilcoxon signed-rank test between proposed agent and baseline."""
        if len(proposed_scores) != len(baseline_scores) or len(proposed_scores) == 0:
            return {"statistic": 0.0, "p_value": 1.0, "significant_at_05": False}

        p_arr = np.array(proposed_scores)
        b_arr = np.array(baseline_scores)
        diff = p_arr - b_arr

        if np.all(diff == 0):
            return {
                "statistic": 0.0,
                "p_value": 1.0,
                "significant_at_05": False,
                "effect_size": 0.0,
                "note": "Zero difference between paired samples"
            }

        try:
            stat, p_val = wilcoxon(p_arr, b_arr, alternative="two-sided")
            n = len(diff[diff != 0])
            z_score = np.abs(np.mean(diff) / (np.std(diff) + 1e-9))
            effect_size = float(z_score / np.sqrt(n)) if n > 0 else 0.0

            return {
                "statistic": round(float(stat), 4),
                "p_value": round(float(p_val), 6),
                "significant_at_05": bool(p_val < 0.05),
                "effect_size": round(effect_size, 4),
                "n_pairs": len(proposed_scores)
            }
        except Exception as e:
            return {
                "statistic": 0.0,
                "p_value": 1.0,
                "significant_at_05": False,
                "error": str(e)
            }

    @classmethod
    def run_significance_suite(cls, runs_df: pd.DataFrame) -> pd.DataFrame:
        """Runs paired Wilcoxon signed-rank tests comparing Proposed_7Phase_Agent vs all baselines."""
        prop_df = runs_df[runs_df["model_name"] == "Proposed_7Phase_Agent"].sort_values("incident_id")
        if prop_df.empty:
            return pd.DataFrame()

        rows = []
        baselines = [m for m in runs_df["model_name"].unique() if m != "Proposed_7Phase_Agent"]
        for base in baselines:
            b_df = runs_df[runs_df["model_name"] == base].sort_values("incident_id")
            merged = pd.merge(prop_df, b_df, on="incident_id", suffixes=("_prop", "_base"))
            if merged.empty:
                continue

            test_res = cls.paired_wilcoxon_test(
                merged["overall_judge_score_prop"].tolist(),
                merged["overall_judge_score_base"].tolist()
            )

            rows.append({
                "baseline": base,
                "metric": "overall_judge_score",
                "proposed_mean": round(float(merged["overall_judge_score_prop"].mean()), 3),
                "baseline_mean": round(float(merged["overall_judge_score_base"].mean()), 3),
                "wilcoxon_statistic": test_res.get("statistic", 0.0),
                "p_value": test_res.get("p_value", 1.0),
                "significant_at_05": test_res.get("significant_at_05", False),
                "effect_size": test_res.get("effect_size", 0.0)
            })

        return pd.DataFrame(rows)
