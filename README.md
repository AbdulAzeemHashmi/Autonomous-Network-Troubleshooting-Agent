# Autonomous Network Troubleshooting Agent

Course: Computer Networks (CS-3001)  
University: FAST National University of Computer and Emerging Sciences (NUCES)  
Group Members:
- Abdul Azeem (24I-2013)
- Taha Amjad (24K-0007)

GitHub Repository: https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent

---

## 1. Project Overview

Modern computer networks are big, complex, and prone to failures like link cuts, route blackholes, buffer congestion, and firewall drops. Human network engineers often take a long time to read logs, run commands, and find the root cause. While Large Language Model (LLM) agents can run network commands, recent research shows two major problems:
1. When the network is healthy and the user ticket is wrong, AI agents almost always make a false alarm (100% false positive rate).
2. As networks grow large (over 100 devices), tool outputs flood the context window, causing the agent to get confused and fail.

This project implements and tests a 7-Phase Autonomous Network Troubleshooting Agent that solves these problems. It includes negative healthy controls to stop false alarms, filters evidence to stop context bloat, uses falsification probes to check hypotheses, and keeps costs very low.

---

## 2. Project Phases Recap

### Phase 1: Literature Review and Research Gaps
In Phase 1, we critically reviewed three 2026 Q1 journal papers on autonomous recovery and self-healing:
1. Huang et al. (IEEE TCCN 2026): LLM agents for AI-native networks.
2. Mwangi et al. (IEEE TNSM 2026): Deep Q Network self-healing for industrial IoT networks.
3. Rawas and Samala (2026): Bio-inspired self-healing for software defined networks.

We identified three research gaps:
- Gap 1: Lack of standardized, reproducible benchmarks for network troubleshooting.
- Gap 2: Incomplete evaluation metrics (papers ignored false alarms, diagnostic accuracy, and dollar cost).
- Gap 3: Limited generalizability across different network topologies.

### Phase 2: Extended Literature and Methodology Design
In Phase 2, we expanded the literature review to 9 papers from 2025 and 2026:
- Production systems: BiAn (Alibaba SIGCOMM 2025), Confucius (Meta SIGCOMM 2025), Ericsson MAS.
- Structured reasoning: SADE (Tseng et al. 2026), RCLAgent (Zhang et al. IEEE TDSC 2026).
- Benchmarks: NIKA (Wang et al. 2025), FaulT-Bench (Tseng et al. 2026).
- Domain models: TeleLogs (5G RCA).
- Failure analysis: Kim et al. (12 failure pitfall types).

We refined the research gap into three sub-gaps:
- Sub-Gap A: No healthy-network controls in evaluations, causing severe over-diagnosis.
- Sub-Gap B: Incomplete metrics (missing false positive rates, token cost, and latency).
- Sub-Gap C: Lack of transfer testing across topologies and unseen network scenarios.

We designed a 12-step methodology and a 7-phase agent architecture to solve these gaps.

### Phase 3: Research Implementation and Experimental Evaluation
In Phase 3, we built the full system in Python and ran experimental evaluations:
1. Proposed 7-Phase Agent:
   - Phase 1 (Ticket Validator): Checks if ticket claims match real reachability.
   - Phase 2 (Layered Evidence Scan): Scans L2, L3, L4, and Service layers in order.
   - Phase 3 (Hypothesis Router): Maps observed symptoms to fault families.
   - Phase 4 (Falsification Probes): Tries to disprove candidate hypotheses with targeted tests.
   - Phase 5 (Abstain Logic): Explicitly outputs "no fault found" if all hypotheses are disproven.
   - Phase 6 (Root Cause Synthesis): Ranks surviving causes with calibrated confidence.
   - Phase 7 (Validated Remediation): Generates safe commands with pre/post checks and human approval gates.
