# Autonomous Network Troubleshooting Agent
**Course**: Computer Networks  
**Group Members**: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)  
**Research Focus**: LLM-driven autonomous network troubleshooting, root-cause localization (RCA), and safe remediation with healthy-network controls.

---

## Overview

Modern automated self-healing frameworks frequently over-diagnose healthy networks when fed noisy tickets, suffer from evidence dilution on complex topologies, and fail to report comprehensive metrics (such as false positive rates on healthy controls and token costs).

This project implements the **12-Step Research Methodology** established in Phase 2:
1. **7-Phase Diagnostic Agent**:
   - **Phase 1: Ticket Validator** — Verifies ticket veracity against real-time telemetry.
   - **Phase 2: Layered Evidence Scan** — Structured L2-to-Service scans (`show interface`, `ping`, `ip route`, `ss`, `curl`).
   - **Phase 3: Hypothesis Router** — Symptom-to-fault-family routing.
   - **Phase 4: Falsification Probes** — Explicit attempts to disprove candidate hypotheses.
   - **Phase 5: Abstain Logic** — Declares "No fault found" when evidence does not support failure, avoiding false alarms.
   - **Phase 6: Ranked Root Cause** — Ranked causes with calibrated confidence scores and bounded evidence snippets.
   - **Phase 7: Optional Validated Remediation** — Suggests fixes guarded by validation gates and human-in-the-loop approval.
2. **5 Baseline Architectures**:
   - Zero-Shot LLM (no tool interaction)
   - ReAct Agent (NIKA-style thought-action-observation loop)
   - Generic Coding Agent (Claude Code-style script synthesizer)
   - SADE-Style Agent (phase-gated without falsification/abstain)
   - Scripted Rule Checks (deterministic threshold rules, non-AI)
3. **Comprehensive Metric Suite**:
   - Detection Accuracy, Localization Accuracy, RCA F1, False-Positive Rate (on healthy controls), Mean Steps, Time (s), Token Usage & Dollar Cost, No-Submission Rate, LLM Judge Score, and Cross-Scenario Transfer Score.
4. **Rigorous Statistical & Failure Analysis**:
   - 95% Bootstrap Confidence Intervals & Paired Wilcoxon Signed-Rank tests.
   - 5 Component Ablation Studies.
   - Kim et al. 12-Pitfall Failure Taxonomy Classification.

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent.git
   cd Autonomous-Network-Troubleshooting-Agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Environment**:
   ```bash
   pytest tests/
   ```

---

## Running the Complete Experimental Pipeline

To run the end-to-end evaluation, ablations, statistical tests, and figure generation in a single command:
```bash
python run_all.py --config configs/experiment_config.yaml
```

Generated outputs:
- **Raw execution logs**: `results/raw_runs.csv`
- **Metric summaries & CIs**: `results/metrics_summary.csv`
- **Statistical significance tests**: `results/statistical_tests.csv`
- **Ablation results**: `results/ablation_results.csv`
- **Failure classification**: `results/failure_taxonomy.csv`
- **Publication figures**: `figures/*.png`
- **Full Research Report**: `docs/Phase3_Report.md`

---

## Directory Structure

```text
Autonomous-Network-Troubleshooting-Agent/
├── code/
│   ├── agent/          # 7-phase agent modules and orchestrator
│   ├── baselines/      # 5 comparative baselines
│   ├── data/           # Dataset loaders, fault audit, mock network telemetry
│   ├── experiments/    # Runner, metrics, statistical tests, ablations, error taxonomy
│   └── visualization/  # Publication plotting scripts
├── configs/            # Experiment, model, and dataset split configurations
├── docs/               # Detailed documentation and final Phase 3 report
├── figures/            # High-resolution charts and diagrams
├── prompts/            # Agent phase prompts and LLM judge rubric
├── results/            # CSV/JSON experimental artifacts
└── tests/              # Pytest test suite
```

