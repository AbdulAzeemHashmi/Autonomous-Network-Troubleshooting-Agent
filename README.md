<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=220&section=header&text=Autonomous%20Network%20Troubleshooting%20Agent&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Find%20the%20real%20fault.%20Ignore%20the%20false%20alarm.&descAlignY=58&descSize=18" alt="Header banner" width="100%"/>

<a href="https://github.com/AbdulAzeemHashmi/Autonomous-Network-Troubleshooting-Agent">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=800&color=2C9CDB&center=true&vCenter=true&width=720&lines=7-Phase+AI+Agent+for+Network+Faults;Powered+by+Google+Gemini+API;0.0%25+False+Positive+Rate+on+Healthy+Networks;Only+%240.0138+per+Troubleshooting+Session;Tested+on+15+Topologies+and+720+Runs" alt="Typing animation"/>
</a>

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-3.7-orange?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Tests-25%20passing-success?style=for-the-badge&logo=pytest&logoColor=white)
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

Modern computer networks are big, diverse, and fragile. When something breaks, finding the root cause quickly saves thousands of dollars per minute.

Large Language Model (LLM) agents can run commands like `ping`, `traceroute`, `show ip route`, and `ss` to debug outages. However, recent academic studies (NIKA from Wang et al. 2025, and Fault-Bench from Tseng et al. 2026) revealed major flaws in standard agents:

- **Over-diagnosis:** Standard agents almost always diagnose a fault, even on healthy networks (up to 100% false alarms).
- **High cost:** Unconstrained agents cost about $1.44 per incident in tokens.
- **Context dilution:** Large topologies flood the context window, causing diagnosis failures.

This project implements a **7-Phase Autonomous Network Troubleshooting Agent** that:

- Validates tickets before jumping into deep investigation.
- Scans layer by layer from Layer 2 up to the Service layer.
- Actively runs counter probes to disprove wrong guesses.
- Abstains from diagnosing when the network is healthy.
- Connects directly to Google Gemini models (Gemini 1.5 Flash, Gemini 2.0 Flash) with generous free tier quotas.
- Evaluates against 5 baselines across 13 network topologies with 720 benchmark runs and 60 ablations.
- Automatically compiles a publication quality PDF research report.

---

## 2. How the Agent Works

The agent moves through seven sequential phases:

```text
[Incident Ticket]
       |
       v
Phase 1: Ticket Validator       (Checks if reported symptom can be reproduced)
       |
       +--> If invalid on healthy network -> FAST ABSTAIN (Cost: $0.00)
       |
       v
Phase 2: Layered Evidence Scan  (Checks L2 -> L3 -> L4 -> Service layer)
       |
       v
Phase 3: Hypothesis Router      (Maps symptoms to 7 known fault families)
       |
       v
Phase 4: Falsification Probes   (Runs counter checks to disprove candidate faults)
       |
       v
Phase 5: Abstain Decision       (If no fault survives tests, output "no fault found")
       |
       v
Phase 6: Root Cause Synthesis   (Ranks surviving hypotheses with confidence)
       |
       v
Phase 7: Safe Remediation       (Plans pre-checks, fix command, and rollback)
       |
       v
[Final Diagnosis and Human-Approval Gate]
```

### The Seven Fault Families

The agent identifies seven canonical network fault families:

1. `link_failure`: Interface down, line protocol down, carrier lost.
2. `congestion`: High link utilization, buffer queue drops, elevated RTT.
3. `routing_misconfiguration`: Missing prefix, BGP route flapping, routing loop.
4. `service_failure`: Daemon crashed, port closed, connection refused.
5. `acl_firewall_block`: Packets dropped by ACL or firewall filter rule.
6. `hardware_transceiver`: High CRC error rate, low optical Rx power.
7. `dns_failure`: Name resolution failure, DNS query timeout.

---

## 3. Project Phases Recap