2. Five Comparative Baselines: Zero-Shot LLM, ReAct (NIKA standard), Generic Coding Agent (Claude Code style), SADE-style Agent, and Scripted Rule Checks.
3. Evaluated across 720 benchmark runs and 60 ablation runs across 13 network topologies.
4. Achieved a 0.0% False Positive Rate on healthy networks (compared to 100% for ReAct, SADE, and Coding agents).
5. Achieved an average cost of $0.0138 per session (over 100 times cheaper than SADE).
6. Maintained a 96.3% transfer score on held-out scenarios.

---

## 3. Technology Stack

- Language: Python 3.10+ (tested on Python 3.12)
- Network Modeling: NetworkX 3.7 (graph topology construction, path computations, node dependencies)
- Data Analysis: Pandas 3.0, NumPy 2.5, SciPy 1.18, Scikit-Learn 1.9
- Plotting and Visualization: Matplotlib 3.11
- Testing: Pytest 7.4
- Progress Tracking: Tqdm 4.70
- Configuration: PyYAML 6.0
- HTTP and Telemetry: Requests 2.34, HTTPX 0.28
- PDF Generation: ReportLab 4.0

---

## 4. Dataset and Topologies

The evaluation uses scenarios derived from the public NIKA and FaulT-Bench benchmarks:

1. NIKA Scenarios:
   - datacenter_clos (Data center leaf-spine CLOS fabric)
   - campus_network (Multi-tier campus with core and access switches)
   - isp_backbone (Transit ring and mesh backbone routers)
   - sdn_cloud_fabric (SDN controller and OpenFlow forwarders)
   - p4_testbed (P4 programmable packet processing nodes)

2. FaulT-Bench Topologies:
   - enterprise_branch, leaf_spine_clos, multihomed_edge, transit_wan, sdn_hybrid, bgp_peering_exchange, datacenter_dci, campus_core_access.

3. Topology Sizes:
   - Small: around 11 nodes
   - Medium: around 27 nodes
   - Large: around 101 nodes

4. Healthy-Network Controls (25% of dataset):
   - Networks are completely healthy (0% loss, sub-millisecond latency).
   - Tickets contain false-premise complaints written in 5 reporter styles (Panicked User, Overconfident Junior Admin, Misdirected Developer, Monitoring Bot False Alarm, Cautious Operator).

5. Fault Injection Audit:
   - Every incident is checked by automated probes before testing. All 120 generated benchmark incidents passed verification.

6. Data Splits (configs/splits.json):
   - Strict whole-scenario partition to prevent data leakage.
   - Development (69.2%): 9 scenarios.
   - Held-Out Test (30.8%): 4 scenarios (sdn_cloud_fabric, p4_testbed, bgp_peering_exchange, datacenter_dci).

---

## 5. File and Folder Structure

