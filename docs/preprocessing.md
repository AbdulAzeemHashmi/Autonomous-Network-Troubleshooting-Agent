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
We synthesize and load incidents reflecting the five official NIKA scenarios (`datacenter_clos`, `campus_network`, `isp_backbone`, `sdn_cloud_fabric`, `p4_testbed`), eight FaulT-Bench topologies (`enterprise_branch`, `leaf_spine_clos`, `multihomed_edge`, `transit_wan`, `sdn_hybrid`, `bgp_peering_exchange`, `datacenter_dci`, `campus_core_access`), and two course-recommended benchmarks (`abilene_backbone` Internet2 backbone and `netman_aiops` enterprise multi-tier network) across 15 total topologies:

| Scenario Identifier | Benchmark Source | Architecture / Domain | Node Count | Edge Count | Graph Diameter | Network Tier Structure |
|:---|:---|:---|:---:|:---:|:---:|:---|
| `datacenter_clos` | NIKA (Wang '25) | 2-tier Leaf-Spine Fabric | 12 | 24 | 3 | Spines, Leaves, Compute Hosts |
| `campus_network` | NIKA (Wang '25) | Multi-tier Enterprise Campus | 24 | 42 | 4 | Core, Distribution, Access, Endpoints |
| `isp_backbone` | NIKA (Wang '25) | Regional ISP Mesh Backbone | 18 | 36 | 5 | Core POPs, Edge Routers, Transit Links |
| `sdn_cloud_fabric` | NIKA (Wang '25) | OpenFlow SDN Cloud Fabric | 16 | 28 | 3 | SDN Controller, OF Switches, VMs |
| `p4_testbed` | NIKA (Wang '25) | Programmable Data Plane | 8 | 14 | 3 | P4 Ingress/Egress Pipelines |
| `enterprise_branch` | FaulT-Bench ('26) | Dual-Homed Branch Office | 10 | 16 | 3 | Branch CPE, Dual WAN Upstreams |
| `leaf_spine_clos` | FaulT-Bench ('26) | 3-tier High-Density Data Center | 32 | 64 | 4 | Super-Spines, Spines, Leaves |
| `multihomed_edge` | FaulT-Bench ('26) | Multi-Homed BGP Edge | 14 | 22 | 4 | BGP Border Gateways, Peering Routers |
| `transit_wan` | FaulT-Bench ('26) | Global Transit WAN Mesh | 22 | 48 | 5 | Core MPLS LSRs, Edge LERs |
| `sdn_hybrid` | FaulT-Bench ('26) | Hybrid Legacy and SDN Fabric | 20 | 38 | 4 | Hybrid OF Switches, OSPF Routers |
| `bgp_peering_exchange` | FaulT-Bench ('26) | Internet Exchange Point (IXP) | 16 | 32 | 3 | IXP Route Servers, Peer Routers |
| `datacenter_dci` | FaulT-Bench ('26) | Data Center Interconnect (DCI) | 28 | 54 | 4 | DCI Gateways, Optical Extenders |
| `campus_core_access` | FaulT-Bench ('26) | Ultra-Large Enterprise Campus | 101 | 182 | 6 | Multi-Building Core, Agg, Access |
| `abilene_backbone` | Course Benchmark | Internet2 National Backbone | 11 | 28 | 4 | Core PoPs across US Metro Areas |
| `netman_aiops` | Course Benchmark | NetManAIOps Enterprise Fabric | 16 | 30 | 4 | Core Gateways, Aggregation, Services |

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