### Phase 1: Literature Review
- Evaluated 3 recent papers (Huang et al. 2026, Mwangi et al. 2026, Rawas and Samala 2026).
- Found 3 research gaps: no standard benchmarks, missing false-positive metrics, and weak transfer testing.

### Phase 2: Methodology Design
- Expanded review to 9 papers (including BiAn, Confucius, RCLAgent, NIKA, SADE, Fault-Bench, Kim et al.).
- Formalized the 7-phase agent architecture with ticket validation and falsification.
- Designed 9 metric groups, scenario splits, and healthy network controls.

### Phase 3: Implementation and Experimental Evaluation (This Phase)
- Implemented full 7-phase agent and 5 baselines in Python.
- Integrated Google Gemini LLM API client with offline fallback.
- Ran 720 benchmark evaluations across 13 topologies.
- Ran 60 ablation studies across 5 component removals.
- Generated 8 publication grade figures at 300 DPI.
- Built an automated PDF compiler for the academic report.

---

## 4. Technology Stack

<div align="center">

<img src="https://skillicons.dev/icons?i=python,github,git,vscode,linux&theme=dark" alt="Core tools"/>

</div>

| Area | Tool | Version / Details |
|------|------|-------------------|
| Language | Python | 3.10+ (tested on 3.12) |
| LLM Backends | Google Gemini API | gemini-1.5-flash, gemini-2.0-flash, gemini-1.5-pro |
| Network modeling | NetworkX | 3.7 graph library |
| Data analysis | Pandas, NumPy, SciPy, Scikit-Learn | Statistical tests, CIs, F1 scores |
| Plotting | Matplotlib | 8 publication figures at 300 DPI |
| PDF Export | ReportLab | Formatted academic report compiler |
| Testing | Pytest | 25 automated unit tests |

---

## 5. Dataset and Topologies

The evaluation uses 15 network topologies across 3 sizes:

| Scenario Name | Source | Topology Type | Node Count |
|---|---|---|---|
| datacenter_clos | NIKA | 2-tier Leaf-Spine CLOS | 12 |
| campus_network | NIKA | Core, Distribution, Access | 24 |
| isp_backbone | NIKA | Multi-ring ISP mesh | 18 |
| sdn_cloud_fabric | NIKA | OpenFlow controller + switches | 16 |
| p4_testbed | NIKA | Programmable data plane | 8 |
| enterprise_branch | Fault-Bench | Dual-homed branch router | 10 |
| leaf_spine_clos | Fault-Bench | 3-tier CLOS data center | 32 |
| multihomed_edge | Fault-Bench | Edge multi-homing | 14 |
| transit_wan | Fault-Bench | Transit WAN backbone | 22 |
| sdn_hybrid | Fault-Bench | Hybrid legacy and SDN | 20 |
| bgp_peering_exchange| Fault-Bench | Internet Exchange Point (IXP) | 16 |
| datacenter_dci | Fault-Bench | Data Center Interconnect | 28 |
| campus_core_access | Fault-Bench | Large campus network | 101 |
| abilene_backbone | Course Benchmark | Internet2 Abilene 11-node backbone | 11 |
| netman_aiops | Course Benchmark | Enterprise multi-tier (NetManAIOps) | 16 |

---

## 6. Folder Structure