```text
Autonomous-Network-Troubleshooting-Agent/
├── Phase1_Literature_Review_Report.pdf   # Phase 1 submission report
├── Phase_2_Deliverables.pdf              # Phase 2 methodology report
├── LICENSE                               # MIT License
├── README.md                             # Project documentation and guide
├── requirements.txt                      # Python dependencies
├── run_all.py                            # Single-command end-to-end execution
│
├── configs/                              # System configurations
│   ├── experiment_config.yaml            # Scenarios, topology sizes, token limits
│   ├── models.yaml                       # LLM backbone definitions and pricing
│   └── splits.json                       # Whole-scenario train/test split IDs
│
├── prompts/                              # LLM prompt templates
│   ├── phase1_ticket_validator.txt       # Prompt for validating ticket claims
│   ├── phase2_evidence_scan.txt          # Prompt for layered telemetry scan
│   ├── phase3_hypothesis_router.txt      # Prompt for symptom-to-family mapping
│   ├── phase4_falsification.txt          # Prompt for disproving hypotheses
│   ├── phase6_root_cause.txt             # Prompt for synthesizing root causes
│   ├── phase7_remediation.txt            # Prompt for planning safe remediation
│   └── judge.txt                         # LLM judge rubric (1 to 5 scale)
│
├── code/                                 # Source code
│   ├── agent/                            # Proposed 7-phase troubleshooting agent
│   │   ├── ticket_validator.py           # Phase 1: Ticket veracity evaluation
│   │   ├── evidence_scanner.py           # Phase 2: Layered L2 to service scanner
│   │   ├── hypothesis_router.py          # Phase 3: Domain hypothesis routing
│   │   ├── falsification.py              # Phase 4: Active falsification engine
│   │   ├── abstain.py                    # Phase 5: Healthy-network abstain logic
│   │   ├── root_cause.py                 # Phase 6: Ranked root cause synthesis
│   │   ├── remediation.py                # Phase 7: Guarded remediation planner
│   │   └── orchestrator.py               # Main agent control loop with turn budget
│   │
│   ├── baselines/                        # Five comparative baselines
│   │   ├── zero_shot.py                  # Baseline 1: Single turn, no tools
│   │   ├── react_agent.py                # Baseline 2: Standard NIKA ReAct loop
│   │   ├── coding_agent.py               # Baseline 3: Claude Code style python scripts
│   │   ├── sade_style.py                 # Baseline 4: Layered scan without falsification
│   │   └── scripted_rules.py             # Baseline 5: Deterministic threshold rules
│   │
│   ├── data/                             # Data and environment modules
│   │   ├── loader.py                     # Incident dataset synthesizer and loader
│   │   ├── healthy_controls.py           # False-premise ticket generator (5 personas)
│   │   ├── fault_family_index.py         # Symptom to fault family dictionary
│   │   ├── topology_graph.py             # NetworkX topology generator
│   │   ├── mock_network_env.py           # Telemetry emulator for CLI tools
│   │   └── preprocessing.py              # Fault audit and 500-token trimmer
│   │
│   ├── experiments/                      # Experimental evaluation modules
│   │   ├── runner.py                     # Multi-scenario experimental runner and judge
│   │   ├── metrics.py                    # 9 canonical metric group calculations
│   │   ├── statistical_tests.py          # 95% bootstrap CIs and Wilcoxon tests
│   │   ├── ablation.py                   # 5-component ablation experiment suite
│   │   └── error_analysis.py             # Kim et al. 12-pitfall taxonomy classifier
│   │
│   └── visualization/                    # Publication charts generator
│       └── plots.py                      # Matplotlib script generating 8 figures
│
├── tests/                                # Test suite (20 automated unit tests)
│   ├── test_data_loader.py               # Tests for loader, audit, and mock env
│   ├── test_agent_phases.py              # Tests for all 7 agent phases
│   ├── test_baselines.py                 # Tests for all 5 baseline agents
│   ├── test_metrics.py                   # Tests for metrics and statistical tests
│   └── test_reproducibility.py           # End-to-end integration test
│
├── results/                              # Generated experimental CSV outputs
│   ├── fault_audit.csv                   # Injection verification log
│   ├── raw_runs.csv                      # All 720 individual run logs
│   ├── metrics_summary.csv               # Aggregated metrics and 95% CIs
│   ├── statistical_tests.csv             # Paired Wilcoxon test p-values
│   ├── ablation_results.csv              # Component ablation metrics
│   └── failure_taxonomy.csv              # Pitfall classification counts
│
├── figures/                              # Generated high-resolution charts (PNG)
│   ├── fig1_main_performance_comparison.png
│   ├── fig2_accuracy_vs_topology_size.png
│   ├── fig3_cost_vs_rca_f1_pareto.png
│   ├── fig4_root_cause_confusion_matrix.png
│   ├── fig5_ablation_component_drop.png
│   ├── fig6_transfer_generalization.png
│   ├── fig7_token_usage_breakdown.png
│   └── fig8_no_submission_rates.png
│
└── docs/                                 # Documentation and final report
    ├── preprocessing.md                  # Preprocessing and audit documentation
    ├── baselines.md                      # Baseline specifications and settings
    ├── comparison_with_existing.md       # Benchmarking against NIKA and SADE
    ├── error_analysis.md                 # Qualitative failure analysis and traces
    └── Phase3_Report.md                  # Complete final academic research report
```

