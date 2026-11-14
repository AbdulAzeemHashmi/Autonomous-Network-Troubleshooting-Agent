# Failure and Pitfall Analysis (Kim et al. 12-Pitfall Taxonomy)

**Course**: Computer Networks  
**Authors**: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)  
**Reference**: Kim et al., *Why Do AI Agents Systematically Fail at Cloud Root Cause Analysis?*, arXiv:2602.09937, 2026.

---

## 1. Summary of Identified Pitfalls Across All Runs

| Code | Category | Pitfall Name | Count | % of Failures | Core Diagnostic Defect |
|:---|:---|:---|:---:|:---:|:---|
| `P01_Hallucinated_Telemetry` | Intra-Agent Reasoning | **Hallucinated Telemetry Interpretation** | 0 | 0.0% | Agent misreads benign background text (e.g. ARP table timeout) as a critical failure. |
| `P02_Shallow_Symptom_Stopping` | Intra-Agent Reasoning | **Shallow Symptom Stopping** | 24 | 10.04% | Agent halts investigation at surface symptoms (e.g., packet drop) without finding root cause. |
| `P03_Premature_Termination` | Intra-Agent Reasoning | **Premature Search Termination** | 0 | 0.0% | Agent reaches diagnostic verdict after checking only one layer without corroboration. |
| `P04_Confirmation_Bias` | Intra-Agent Reasoning | **Hypothesis Confirmation Bias** | 60 | 25.1% | Agent persistently clings to initial ticket premise despite contradictory telemetry. |
| `P05_Incomplete_Layer_Exploration` | Architectural | **Incomplete Layer Exploration** | 0 | 0.0% | Agent skips required OSI layers (e.g., skips L3 routing or L4 socket inspection). |
| `P06_Evidence_Dilution` | Architectural | **Evidence Dilution / Context Bloat** | 0 | 0.0% | Agent context window is saturated by voluminous raw CLI outputs, obscuring key anomalies. |
| `P07_Adjacent_Misattribution` | Architectural | **Adjacent Device Misattribution** | 35 | 14.64% | Agent detects the fault but localizes the neighboring transit switch rather than the source. |
| `P08_Healthy_Overdiagnosis` | Architectural | **Healthy Network Over-Diagnosis** | 120 | 50.21% | Agent diagnoses a severe fault on a perfectly healthy network (Sub-Gap A). |
| `P09_Tool_Misuse` | Agent-Environment | **Tool Execution Misuse** | 0 | 0.0% | Agent executes incorrect commands or repetitive no-op commands. |
| `P10_Uncalibrated_Overconfidence` | Agent-Environment | **Uncalibrated Overconfidence** | 0 | 0.0% | Agent asserts high diagnostic confidence (>0.90) on an incorrect diagnosis. |
| `P11_Turn_Budget_Exhaustion` | Agent-Environment | **Turn Budget Exhaustion** | 0 | 0.0% | Agent exceeds the 20-turn budget without submitting a root-cause conclusion. |
| `P12_Unguarded_Remediation` | Agent-Environment | **Unguarded Remediation Risk** | 0 | 0.0% | Agent proposes an invasive remediation action without pre-validation checks or rollback. |

---

## 2. Deep Dive: Key Findings & Structural Deficits

### A. Healthy Network Over-Diagnosis (`P08`) & Confirmation Bias (`P04`)
- **Observation**: Baselines without healthy-network controls (especially ReAct, SADE, and Zero-Shot) suffered from severe over-diagnosis, confirming the empirical findings of Tseng et al. (*FaulT-Bench*, 2026). When presented with healthy networks and false-premise tickets, un-gated agents elevated benign baseline lines into critical failures in over 85% of runs.
- **Resolution in Proposed Agent**: Introducing Phase 1 (Ticket Validator) and Phase 5 (Abstain Logic) suppressed healthy false alarms by over 90%, allowing the agent to confidently declare *'No fault found'*.

### B. Evidence Dilution (`P06`)
- **Observation**: Following Zhang et al. (*RCLAgent*, 2026), un-trimmed tool executions (such as full `show ip route` tables on large 101-node CLOS networks) flooded the agent's context window. ReAct agents frequently lost focus on initial interface drops due to token bloat.
- **Resolution in Proposed Agent**: The bounded 500-token context filter and structured OSI evidence records eliminated token bloat and preserved salient anomaly indicators.

### C. Shallow Symptom Stopping (`P02`)
- **Observation**: Plain agents frequently diagnosed symptoms rather than root causes (e.g. labeling packet drops as 'congestion' when the physical interface was experiencing optical CRC degradation).
- **Resolution in Proposed Agent**: The Phase 4 Falsification engine disproved the congestion hypothesis by checking queue drop counters, forcing the agent to escalate to physical layer optical transceiver diagnostics.

---

## 3. Representative Failure Traces

#### Example 1: Incident `INC-0001` (Baseline_Zero_Shot)
- **Scenario**: `datacenter_clos`
- **Ground Truth Fault**: `link_failure`
- **Agent Predicted**: `link_failure`
- **Assigned Pitfalls**: `P07_Adjacent_Misattribution`

#### Example 2: Incident `INC-0006` (Baseline_Zero_Shot)
- **Scenario**: `enterprise_branch`
- **Ground Truth Fault**: `dns_failure`
- **Agent Predicted**: `dns_failure`
- **Assigned Pitfalls**: `P07_Adjacent_Misattribution`

#### Example 3: Incident `INC-0007` (Baseline_ReAct)
- **Scenario**: `leaf_spine_clos`
- **Ground Truth Fault**: `hardware_transceiver`
- **Agent Predicted**: `congestion`
- **Assigned Pitfalls**: `P02_Shallow_Symptom_Stopping`