```text
Autonomous-Network-Troubleshooting-Agent/
|-- Phase1_Literature_Review_Report.pdf   # Phase 1 submission report
|-- Phase_2_Deliverables.pdf              # Phase 2 methodology report
|-- LICENSE                               # MIT License
|-- README.md                             # Project documentation and guide
|-- requirements.txt                      # Python dependencies
|-- pytest.ini                            # Pytest configuration
|-- conftest.py                           # Root path configuration
|-- export_pdf.py                         # ReportLab PDF compiler
|-- run_all.py                            # Single-command end-to-end execution
|
|-- configs/                              # System configurations
|   |-- experiment_config.yaml            # Scenarios, topology sizes, token limits
|   |-- models.yaml                       # LLM backbone definitions and pricing
|   \-- splits.json                       # Whole-scenario train/test split IDs
|
|-- code/                                 # Implementation source code
|   |-- agent/                            # Proposed 7-phase agent
|   |   |-- llm_client.py                 # Google Gemini API wrapper
|   |   |-- ticket_validator.py           # Phase 1: Ticket validation
|   |   |-- evidence_scanner.py           # Phase 2: Layered scan
|   |   |-- hypothesis_router.py          # Phase 3: Fault family routing
|   |   |-- falsification.py              # Phase 4: Counter probes
|   |   |-- abstain.py                    # Phase 5: Abstain decision
|   |   |-- root_cause.py                 # Phase 6: Ranked root causes
|   |   |-- remediation.py                # Phase 7: Validated fix playbooks
|   |   \-- orchestrator.py               # Main agent execution loop
|   |-- baselines/                        # 5 comparative baselines
|   |   |-- zero_shot.py                  # Baseline 1: Zero-shot LLM
|   |   |-- react_agent.py                # Baseline 2: Standard ReAct
|   |   |-- coding_agent.py               # Baseline 3: Generic coding agent
|   |   |-- sade_style.py                 # Baseline 4: SADE style agent
|   |   \-- scripted_rules.py             # Baseline 5: Fixed script rules
|   |-- data/                             # Data loaders and network simulation
|   |   |-- fault_family_index.py         # Symptom to fault family dictionary
|   |   |-- topology_graph.py             # NetworkX topology generator
|   |   |-- mock_network_env.py           # CLI telemetry simulator
|   |   |-- healthy_controls.py           # False premise ticket generator
|   |   |-- loader.py                     # Incident dataset manager
|   |   \-- preprocessing.py              # Fault audit and token trimming
|   |-- experiments/                      # Experiment runner and evaluation
|   |   |-- runner.py                     # Benchmark runner and LLM judge
|   |   |-- metrics.py                    # 9 canonical metric groups
|   |   |-- statistical_tests.py          # Bootstrap CI and Wilcoxon tests
|   |   |-- ablation.py                   # 5-component ablation studies
|   |   \-- error_analysis.py             # Kim et al. 12-pitfall taxonomy
|   \-- visualization/                    # Publication figure generator
|       \-- plots.py                      # Matplotlib visualization code
|
|-- docs/                                 # Documentation and final report
|   |-- Phase3_Report.md                  # Comprehensive academic report
|   |-- Phase3_Report.pdf                 # Formatted academic report PDF
|   |-- baselines.md                      # Baseline descriptions
|   |-- comparison_with_existing.md       # Comparison with published papers
|   |-- error_analysis.md                 # Failure taxonomy report
|   \-- preprocessing.md                  # Audit and split documentation
|
|-- figures/                              # Generated 300 DPI figures
|   |-- fig1_main_performance_comparison.png
|   |-- fig2_accuracy_vs_topology_size.png
|   |-- fig3_cost_vs_rca_f1_pareto.png
|   |-- fig4_root_cause_confusion_matrix.png
|   |-- fig5_ablation_component_drop.png
|   |-- fig6_transfer_generalization.png
|   |-- fig7_token_usage_breakdown.png
|   \-- fig8_no_submission_rates.png
|
|-- prompts/                              # Phase-specific prompt templates
|   |-- judge.txt                         # FaulT-Bench LLM judge prompt
|   |-- phase1_ticket_validator.txt
|   |-- phase2_evidence_scan.txt
|   |-- phase3_hypothesis_router.txt
|   |-- phase4_falsification.txt
|   |-- phase6_root_cause.txt
|   \-- phase7_remediation.txt
|
|-- results/                              # Output CSV files
|   |-- raw_runs.csv                      # All 720 individual run records
|   |-- metrics_summary.csv               # Aggregate metrics with CIs
|   |-- statistical_tests.csv             # Wilcoxon test results
|   |-- ablation_results.csv              # Component ablation metrics
|   |-- failure_taxonomy.csv              # Error classification counts
|   \-- fault_audit.csv                   # Preprocessing audit logs
|
\-- tests/                                # Automated test suite (25 tests)
    |-- test_agent_phases.py              # Phase 1 through 7 unit tests
    |-- test_baselines.py                 # All 5 baselines tests
    |-- test_data_loader.py               # Loader, graph, and env tests
    |-- test_llm_client.py                # Gemini client and judge tests
    |-- test_metrics.py                   # Metric and runner tests
    \-- test_reproducibility.py           # End-to-end pipeline test
```

