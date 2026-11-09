"""
End-to-end reproducibility tests for the complete Phase 3 pipeline.
"""

import pytest
import subprocess
import sys
import os


def test_reproducibility_run_all(tmp_path):
    cmd = [
        sys.executable,
        "run_all.py",
        "--config", "configs/experiment_config.yaml",
        "--num_incidents", "6",
        "--num_ablations", "6",
        "--seed", "42"
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, f"run_all failed with stderr: {proc.stderr}"

    # Verify generated artifacts
    assert os.path.exists("results/raw_runs.csv")
    assert os.path.exists("results/metrics_summary.csv")
    assert os.path.exists("results/statistical_tests.csv")
    assert os.path.exists("results/ablation_results.csv")
    assert os.path.exists("results/failure_taxonomy.csv")
    assert os.path.exists("docs/error_analysis.md")
    assert os.path.exists("figures/fig1_main_performance_comparison.png")
    assert os.path.exists("figures/fig4_root_cause_confusion_matrix.png")
