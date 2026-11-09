"""
Unit tests for metrics calculation, statistical significance tests, and experimental runner pilot.
"""

import pytest
import os
import pandas as pd
from code.experiments.metrics import MetricCalculator
from code.experiments.statistical_tests import StatisticalAnalyzer
from code.experiments.runner import ExperimentRunner


def test_metric_calculator():
    data = {
        "ground_truth_has_fault": [True, True, False, False],
        "detected": [True, True, False, True],  # 1 false alarm
        "ground_truth_device": ["leaf1", "spine1", "none", "none"],
        "localized_device": ["leaf1", "leaf2", "none", "leaf1"],
        "ground_truth_fault_family": ["link_failure", "congestion", "healthy", "healthy"],
        "root_cause": ["link_failure", "congestion", "none", "routing_misconfiguration"],
        "turns_used": [5, 6, 2, 8],
        "time_seconds": [0.1, 0.2, 0.05, 0.2],
        "input_tokens": [1000, 1200, 400, 900],
        "output_tokens": [200, 250, 80, 150],
        "cost_usd": [0.006, 0.007, 0.002, 0.005],
        "no_submission": [False, False, False, False],
        "overall_judge_score": [5.0, 4.0, 5.0, 2.0],
        "split": ["development", "held_out", "development", "held_out"]
    }
    df = pd.DataFrame(data)
    metrics = MetricCalculator.compute_all_metrics(df)

    assert metrics["detection_accuracy"] == 0.75
    assert metrics["localization_accuracy"] == 0.50
    assert metrics["false_positive_rate"] == 0.50  # 1 false alarm out of 2 healthy
    assert metrics["mean_steps"] == 5.25


def test_statistical_tests():
    data = [0.8, 0.85, 0.78, 0.92, 0.88]
    mean_val, low, high = StatisticalAnalyzer.bootstrap_confidence_interval(data)
    assert low <= mean_val <= high

    # Paired Wilcoxon
    proposed = [1, 1, 1, 1, 1, 0, 1, 1, 1, 1]
    baseline = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0]
    res = StatisticalAnalyzer.paired_wilcoxon_test(proposed, baseline)
    assert "p_value" in res
    assert res["p_value"] < 0.05


def test_runner_pilot(tmp_path):
    runner = ExperimentRunner()
    out_csv = str(tmp_path / "pilot_runs.csv")
    df = runner.run_benchmark(num_incidents=6, output_csv=out_csv, seed=42)
    assert len(df) == 6 * 6  # 6 incidents * 6 models = 36 runs
    assert os.path.exists(out_csv)
