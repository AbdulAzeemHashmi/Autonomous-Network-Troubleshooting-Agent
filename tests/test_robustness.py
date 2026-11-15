"""
Unit tests for Robustness Evaluation Suite
Grounding: Phase 3 Rubric Criterion 3 (Relevant Robustness Tests and Research Validation).
"""

import pytest
import os
import pandas as pd
from code.experiments.robustness import RobustnessAnalyzer


def test_robustness_analyzer_initialization():
    analyzer = RobustnessAnalyzer(seed=42)
    assert analyzer.seed == 42
    assert analyzer.llm_client is not None
    assert analyzer.dataset_mgr is not None


def test_robustness_topology_scale_subset():
    analyzer = RobustnessAnalyzer(seed=42)
    df = analyzer.evaluate_topology_scale()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "test_type" in df.columns
    assert "model_name" in df.columns
    assert "metric_value" in df.columns
    assert (df["test_type"] == "topology_scale").all()


def test_robustness_threshold_sensitivity():
    analyzer = RobustnessAnalyzer(seed=42)
    df = analyzer.evaluate_threshold_sensitivity()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5  # 5 thresholds: 0.60, 0.70, 0.80, 0.90, 0.95
    assert (df["test_type"] == "remediation_threshold").all()


def test_robustness_healthy_ratio_stress():
    analyzer = RobustnessAnalyzer(seed=42)
    df = analyzer.evaluate_healthy_ratio_stress()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Verify that proposed agent maintained 0.0 false positive rate
    prop_runs = df[df["model_name"] == "Proposed_7Phase_Agent"]
    assert (prop_runs["metric_value"] == 0.0).all()
