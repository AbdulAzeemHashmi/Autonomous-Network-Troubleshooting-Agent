<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=220&section=header&text=Autonomous%20Network%20Troubleshooting%20Agent&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Find%20the%20real%20fault.%20Ignore%20the%20false%20alarm.&descAlignY=58&descSize=18" alt="Header banner" width="100%"/>

<a href="https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=800&color=2C9CDB&center=true&vCenter=true&width=760&lines=7-Phase+AI+Agent+for+Network+Faults;Powered+by+Google+Gemini+API;0.0%25+False+Positive+Rate+on+Healthy+Networks;Only+%240.0138+per+Troubleshooting+Session;720+Benchmark+Runs+and+60+Ablations" alt="Typing animation"/>
</a>

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-3.7-orange?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Tests-32%20passing-success?style=for-the-badge&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Repo](https://img.shields.io/badge/Repository-Private-lightgrey?style=for-the-badge&logo=github)

![False Positive Rate](https://img.shields.io/badge/False%20Positive%20Rate-0.0%25-brightgreen?style=flat-square)
![Cost](https://img.shields.io/badge/Cost%20per%20Session-%240.0138-brightgreen?style=flat-square)
![Transfer Score](https://img.shields.io/badge/Transfer%20Score-96.3%25-brightgreen?style=flat-square)
![Benchmark Runs](https://img.shields.io/badge/Benchmark%20Runs-720-informational?style=flat-square)
![Ablation Runs](https://img.shields.io/badge/Ablation%20Runs-60-informational?style=flat-square)
![Topologies](https://img.shields.io/badge/Topologies-15-informational?style=flat-square)

<br/>

**Course:** Computer Networks (CS-3001) | **University:** FAST National University of Computer and Emerging Sciences (NUCES)

</div>

---

## Table of Contents

| # | Section | # | Section |
|---|---------|---|---------|
| 1 | [Project Overview](#1-project-overview) | 6 | [Folder Structure](#6-folder-structure) |
| 2 | [How the Agent Works](#2-how-the-agent-works) | 7 | [Quick Start](#7-quick-start) |
| 3 | [Project Phases Recap](#3-project-phases-recap) | 8 | [Key Benchmark Findings](#8-key-benchmark-findings) |
| 4 | [Technology Stack](#4-technology-stack) | 9 | [Team](#9-team) |
| 5 | [Dataset and Topologies](#5-dataset-and-topologies) | 10 | [License](#10-license) |

---

## 1. Project Overview

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
- Is tested against 5 baselines with 720 benchmark runs and 60 ablations.
- Builds a publication quality PDF research report automatically.

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

<details open>
<summary><b>Click to open: Phase 3, Implementation and Experimental Evaluation (this phase)</b></summary>

<br/>

- Built the full 7-phase agent and 5 baselines in Python.
- Added a Google Gemini LLM API client with an offline fallback.
- Ran 720 benchmark evaluations.
- Ran 60 ablation studies across 5 component removals.
- Made 8 publication grade figures at 300 DPI.
- Built an automatic PDF compiler for the academic report.

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
| Plotting | ![Matplotlib](https://img.shields.io/badge/-Matplotlib-11557c) | 8 publication figures at 300 DPI |
| PDF export | ReportLab | Academic report compiler |
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
├── LICENSE                               # MIT License
├── README.md                             # Project documentation and guide
├── requirements.txt                      # Python dependencies
├── pytest.ini                            # Pytest configuration
├── conftest.py                           # Root path configuration
├── export_pdf.py                         # ReportLab PDF compiler
├── interactive_cli.py                    # Interactive single-incident demo
├── run_all.py                            # Single-command end-to-end run
│
├── configs/                              # System configurations
│   ├── experiment_config.yaml            # Scenarios, topology sizes, token limits
│   ├── models.yaml                       # LLM backbone definitions and pricing
│   └── splits.json                       # Whole-scenario train/test split IDs
│
├── code/                                 # Implementation source code
│   ├── agent/                            # Proposed 7-phase agent
│   │   ├── llm_client.py                 # Google Gemini API wrapper
│   │   ├── ticket_validator.py           # Phase 1: Ticket validation
│   │   ├── evidence_scanner.py           # Phase 2: Layered scan
│   │   ├── hypothesis_router.py          # Phase 3: Fault family routing
│   │   ├── falsification.py              # Phase 4: Counter probes
│   │   ├── abstain.py                    # Phase 5: Abstain decision
│   │   ├── root_cause.py                 # Phase 6: Ranked root causes
│   │   ├── remediation.py                # Phase 7: Validated fix playbooks
│   │   └── orchestrator.py               # Main agent loop
│   ├── baselines/                        # 5 comparative baselines
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
│   │   ├── metrics.py                    # 9 canonical metric groups
│   │   ├── statistical_tests.py          # Bootstrap CI and Wilcoxon tests
│   │   ├── ablation.py                   # 5-component ablation studies
│   │   └── error_analysis.py             # Kim et al. 12-pitfall taxonomy
│   └── visualization/                    # Publication figure generator
│       └── plots.py                      # Matplotlib visualization code
│
├── docs/                                 # Documentation and final report
│   ├── Phase3_Report.md                  # Full academic report
│   ├── Phase3_Report.pdf                 # Formatted academic report PDF
│   ├── baselines.md                      # Baseline descriptions
│   ├── comparison_with_existing.md       # Comparison with published papers
│   ├── error_analysis.md                 # Failure taxonomy report
│   └── preprocessing.md                  # Audit and split documentation
│
├── figures/                              # Generated 300 DPI figures
│   ├── fig1_main_performance_comparison.png
│   ├── fig2_accuracy_vs_topology_size.png
│   ├── fig3_cost_vs_rca_f1_pareto.png
│   ├── fig4_root_cause_confusion_matrix.png
│   ├── fig5_ablation_component_drop.png
│   ├── fig6_transfer_generalization.png
│   ├── fig7_token_usage_breakdown.png
│   └── fig8_no_submission_rates.png
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
│   ├── raw_runs.csv                      # All 720 individual run records
│   ├── metrics_summary.csv               # Aggregate metrics with CIs
│   ├── statistical_tests.csv             # Wilcoxon test results
│   ├── ablation_results.csv              # Component ablation metrics
│   ├── robustness_results.csv            # Scale, persona, and sensitivity stress tests
│   ├── failure_taxonomy.csv              # Error classification counts
│   └── fault_audit.csv                   # Preprocessing audit logs
│
└── tests/                                # Automated test suite (32 tests)
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

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the full pipeline (one command)

This runs 720 benchmark evaluations, 60 ablations, statistical tests, error classification, figure generation, and PDF report compilation.

```bash
python run_all.py --config configs/experiment_config.yaml
```

### Step 3: Run with the live Google Gemini API

Use live Gemini calls for ticket validation, zero-shot reasoning, and LLM judge scoring.

```bash
python run_all.py --use_live_llm --gemini_model gemini-1.5-flash
```

Or pass your API key on the command line:

```bash
python run_all.py --use_live_llm --gemini_api_key "YOUR_GEMINI_KEY"
```

> **Security note:** Never commit your real API key to GitHub. Keep it private.

### Step 4: Run unit tests

All 32 automated unit tests run with:

```bash
pytest tests/ -v
```

### Step 5: Run the interactive demo

Troubleshoot one incident step by step on any of the 15 topologies.

```bash
# Troubleshoot the Internet2 Abilene backbone
python interactive_cli.py --scenario abilene_backbone

# Test a healthy network with a false alarm ticket
python interactive_cli.py --scenario abilene_backbone --healthy

# Test with the live Google Gemini API
python interactive_cli.py --scenario netman_aiops --use_live_llm
```

### Step 6: Export the PDF report only

```bash
python export_pdf.py
```

The PDF is saved to `docs/Phase3_Report.pdf`.

---

## 8. Key Benchmark Findings

<div align="center">

| False Positive Rate | Cost per Session | Transfer Score | Input Tokens per Session |
|:-------------------:|:----------------:|:--------------:|:------------------------:|
| **0.0%** | **$0.0138** | **96.3%** | **1,915** |

</div>

### 1. Comparison with baselines

| Model | Detection Acc | Localization Acc | RCA F1 | False Positive Rate | Cost per Session |
|-------|:-------------:|:----------------:|:------:|:-------------------:|:----------------:|
| **Proposed 7-Phase Agent** | **0.7500** | **0.6667** | **0.6207** | **0.00%** | **$0.0138** |
| SADE-Style Baseline | 0.7500 | 0.6556 | 0.5734 | 100.0% | $0.0109 |
| Zero-Shot LLM | 0.7500 | 0.6556 | 0.5375 | 100.0% | $0.0013 |
| Scripted Rules | 0.6833 | 0.5778 | 0.5372 | 0.00% | $0.0000 |
| ReAct Agent | 0.7500 | 0.6556 | 0.0244 | 100.0% | $0.0038 |
| Generic Coding Agent | 0.7500 | 0.6556 | 0.0244 | 100.0% | $0.0088 |

```mermaid
xychart-beta
    title "RCA F1 Score (higher is better)"
    x-axis ["Proposed", "SADE-Style", "Zero-Shot", "Scripted", "ReAct", "Coding"]
    y-axis "RCA F1" 0 --> 0.7
    bar [0.6207, 0.5734, 0.5375, 0.5372, 0.0244, 0.0244]
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
| **Sub-Gap A: Over-diagnosis** | The agent had a **0.0% False Positive Rate** on healthy network controls. ReAct, Claude Code style, and SADE baselines had 100% false alarms. |
| **Sub-Gap B: Cost and tokens** | The agent used **1,915 input tokens ($0.0138 per session)**. That is more than 100 times cheaper than unconstrained agents ($1.44 in SADE). |
| **Sub-Gap C: Transferability** | The agent kept a **96.3% transfer score** on held-out topologies and P4 testbeds, with no performance collapse. |

### 3. Component ablations

| Component removed | Effect observed |
|-------------------|-----------------|
| Falsification probes | RCA F1 drops by **29.1%** |
| Abstain option | False positive rate jumps to **100%** |
| Phase gating or skills | RCA F1 falls to **near zero** |

---

## 9. Team

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

[![Project Repository](https://img.shields.io/badge/Project%20Repository-Autonomous--Network--Troubleshooting--Agent-2C5364?style=for-the-badge&logo=github)](https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent)

</div>

---

## 10. License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a43,100:0f2027&height=120&section=footer" alt="Footer wave" width="100%"/>

</div>