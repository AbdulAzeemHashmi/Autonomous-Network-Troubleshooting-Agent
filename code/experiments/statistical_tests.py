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
            # Rank biserial correlation or standard effect size r = Z / sqrt(N)
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