---

## 6. Commands to Run, Test, and Debug

### A. Environment Installation
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

### B. Run the Full Pipeline (One Command)
Run all 720 benchmark evaluations, 60 component ablations, statistical tests, error taxonomy, and figure generation:
```bash
python run_all.py --config configs/experiment_config.yaml
```

To run a fast test run with fewer incidents:
```bash
python run_all.py --config configs/experiment_config.yaml --num_incidents 12 --num_ablations 6
```

### C. Run All Unit Tests
Run the entire Pytest test suite (20 tests covering data, agent phases, baselines, metrics, and reproducibility):
```bash
pytest tests/
```

### D. Run Specific Component Tests (Debugging)
To debug and test individual parts of the system:

1. Test data loader, fault audit, and network emulator:
   ```bash
   pytest tests/test_data_loader.py -v
   ```

2. Test the 7 individual agent phases and orchestrator:
   ```bash
   pytest tests/test_agent_phases.py -v
   ```

3. Test the five comparative baselines:
   ```bash
   pytest tests/test_baselines.py -v
   ```

4. Test metrics calculation and paired Wilcoxon statistical tests:
   ```bash
   pytest tests/test_metrics.py -v
   ```

5. Test end-to-end pipeline reproducibility:
   ```bash
   pytest tests/test_reproducibility.py -v
   ```

### E. Interactive Debugging in Python
You can test the agent interactively in Python on a specific incident:
```python
from code.data.loader import IncidentDataset
from code.data.mock_network_env import MockNetworkEnv
from code.agent.orchestrator import TroubleshootingAgent

# 1. Load sample dataset
mgr = IncidentDataset()
incidents = mgr.generate_benchmark_dataset(total_target=10)
sample_inc = incidents[0]

# 2. Build live network environment
env = MockNetworkEnv(
    scenario=sample_inc["scenario"],
    topology_size=sample_inc["topology_size"],
    fault_injected=sample_inc["ground_truth_has_fault"],
    fault_family=sample_inc["ground_truth_fault_family"],
    faulty_device=sample_inc["ground_truth_device"]
)

# 3. Run troubleshooting agent
agent = TroubleshootingAgent()
result = agent.troubleshoot(sample_inc, env)

print("Detected:", result["detected"])
print("Localized Device:", result["localized_device"])
print("Root Cause:", result["root_cause"])
print("Confidence:", result["confidence"])
print("Turns Used:", result["turns_used"])
print("Remediation Plan:", result["remediation"])
```

### F. Re-Generate Figures Only
To re-generate all 8 publication figures from existing results:
```python
from code.visualization.plots import PlotGenerator
plotter = PlotGenerator(figures_dir="figures")
plotter.generate_all_plots(
    raw_runs_path="results/raw_runs.csv",
    metrics_summary_path="results/metrics_summary.csv",
    ablation_results_path="results/ablation_results.csv"
)
```

---

## 7. Key Benchmark Findings

1. False-Alarm Elimination:
   The proposed agent reduced the false positive rate on healthy networks from 100% (in ReAct, SADE, and Coding baselines) down to 0.0%, completely stopping false alarms on normal networks.

2. Cost and Token Efficiency:
   The proposed agent consumes an average of 1,915 input tokens per session ($0.0138 per incident), making it over 100 times cheaper than SADE (~$1.44 per incident) while achieving higher localization accuracy.

3. Topology Scaling:
   Context bounding prevents context saturation. When scaling from 11-node to 101-node topologies, the proposed agent maintains over 65% localization accuracy, while plain ReAct agents drop sharply.

4. Component Ablations:
   Removing falsification probes causes a 29.1% drop in RCA F1 score. Removing the abstain option causes false positive rates to jump to 100%. Removing phase gating or skills drops RCA F1 to near zero.

---

## 8. License

This project is licensed under the MIT License. See the LICENSE file for details.
