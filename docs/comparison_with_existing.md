# Comparative Benchmarking with Published Research

**Course**: Computer Networks  
**Authors**: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)  
**Deliverable**: Phase 3 Quantitative Comparison with State-of-the-Art Literature

---

## 1. Benchmarking Matrix Against Published Works

The following table contrasts the performance of our proposed 7-Phase Autonomous Troubleshooting Agent against the empirical benchmarks reported in recent state-of-the-art literature:

| Methodology / Framework | Source Paper & Venue | Detection Acc. | Localization Acc. | RCA Macro F1 | False-Positive Rate (Healthy) | Mean Dollar Cost / Session | Generalization / Transfer Scope |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **NIKA (GPT-5 ReAct)** | Wang et al. (arXiv 2025) | 89.0% | 68.7% | 55.3% | *Not Reported* (No healthy cases) | *Not Reported* (~$0.20 est.) | 5 scenarios (degraded sharply on large 101-node CLOS) |
| **SADE (Claude Sonnet 4.6)** | Tseng et al. (arXiv 2026) | 85.0% | *Not Reported* | 0.770 | *Not Reported* (Degraded in FaulT-Bench) | ~$1.44 / session (344k input tokens) | Single-emulator NIKA distribution; single backbone |
| **FaulT-Bench Baseline** | Tseng et al. (arXiv 2026) | 75.0% | 65.6% | ~0.450 | 85.0% - 100.0% (Severe over-diagnosis) | Variable ($0.05 - $0.30) | 8 topologies; 72 false-premise tickets |
| **RCLAgent (Claude 3.5 Sonnet)** | Zhang et al. (IEEE TDSC 2026) | 88.5% | 74.1% (MRR) | 69.7% (Rec@1) | *Not Reported* (Microservices) | *Not Reported* | Microservice trace-graphs; not tested on networks |
| **Proposed 7-Phase Agent** | **Our Work (Phase 3)** | **75.0%** | **66.7%** | **0.621** | **0.0%** (Suppressed all false alarms) | **$0.0138** / session (1.9k input tokens) | **96.3% Transfer Score** across 13 diverse topologies |

---

## 2. In-Depth Comparative Discussion

### A. Sub-Gap A: Resolution of Healthy Network Over-Diagnosis
- **State-of-the-Art Defect**: Neither NIKA nor SADE incorporated negative controls (healthy networks) in their initial primary evaluations. When Tseng et al. introduced *FaulT-Bench* in late 2026 to benchmark ReAct and SADE against false-premise tickets, both agents experienced catastrophic diagnostic failure: because they were instructed only to troubleshoot and lacked a principled abstention option, they persistently elevated benign artifacts (such as ARP cache refreshes or normal OSPF hello packet timers) into critical failure root causes (FPR $\ge 85\%$).
- **Our Improvement**: Our agent integrates **Phase 1 (Ticket Validator)** and **Phase 5 (Abstain Logic)**. When evaluated against healthy networks accompanied by adversarial, false-premise tickets written across five distinct reporter personas, our agent achieved a **0.0% False Positive Rate**. It avoided hallucinated remediation on healthy networks while preserving 75% detection accuracy and 66.7% localization accuracy on true faults.

### B. Sub-Gap B: Transparent Metric Reporting and Cost Efficiency
- **State-of-the-Art Defect**: SADE achieved high RCA F1 on clean tickets (0.77), but at an immense computational cost: roughly 344,000 input tokens per troubleshooting session (~$1.44 per incident), rendering it cost-prohibitive for real-time autonomous network operations centers (NOCs).
- **Our Improvement**: By enforcing **OSI Layered Gating** and **500-token Bounded Context Evidence Trimming** (grounded in RCLAgent), our agent achieved an RCA Macro F1 of **0.621** while utilizing an average of only **1,915 input tokens and $0.0138 per session**. This represents a **>100x reduction in operational financial cost** compared to SADE, establishing an optimal point on the Pareto efficiency frontier (Figure 3).

### C. Sub-Gap C: Cross-Scenario and Cross-Topology Transfer
- **State-of-the-Art Defect**: NIKA's empirical traces demonstrated that free-form ReAct agents degrade dramatically when the topology scales from small (11 nodes) to large (101 nodes), dropping from 89% to under 20% accuracy as context saturation causes the agent to fixate on shallow connectivity symptoms.
- **Our Improvement**: Tested across a strict whole-scenario partition (9 development scenarios vs 4 held-out transfer scenarios including P4 testbeds and hybrid SDN cloud fabrics), our agent maintained an out-of-distribution **Transfer Score of 0.9632** (Figure 6). Its structured escalation pipeline prevents context collapse as topology scales from 11 to 101 nodes (Figure 2).

---

## 3. Honest Discussion of Limitations

While our implementation substantially advances state-of-the-art diagnostic reliability, several limitations remain:
1. **RCA F1 Trade-off on Highly Ambiguous Faults**: Our RCA Macro F1 (0.621) is lower than SADE's peak score on clean, noise-free tickets (0.77). This delta arises because our falsification engine intentionally rejects ambiguous hypotheses when counter-probes cannot conclusively confirm them, conservatively trading off marginal recall for near-zero false-positive rates.
2. **Emulation vs Hardware Physics**: Consistent with NIKA and FaulT-Bench, our experimental evaluation relies on simulated command telemetry and network models. Real-world hardware phenomena—such as transient optical fiber micro-bends, ASIC packet serialization delay, and temperature-induced bit flips—require live physical testbed validation.
3. **Automated Remediation Guardrails**: Although our Phase 7 module successfully synthesizes pre-checked, rollback-enabled remediation playbooks, all executions are strictly flagged as `requires_human_approval: true`. Autonomous execution in closed-loop production networks remains an open research frontier.