---

## 7. Quick Start

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the full pipeline (one command)

This executes 720 benchmark evaluations, 60 ablations, statistical tests, error classification, figure generation, and PDF report compilation:

```bash
python run_all.py --config configs/experiment_config.yaml
```

### Step 3: Run with live Google Gemini API

To evaluate using live Google Gemini API calls for ticket validation, zero shot reasoning, and LLM judge scoring:

```bash
python run_all.py --use_live_llm --gemini_model gemini-1.5-flash
```

Or pass your API key directly on the command line:

```bash
python run_all.py --use_live_llm --gemini_api_key "YOUR_GEMINI_KEY"
```

### Step 4: Run unit tests

All 25 automated unit tests run with:

```bash
pytest tests/ -v
```

### Step 5: Export the PDF report only

```bash
python export_pdf.py
```

The output PDF is saved to `docs/Phase3_Report.pdf`.

---

## 8. Key Benchmark Findings

### 1. Comparison with Baselines

| Model | Detection Acc | Localization Acc | RCA F1 | False Positive Rate | Cost per Session |
|---|---|---|---|---|---|
| **Proposed 7-Phase Agent** | **0.7500** | **0.6667** | **0.6207** | **0.00%** | **$0.0138** |
| SADE-Style Baseline | 0.7500 | 0.6556 | 0.5734 | 100.0% | $0.0109 |
| Zero-Shot LLM | 0.7500 | 0.6556 | 0.5375 | 100.0% | $0.0013 |
| Scripted Rules | 0.6833 | 0.5778 | 0.5372 | 0.00% | $0.0000 |
| ReAct Agent | 0.7500 | 0.6556 | 0.0244 | 100.0% | $0.0038 |
| Generic Coding Agent | 0.7500 | 0.6556 | 0.0244 | 100.0% | $0.0088 |

### 2. Research Gaps Addressed

- **Sub-Gap A (Over-diagnosis):** The proposed agent achieved a **0.0% False Positive Rate** on healthy network controls, compared to 100% false alarms in ReAct, Claude Code, and SADE baselines.
- **Sub-Gap B (Cost and Tokens):** The agent averaged **1,915 input tokens ($0.0138 per session)**, achieving more than 100 times lower cost than unconstrained agents ($1.44 in SADE).
- **Sub-Gap C (Transferability):** The agent maintained a **96.3% transfer score** on held-out topologies and P4 testbeds without performance collapse.

### 3. Component Ablations

| Component Removed | Effect Observed |
|---|---|
| Falsification probes | RCA F1 drops by **29.1%** |
| Abstain option | False positive rate spikes to **100%** |
| Phase gating or skills | RCA F1 falls to **near zero** |

---

## 9. Team

<div align="center">

<table>
  <tr>
    <td align="center">
      <b>Abdul Azeem</b><br/>
      Roll Number: 24I-2013<br/>
      FAST-NUCES
    </td>
    <td align="center">
      <b>Taha Amjad</b><br/>
      Roll Number: 24K-0007<br/>
      FAST-NUCES
    </td>
  </tr>
</table>

</div>

---

## 10. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
