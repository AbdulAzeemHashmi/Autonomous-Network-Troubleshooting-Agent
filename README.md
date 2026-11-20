<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=220&section=header&text=Autonomous%20Network%20Troubleshooting%20Agent&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Find%20the%20real%20fault.%20Ignore%20the%20false%20alarm.&descAlignY=58&descSize=18" alt="Header banner" width="100%"/>

<a href="https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=800&color=2C9CDB&center=true&vCenter=true&width=760&lines=Now+Open+Source+and+Public+on+GitHub;7-Phase+AI+Agent+for+Network+Faults;Powered+by+Google+Gemini+API;85.0%25+Detection+%7C+87.4%25+RCA+F1+(credited);0.0%25+False+Positive+Rate+on+Healthy+Networks;120+Incidents+%7C+60+Ablations+%7C+Phase+4+Paper" alt="Typing animation"/>
</a>

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-3.7-orange?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Tests-32%20passing-success?style=for-the-badge&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Repo](https://img.shields.io/badge/Repository-Public-brightgreen?style=for-the-badge&logo=github)

![Detection Accuracy](https://img.shields.io/badge/Detection%20Accuracy-85.0%25-brightgreen?style=flat-square)
![RCA F1](https://img.shields.io/badge/RCA%20F1%20(credited)-87.4%25-brightgreen?style=flat-square)
![Fault Recall](https://img.shields.io/badge/Fault%20Recall-80.0%25-brightgreen?style=flat-square)
![False Positive Rate](https://img.shields.io/badge/False%20Positive%20Rate-0.0%25-brightgreen?style=flat-square)
![Cost](https://img.shields.io/badge/Cost%20per%20Session-%240.000296-brightgreen?style=flat-square)
![Incidents](https://img.shields.io/badge/Benchmark%20Incidents-120-informational?style=flat-square)
![Ablation Runs](https://img.shields.io/badge/Ablation%20Runs-60-informational?style=flat-square)
![Topologies](https://img.shields.io/badge/Topologies-15-informational?style=flat-square)

<br/>

![Stars](https://img.shields.io/github/stars/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent?style=flat-square&logo=github&color=yellow)
![Forks](https://img.shields.io/github/forks/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent?style=flat-square&logo=github&color=blue)
![Issues](https://img.shields.io/github/issues/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent?style=flat-square&logo=github&color=orange)
![Last Commit](https://img.shields.io/github/last-commit/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent?style=flat-square&logo=git&color=success)
![Repo Size](https://img.shields.io/github/repo-size/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent?style=flat-square&color=lightgrey)
![Top Language](https://img.shields.io/github/languages/top/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent?style=flat-square&logo=python&logoColor=white)

<br/>

<a href="#7-quick-start"><img src="https://img.shields.io/badge/Get%20Started-Quick%20Start-2C9CDB?style=for-the-badge&logo=rocket&logoColor=white" alt="Get started"/></a>
<a href="#8-key-benchmark-findings"><img src="https://img.shields.io/badge/See%20Results-Benchmarks-2da44e?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="See results"/></a>
<a href="#9-contributing"><img src="https://img.shields.io/badge/Join%20In-Contribute-bf8700?style=for-the-badge&logo=github&logoColor=white" alt="Contribute"/></a>
<a href="https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent/stargazers"><img src="https://img.shields.io/github/stars/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent?style=for-the-badge&logo=github&label=Stars&color=yellow" alt="Live GitHub stars count"/></a>

<br/><br/>

**Course:** Computer Networks (CS-3001) | **University:** FAST National University of Computer and Emerging Sciences (NUCES)

</div>

---

## Table of Contents

| # | Section | # | Section |
|---|---------|---|---------|
| 1 | [Project Overview](#1-project-overview) | 8 | [Key Benchmark Findings](#8-key-benchmark-findings) |
| 2 | [How the Agent Works](#2-how-the-agent-works) | 9 | [Contributing](#9-contributing) |
| 3 | [Project Phases Recap](#3-project-phases-recap) | 10 | [Security and API Keys](#10-security-and-api-keys) |
| 4 | [Technology Stack](#4-technology-stack) | 11 | [How to Cite](#11-how-to-cite) |
| 5 | [Dataset and Topologies](#5-dataset-and-topologies) | 12 | [Team](#12-team) |
| 6 | [Folder Structure](#6-folder-structure) | 13 | [License](#13-license) |
| 7 | [Quick Start](#7-quick-start) | | |

---

## 1. Project Overview

> **Good news:** This repository is now **public**. Anyone can read the code, run the experiments, and build on this work.

Modern computer networks are big, different from each other, and easy to break. When something fails, finding the root cause fast can save a lot of money.

Large Language Model (LLM) agents can run commands like `ping`, `traceroute`, `show ip route`, and `ss` to debug outages. But recent studies (NIKA by Wang et al. 2025, and Fault-Bench by Tseng et al. 2026) found big problems with standard agents:

| Problem | What happens |
|---------|--------------|
| **Over-diagnosis** | Standard agents almost always find a fault, even on a healthy network. False alarms reach up to 100%. |
| **High cost** | Agents with no limits cost about $1.44 per incident in tokens. |
| **Context dilution** | Large networks flood the context window, so the diagnosis fails. |

This project builds a **7-Phase Autonomous Network Troubleshooting Agent** that:

- Checks the ticket before starting a deep investigation.
- Scans layer by layer, from Layer 2 up to the Service layer.
- Runs counter probes to disprove wrong guesses.
- Abstains (says "no fault found") when the network is healthy.
- Connects to Google Gemini models (Gemini 1.5 Flash, Gemini 2.0 Flash), which have generous free tier quotas.
- Is tested against 5 baselines across 120 incidents (6 agents x 120 = 720 total runs) and 60 ablation runs.
- Builds a publication quality PDF research report automatically.
- Includes a full Phase 4 research paper in Springer Nature format with statistical analysis and reproducibility scripts.

### Why this project is useful

| Who you are | How this repository helps you |
|-------------|-------------------------------|
| **Student** | Learn how an AI agent can debug a network step by step. |
| **Researcher** | Reuse the benchmark, the 5 baselines, and the statistics scripts. |
| **Network engineer** | See how falsification probes reduce false alarms. |
| **Developer** | Study a clean Python agent with 32 passing tests. |

---

## 2. How the Agent Works

The agent moves through seven phases, one after the other.

```mermaid
flowchart TD
    A([Incident Ticket]) --> B["Phase 1<br/>Ticket Validator<br/>Can the symptom be reproduced?"]
    B -- "Invalid ticket on healthy network" --> X(["FAST ABSTAIN<br/>Cost: $0.00"])
    B -- "Ticket looks real" --> C["Phase 2<br/>Layered Evidence Scan<br/>L2 then L3 then L4 then Service"]
    C --> D["Phase 3<br/>Hypothesis Router<br/>Maps symptoms to 7 fault families"]
    D --> E["Phase 4<br/>Falsification Probes<br/>Try to disprove each guess"]
    E --> F{"Does any<br/>fault survive?"}
    F -- No --> G(["Phase 5<br/>Abstain: No fault found"])
    F -- Yes --> H["Phase 6<br/>Root Cause Synthesis<br/>Rank causes with confidence"]
    H --> I["Phase 7<br/>Safe Remediation<br/>Pre-checks, fix, rollback"]
    I --> J([Final Diagnosis and Human Approval Gate])

    style A fill:#1f6feb,color:#fff,stroke:#1f6feb
    style X fill:#2da44e,color:#fff,stroke:#2da44e
    style G fill:#2da44e,color:#fff,stroke:#2da44e
    style J fill:#bf8700,color:#fff,stroke:#bf8700
```

### The seven fault families

The agent knows seven main types of network faults.

| # | Fault family | What it means |
|:-:|--------------|---------------|
| 1 | `link_failure` | Interface down, line protocol down, carrier lost. |
| 2 | `congestion` | High link use, full buffer queues, high round trip time. |
| 3 | `routing_misconfiguration` | Missing prefix, BGP route flapping, routing loop. |
| 4 | `service_failure` | Daemon crashed, port closed, connection refused. |
| 5 | `acl_firewall_block` | Packets dropped by an ACL or firewall rule. |
| 6 | `hardware_transceiver` | High CRC error rate, low optical Rx power. |
| 7 | `dns_failure` | Name resolution failure, DNS query timeout. |

---

## 3. Project Phases Recap

<details>
<summary><b>Click to open: Phase 1, Literature Review</b></summary>

<br/>

- Reviewed 3 recent papers (Huang et al. 2026, Mwangi et al. 2026, Rawas and Samala 2026).
- Found 3 research gaps: no standard benchmarks, missing false positive metrics, and weak transfer testing.

</details>

<details>
<summary><b>Click to open: Phase 2, Methodology Design</b></summary>

<br/>

- Expanded the review to 9 papers (including BiAn, Confucius, RCLAgent, NIKA, SADE, Fault-Bench, and Kim et al.).
- Defined the 7-phase agent design with ticket validation and falsification.
- Designed 9 metric groups, scenario splits, and healthy network controls.

</details>

<details>
<summary><b>Click to open: Phase 3, Implementation and Experimental Evaluation</b></summary>

<br/>

- Built the full 7-phase agent and 5 baselines in Python.
- Added a Google Gemini LLM API client with resilient offline fallback.
- Ran 720 benchmark evaluations across 120 incidents and 15 network scenarios.
- Ran 60 ablation studies across 5 component removals.
- Generated 9 publication grade figures at 300 DPI.
- Built an automatic ReportLab PDF compiler for the academic evaluation report.

</details>

<details open>
<summary><b>Click to open: Phase 4, Research Paper Writing and Publication (Final Phase)</b></summary>

<br/>

- Authored a complete, self-contained publication research paper formatted in the Springer Nature `sn-jnl` template (two column layout, `sn-basic` citation style).
- Resolved device name parsing collisions using whole token regex word boundary matching, lifting fault recall to 80.0% (72/90) and detection accuracy to 85.0% (102/120).
- Performed rigorous statistical analysis: 5,000 bootstrap resamples for 95% confidence intervals and exact two sided McNemar tests on discordant incident pairs.
- Conducted a ground truth leakage audit (zero discrepancy when healthy flags are hidden).
- Harmonized root cause evaluation labels (`"healthy"` vs `"none"`), measuring both raw logged F1 (0.691) and credited abstention F1 (0.874).
- Packaged the complete LaTeX source, reproducibility scripts, vector figures, and compiled PDF (`Phase4_Research_Paper.pdf`).

</details>

---

## 4. Technology Stack

<div align="center">

<img src="https://skillicons.dev/icons?i=python,github,git,vscode,linux&theme=dark" alt="Core tools"/>

</div>

| Area | Tool | Version or details |
|------|------|--------------------|
| Language | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) | 3.10+ (tested on 3.12) |
| LLM backend | ![Gemini](https://img.shields.io/badge/-Google%20Gemini-4285F4?logo=google&logoColor=white) | gemini-1.5-flash, gemini-2.0-flash, gemini-1.5-pro |
| Network modeling | ![NetworkX](https://img.shields.io/badge/-NetworkX-orange) | 3.7 graph library |
| Data analysis | ![Pandas](https://img.shields.io/badge/-Pandas-150458?logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/-NumPy-013243?logo=numpy&logoColor=white) ![SciPy](https://img.shields.io/badge/-SciPy-8CAAE6?logo=scipy&logoColor=white) ![Scikit-Learn](https://img.shields.io/badge/-Scikit--Learn-F7931E?logo=scikitlearn&logoColor=white) | Statistical tests, confidence intervals, F1 scores |
| Plotting | ![Matplotlib](https://img.shields.io/badge/-Matplotlib-11557c) | 9 publication figures at 300 DPI |
| PDF export | ReportLab | Academic report compiler (Phase 3 report) |
| Research paper | LaTeX (Springer Nature sn-jnl) | Phase 4 publication paper with BibTeX references |
| Testing | ![Pytest](https://img.shields.io/badge/-Pytest-0A9EDC?logo=pytest&logoColor=white) | 32 automated unit tests |

---

## 5. Dataset and Topologies

The evaluation uses network topologies from three sources: NIKA, Fault-Bench, and the course benchmark.

| Scenario name | Source | Topology type | Nodes |
|---------------|--------|---------------|:-----:|
| `datacenter_clos` | NIKA | 2-tier Leaf-Spine CLOS | 12 |
| `campus_network` | NIKA | Core, Distribution, Access | 24 |
| `isp_backbone` | NIKA | Multi-ring ISP mesh | 18 |
| `sdn_cloud_fabric` | NIKA | OpenFlow controller and switches | 16 |
| `p4_testbed` | NIKA | Programmable data plane | 8 |
| `enterprise_branch` | Fault-Bench | Dual-homed branch router | 10 |
| `leaf_spine_clos` | Fault-Bench | 3-tier CLOS data center | 32 |
| `multihomed_edge` | Fault-Bench | Edge multi-homing | 14 |
| `transit_wan` | Fault-Bench | Transit WAN backbone | 22 |
| `sdn_hybrid` | Fault-Bench | Hybrid legacy and SDN | 20 |
| `bgp_peering_exchange` | Fault-Bench | Internet Exchange Point (IXP) | 16 |
| `datacenter_dci` | Fault-Bench | Data Center Interconnect | 28 |
| `campus_core_access` | Fault-Bench | Large campus network | 101 |
| `abilene_backbone` | Course Benchmark | Internet2 Abilene backbone | 11 |
| `netman_aiops` | Course Benchmark | Enterprise multi-tier (NetManAIOps) | 16 |

---

## 6. Folder Structure

```text
Autonomous-Network-Troubleshooting-Agent/
├── Phase1_Literature_Review_Report.pdf   # Phase 1 submission report
├── Phase_2_Deliverables.pdf              # Phase 2 methodology report
├── Phase4_Research_Paper.pdf             # Phase 4 compiled research paper (PDF)
├── LICENSE                               # MIT License
├── README.md                             # Project documentation and guide
├── requirements.txt                      # Python dependencies
├── pytest.ini                            # Pytest configuration
├── conftest.py                           # Root path configuration
├── export_pdf.py                         # ReportLab PDF compiler (Phase 3 report)
├── interactive_cli.py                    # Interactive single-incident demo
├── run_experiments.bat                   # One-click Windows batch runner
├── run_experiments.ps1                   # One-click Windows PowerShell runner
├── run_all.py                            # Single-command end-to-end run
│
├── Phase4_Paper_LaTeX_Source/            # Phase 4: full LaTeX source package
│   └── phase4_paper_source/
│       ├── paper.tex                     # Springer Nature sn-jnl LaTeX source
│       ├── references.bib                # BibTeX bibliography
│       ├── sn-jnl.cls                    # Springer Nature journal class file
│       ├── sn-basic.bst                  # Springer Nature citation style
│       ├── README.md                     # Compilation instructions
│       ├── analysis/                     # Reproducibility and stats scripts
│       │   ├── phase4_analysis.py        # Bootstrap CIs, McNemar tests, figures
│       │   ├── ablation_rerun.py         # Label-harmonized ablation re-run
│       │   ├── leakage_audit.py          # Ground-truth leakage check (0 discrepancies)
│       │   └── build_tables.py           # LaTeX table rows and tokens.json
│       ├── data/                         # Intermediate data for the paper
│       │   ├── phase4_stats.json         # Full 120-incident stats with CIs
│       │   ├── ablation_stats.json       # Ablation summary (60 runs each)
│       │   ├── ablation_raw.csv          # Raw ablation measurements
│       │   ├── main_metrics_point.csv    # Point-estimate table
│       │   ├── proposed_failure_attribution.csv
│       │   ├── scenario_table.json       # Per-scenario accuracy breakdown
│       │   └── tokens.json               # Token-cost breakdown table
│       ├── figures/                      # Vector figures embedded in paper
│       │   ├── fig_main_results.pdf      # Main performance comparison
│       │   ├── fig_ablation.pdf          # Component ablation drop chart
│       │   ├── fig_failure_attribution.pdf
│       │   └── fig_split_transfer.pdf    # Dev vs. held-out transfer plot
│       └── results/                      # Raw CSVs scoped to the paper
│           ├── raw_runs.csv
│           └── ablation_results.csv
│
├── configs/                              # System configurations
│   ├── experiment_config.yaml            # Scenarios, topology sizes, token limits
│   ├── models.yaml                       # LLM backbone definitions and pricing
│   └── splits.json                       # Whole-scenario train/test split IDs
│
├── code/                                 # Implementation source code
│   ├── agent/                            # Proposed 7-phase agent
│   │   ├── llm_client.py                 # Google Gemini API wrapper (importlib, no hardcoded key)
│   │   ├── ticket_validator.py           # Phase 1: Ticket validation (word-boundary regex)
│   │   ├── evidence_scanner.py           # Phase 2: Layered scan (L2 to Service)
│   │   ├── hypothesis_router.py          # Phase 3: Fault family routing
│   │   ├── falsification.py              # Phase 4: Counter probes
│   │   ├── abstain.py                    # Phase 5: Abstain decision
│   │   ├── root_cause.py                 # Phase 6: Ranked root causes
│   │   ├── remediation.py                # Phase 7: Validated fix playbooks
│   │   └── orchestrator.py               # Main agent loop (word-boundary regex fix)
│   ├── baselines/                        # 5 comparative baselines (all use word-boundary regex)
│   │   ├── zero_shot.py                  # Baseline 1: Zero-shot LLM
│   │   ├── react_agent.py                # Baseline 2: Standard ReAct
│   │   ├── coding_agent.py               # Baseline 3: Generic coding agent
│   │   ├── sade_style.py                 # Baseline 4: SADE style agent
│   │   └── scripted_rules.py             # Baseline 5: Fixed script rules
│   ├── data/                             # Data loaders and network simulation
│   │   ├── fault_family_index.py         # Symptom to fault family dictionary
│   │   ├── topology_graph.py             # NetworkX topology generator
│   │   ├── mock_network_env.py           # CLI telemetry simulator
│   │   ├── healthy_controls.py           # False premise ticket generator
│   │   ├── loader.py                     # Incident dataset manager
│   │   └── preprocessing.py              # Fault audit and token trimming
│   ├── experiments/                      # Experiment runner and evaluation
│   │   ├── runner.py                     # Benchmark runner and LLM judge
│   │   ├── metrics.py                    # 9 metric groups (outputs rca_f1_macro_raw too)
│   │   ├── statistical_tests.py          # Bootstrap CI and Wilcoxon tests
│   │   ├── ablation.py                   # 5-component ablation studies
│   │   └── error_analysis.py             # Kim et al. 12-pitfall taxonomy
│   └── visualization/                    # Publication figure generator
│       └── plots.py                      # Matplotlib visualization code
│
├── docs/                                 # Documentation and final report
│   ├── Phase3_Report.md                  # Full academic report (Markdown)
│   ├── Phase3_Report.pdf                 # Formatted academic report (PDF)
│   ├── baselines.md                      # Baseline descriptions
│   ├── comparison_with_existing.md       # Comparison with published papers
│   ├── error_analysis.md                 # Failure taxonomy report
│   └── preprocessing.md                  # Audit and split documentation
│
├── figures/                              # Generated 300 DPI figures (Phase 3)
│   ├── fig1_main_performance_comparison.png
│   ├── fig2_accuracy_vs_topology_size.png
│   ├── fig3_cost_vs_rca_f1_pareto.png
│   ├── fig4_root_cause_confusion_matrix.png
│   ├── fig5_ablation_component_drop.png
│   ├── fig6_transfer_generalization.png
│   ├── fig7_token_usage_breakdown.png
│   ├── fig8_no_submission_rates.png
│   └── fig9_robustness_stress_testing.png
│
├── prompts/                              # Phase-specific prompt templates
│   ├── judge.txt                         # Fault-Bench LLM judge prompt
│   ├── phase1_ticket_validator.txt
│   ├── phase2_evidence_scan.txt
│   ├── phase3_hypothesis_router.txt
│   ├── phase4_falsification.txt
│   ├── phase6_root_cause.txt
│   └── phase7_remediation.txt
│
├── results/                              # Output CSV files
│   ├── raw_runs.csv                      # Per-run records (all 6 agents x 120 incidents)
│   ├── metrics_summary.csv               # Aggregate metrics (includes rca_f1_macro_raw column)
│   ├── statistical_tests.csv             # Wilcoxon and McNemar test results
│   ├── ablation_results.csv              # Component ablation metrics (60 runs each)
│   ├── robustness_results.csv            # Scale, persona, and sensitivity stress tests
│   ├── failure_taxonomy.csv              # Error classification counts
│   └── fault_audit.csv                   # Preprocessing audit logs
│
└── tests/                                # Automated test suite (32 tests, all passing)
    ├── test_agent_phases.py              # Phase 1 to 7 unit tests
    ├── test_baselines.py                 # All 5 baseline tests
    ├── test_data_loader.py               # Loader, graph, and env tests
    ├── test_llm_client.py                # Gemini client and judge tests
    ├── test_metrics.py                   # Metric and runner tests
    ├── test_robustness.py                # Robustness and sensitivity tests
    └── test_reproducibility.py           # End-to-end pipeline test
```

---

## 7. Quick Start

> **Tip:** Run all commands from the root folder of the repository.

### Step 1: Clone the public repository

Anyone can now download the code. No login or special access is needed.

```bash
git clone https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent.git
cd Autonomous-Network-Troubleshooting-Agent
```

### Step 2: Create a virtual environment (recommended)

```bash
# Create the environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux or macOS
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the full pipeline (one command)

This runs 720 benchmark evaluations, 60 ablations, robustness stress tests, statistical tests, error classification, 9 publication figures, and PDF report compilation.

```bash
# Python runner
python run_all.py --config configs/experiment_config.yaml

# Or one-click on Windows PowerShell:
.\run_experiments.ps1

# Or one-click on Windows CMD:
run_experiments.bat
```

### Step 5: Run with the live Google Gemini API

Use live Gemini calls for ticket validation, zero-shot reasoning, and LLM judge scoring. You can get a free key from Google AI Studio.

```bash
python run_all.py --use_live_llm --gemini_model gemini-1.5-flash
```

Or pass your API key on the command line:

```bash
python run_all.py --use_live_llm --gemini_api_key "YOUR_GEMINI_KEY"
```

> **Security note:** The repository is public. Never commit your real API key to GitHub. See [Security and API Keys](#10-security-and-api-keys).

### Step 6: Run unit tests

All 32 automated unit tests run with:

```bash
pytest tests/ -v
```

### Step 7: Run the interactive demo

Troubleshoot one incident step by step on any of the 15 topologies.

```bash
# Troubleshoot the Internet2 Abilene backbone
python interactive_cli.py --scenario abilene_backbone

# Test a healthy network with a false alarm ticket
python interactive_cli.py --scenario abilene_backbone --healthy

# Test with the live Google Gemini API
python interactive_cli.py --scenario netman_aiops --use_live_llm
```

### Step 8: Export the PDF report only

```bash
python export_pdf.py
```

The PDF is saved to `docs/Phase3_Report.pdf`.

### Read the papers without running any code

| Document | File |
|----------|------|
| Phase 1 literature review | [Phase1_Literature_Review_Report.pdf](Phase1_Literature_Review_Report.pdf) |
| Phase 2 methodology | [Phase_2_Deliverables.pdf](Phase_2_Deliverables.pdf) |
| Phase 3 evaluation report | [docs/Phase3_Report.pdf](docs/Phase3_Report.pdf) |
| Phase 4 research paper | [Phase4_Research_Paper.pdf](Phase4_Research_Paper.pdf) |

---

## 8. Key Benchmark Findings

<div align="center">

| Detection Acc | Fault Recall | RCA F1 (credited) | False Positive Rate | Cost per Session | Input Tokens |
|:-------------:|:------------:|:-----------------:|:-------------------:|:----------------:|:------------:|
| **85.0%** | **80.0%** | **0.874** | **0.0%** | **$0.000296** | **1,905** |

</div>

### 1. Comparison with baselines

| Model | Detection Acc | Fault Recall | RCA F1 (credited) | RCA F1 (raw) | False Positive Rate | Cost per Session |
|-------|:-------------:|:------------:|:-----------------:|:------------:|:-------------------:|:----------------:|
| **Proposed 7-Phase Agent** | **0.850** | **0.800** | **0.874** | **0.691** | **0.0%** | **$0.000296** |
| Scripted Rules | 0.767 | 0.689 | 0.754 | 0.595 | 0.0% | $0.000000 |
| SADE-Style Baseline | 0.750 | 1.000 | 0.636 | 0.636 | 100.0% | $0.001095 |
| Zero-Shot LLM | 0.750 | 1.000 | 0.513 | 0.513 | 100.0% | $0.000029 |
| ReAct Agent | 0.750 | 1.000 | 0.024 | 0.024 | 100.0% | $0.000381 |
| Generic Coding Agent | 0.750 | 1.000 | 0.024 | 0.024 | 100.0% | $0.000885 |

```mermaid
xychart-beta
    title "RCA F1 Score credited (higher is better)"
    x-axis ["Proposed", "Scripted", "SADE-Style", "Zero-Shot", "ReAct", "Coding"]
    y-axis "RCA F1" 0 --> 1.0
    bar [0.874, 0.754, 0.636, 0.513, 0.024, 0.024]
```

```mermaid
xychart-beta
    title "False Positive Rate on Healthy Networks (percent, lower is better)"
    x-axis ["Proposed", "Scripted", "SADE-Style", "Zero-Shot", "ReAct", "Coding"]
    y-axis "False Positive Rate" 0 --> 100
    bar [0, 0, 100, 100, 100, 100]
```

### 2. Research gaps addressed

| Gap | Result |
|-----|--------|
| **Sub-Gap A: Over-diagnosis** | The agent achieved **0.0% False Positive Rate** on healthy network controls. ReAct, Coding, and SADE baselines had 100% false alarms. |
| **Sub-Gap B: Cost and tokens** | The agent used **1,905 input tokens ($0.000296 per session)** on average. That is drastically cheaper than unconstrained agents (up to $1.44 in SADE). |
| **Sub-Gap C: Transferability** | The agent achieved **held-out F1 = 1.0** on unseen topologies (dev F1 = 0.667), showing strong transfer to new network environments. |

### 3. Component ablations

| Component removed | Detection Acc | RCA F1 (credited) | False Positive Rate | Effect observed |
|-------------------|:-------------:|:-----------------:|:-------------------:|-----------------|
| Falsification probes | 0.700 | 0.489 | 0.0% | RCA F1 drops by **43.7%** (most critical component) |
| Abstain option | 0.700 | 0.868 | **100.0%** | False positive rate jumps to 100% |
| Phase gating | 0.700 | 0.023 | 100.0% | RCA F1 collapses to near zero |
| Skills (prompt templates) | 1.000 | 0.156 | 0.0% | RCA F1 drops by **82.0%** |
| Evidence filtering | 0.833 | 0.868 | 0.0% | Minimal change (filtering is redundant at small scale) |

---

## 9. Contributing

Now that the repository is public, contributions are welcome. You can fix a bug, improve the docs, add a new topology, or test a new baseline.

### How to contribute

```mermaid
flowchart LR
    A["Fork the repo"] --> B["Create a branch"]
    B --> C["Make your changes"]
    C --> D["Run pytest"]
    D --> E["Open a Pull Request"]
    E --> F(["Review and merge"])

    style A fill:#1f6feb,color:#fff,stroke:#1f6feb
    style F fill:#2da44e,color:#fff,stroke:#2da44e
```

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/Autonomous-Network-Troubleshooting-Agent.git

# 2. Create a new branch
git checkout -b my-new-feature

# 3. Make your changes, then run all tests
pytest tests/ -v

# 4. Commit and push
git add .
git commit -m "Add my new feature"
git push origin my-new-feature
```

After that, open a Pull Request on GitHub and describe what you changed.

### Simple contribution rules

| Rule | Why it matters |
|------|----------------|
| All 32 tests must pass before you open a Pull Request. | It keeps the main branch stable. |
| Add a test for every new feature or bug fix. | It protects the work from future breaks. |
| Keep code and comments simple and clear. | It helps new readers learn faster. |
| Never include API keys, passwords, or private data. | The repository is public. |

### Found a bug or have an idea?

Open an issue on the [Issues page](https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent/issues). Please include:

- What you did.
- What you expected to happen.
- What actually happened.
- Your Python version and operating system.

---

## 10. Security and API Keys

<div align="center">

![Security](https://img.shields.io/badge/Security-Keep%20Your%20Keys%20Private-red?style=for-the-badge&logo=letsencrypt&logoColor=white)

</div>

Because this repository is public, everyone can see every file and every past commit. Please follow these simple tips.

| Tip | What to do |
|-----|------------|
| **Never commit a key** | Do not paste your Gemini API key inside any file. Pass it only on the command line. |
| **Check before you push** | Run `git status` and `git diff` to confirm no secret is included. |
| **Ignore private files** | Add files like `.env` to your `.gitignore` file. |
| **Rotate a leaked key** | If a key was ever pushed, delete it in Google AI Studio and create a new one. Removing it from a later commit is not enough, because the old commit still shows it. |
| **Use the free tier wisely** | The code has an offline fallback, so you can run all experiments without a key. |

The Gemini client in `code/agent/llm_client.py` has no hardcoded key, so it is safe to read and reuse.

---

## 11. How to Cite

If this project helps your study or research, please give it a star on GitHub and cite it.

```bibtex
@misc{azeem2026autonomousnetwork,
  title        = {Autonomous Network Troubleshooting Agent: A 7-Phase LLM Agent with Ticket Validation and Falsification},
  author       = {Abdul Azeem and Taha Amjad},
  year         = {2026},
  howpublished = {\url{https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent}},
  note         = {FAST-NUCES, Computer Networks (CS-3001)}
}
```

<div align="center">

<a href="https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent/stargazers">
  <img src="https://img.shields.io/github/stars/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent?style=for-the-badge&logo=github&label=Live%20GitHub%20Stars&color=yellow" alt="Live GitHub stars count"/>
</a>

</div>

---

## 12. Team

<div align="center">

<table>
  <tr>
    <td align="center" width="260">
      <a href="https://github.com/AbdulAzeemHashmi">
        <img src="https://github.com/AbdulAzeemHashmi.png?size=120" width="120" height="120" style="border-radius:50%" alt="Abdul Azeem"/>
      </a>
      <br/><br/>
      <b>Abdul Azeem</b>
      <br/>Roll Number: 24I-2013
      <br/>FAST-NUCES
      <br/><br/>
      <a href="https://github.com/AbdulAzeemHashmi">
        <img src="https://img.shields.io/badge/GitHub-AbdulAzeemHashmi-181717?style=for-the-badge&logo=github" alt="Abdul Azeem GitHub"/>
      </a>
    </td>
    <td align="center" width="260">
      <a href="https://github.com/tahaamja">
        <img src="https://github.com/tahaamja.png?size=120" width="120" height="120" style="border-radius:50%" alt="Taha Amjad"/>
      </a>
      <br/><br/>
      <b>Taha Amjad</b>
      <br/>Roll Number: 24K-0007
      <br/>FAST-NUCES
      <br/><br/>
      <a href="https://github.com/tahaamja">
        <img src="https://img.shields.io/badge/GitHub-tahaamja-181717?style=for-the-badge&logo=github" alt="Taha Amjad GitHub"/>
      </a>
    </td>
  </tr>
</table>

<br/>

### Contributors

<a href="https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent" alt="Contributors"/>
</a>

<br/><br/>

[![Project Repository](https://img.shields.io/badge/Project%20Repository-Autonomous--Network--Troubleshooting--Agent-2C5364?style=for-the-badge&logo=github)](https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent)

</div>

---

## 13. License

This project is licensed under the **MIT License**. You are free to use, copy, change, and share the code. Please keep the license notice and give credit to the authors. See the [LICENSE](LICENSE) file for details.

<div align="center">

<br/>

![Thanks](https://img.shields.io/badge/Thanks%20for%20visiting-Star%20the%20repo%20if%20you%20like%20it-2C9CDB?style=for-the-badge&logo=github&logoColor=white)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a43,100:0f2027&height=120&section=footer" alt="Footer wave" width="100%"/>

</div>