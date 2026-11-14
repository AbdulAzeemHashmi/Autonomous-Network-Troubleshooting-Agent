# Data Preprocessing, Fault Injection Audit, and Partitioning Protocol

**Course**: Computer Networks  
**Authors**: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)  
**Deliverable**: Phase 3 Experimental Preprocessing Documentation

---

## 1. Overview & Research Grounding

In Phase 2, our critical analysis of the literature identified two key data defects in modern autonomous troubleshooting evaluations:
1. **Unverified Injections**: Tseng et al. (*SADE*, 2026) revealed that automated fault injectors in emulation testbeds (such as NIKA / Kathara) occasionally fail to instantiate the intended anomaly. Evaluating an agent on an uninstalled fault distorts detection and localization accuracy.
2. **Over-Diagnosis on Healthy Networks**: Tseng et al. (*FaulT-Bench*, 2026) demonstrated that standard LLM agents (ReAct, SADE, Claude Code) suffer catastrophic drops when deployed on healthy networks accompanied by false-premise user tickets, persistently elevating benign observations into catastrophic root causes.
3. **Data Leakage in Splits**: Random row-based splitting allows identical network topologies and failure manifestations to leak between development and evaluation partitions.

To address **Sub-Gap A** and **Sub-Gap C**, our preprocessing pipeline enforces a rigorous three-tier data preparation protocol.

---

## 2. Preprocessing Pipeline Steps

### Step 1: Benchmark Dataset Synthesis
We synthesize and load incidents reflecting the five official NIKA scenarios (`datacenter_clos`, `campus_network`, `isp_backbone`, `sdn_cloud_fabric`, `p4_testbed`), eight FaulT-Bench topologies (`enterprise_branch`, `leaf_spine_clos`, `multihomed_edge`, `transit_wan`, `sdn_hybrid`, `bgp_peering_exchange`, `datacenter_dci`, `campus_core_access`), and two course-recommended benchmarks (`abilene_backbone` Internet2 backbone and `netman_aiops` enterprise multi-tier network) across 15 total topologies.
- **Scale**: Multi-tier topologies with small (~11 nodes), medium (~27 nodes), and large (~101 nodes) complexity.
- **Healthy Controls**: 25% of all evaluation scenarios are pristine, non-faulty networks accompanied by false-premise tickets across five reporter personas (*Panicked User*, *Overconfident Junior Admin*, *Misdirected Developer*, *Monitoring Bot Alert*, and *Cautious Operator*).

### Step 2: Fault Injection Audit
Before any incident enters the benchmarking suite, an automated verification probe executes against the environment:
- **Link Failure**: Verifies interface operational status (`DOWN` / `NO-CARRIER`).
- **Congestion**: Verifies active queue drops and buffer utilization alarms.
- **Routing Misconfiguration**: Verifies missing FIB entries or blackhole null routes.
- **ACL / Firewall**: Verifies dropped packet counters.
- **Service Failure**: Verifies dead socket states and refused connections.
- **Hardware Transceiver**: Verifies elevated CRC and frame errors.
- **Healthy Controls**: Verifies 0% loss and nominal sub-millisecond RTT.

The outcome of each audit is logged to `results/fault_audit.csv`. Incidents failing audit verification are dropped immediately.

### Step 3: Whole-Scenario Partitioning
To rigorously evaluate out-of-distribution transfer (**Sub-Gap C**), we partition data strictly by *whole scenario* rather than random sampling:
- **Development Partition (69.2%)**: 9 network scenarios used for prompt refinement and heuristic tuning.
- **Held-Out Test Partition (30.8%)**: 4 scenarios (`sdn_cloud_fabric`, `p4_testbed`, `bgp_peering_exchange`, `datacenter_dci`) strictly reserved for final zero-shot transfer evaluation.

### Step 4: Bounded Context Evidence Trimming
Following Zhang et al. (*RCLAgent*, IEEE TDSC 2026), evidence dilution is the primary root cause of LLM diagnostic failure (accounting for 43 of 100 failed traces). Raw network CLI commands frequently output hundreds of lines of boilerplate copyright headers and whitespace.
Our trimmer:
1. Strips repetitive vendor banners and empty line sequences.
2. Normalizes newline formats across operating systems.
3. Enforces an upper bound of 500 tokens per tool execution output window.

