# Baseline Methods Specification and Configurations

**Course**: Computer Networks  
**Authors**: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)  
**Deliverable**: Comparative Baselines Architecture and Setup

---

## 1. Overview

To evaluate our proposed 7-Phase Autonomous Troubleshooting Agent, we implement five distinct comparative baselines representing the full spectrum of prior art:

1. **Zero-Shot LLM** (No-Tool Baseline)
2. **ReAct Agent** (NIKA Benchmark Standard, Wang et al. 2025)
3. **Generic Coding Agent** (Claude Code Paradigm, Tseng et al. 2026)
4. **SADE-Style Agent** (Symptom-Aware Diagnostic Escalation, Tseng et al. 2026)
5. **Scripted Rule Checks** (Deterministic Non-AI Threshold Engine)

---

## 2. Detailed Baseline Configurations

| Metric / Feature | Zero-Shot LLM | ReAct Agent | Generic Coding Agent | SADE-Style Agent | Scripted Rule Checks | Proposed 7-Phase Agent |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Turn Budget** | 1 turn | 20 turns | 20 turns | 20 turns | 4 turns | 20 turns |
| **Tool Execution** | None (Static) | Free-form (MCP) | Python scripts | Layered scan | Fixed script | Layered + Falsification |
| **Evidence Filtering** | N/A | None (Raw) | None (Raw) | 500-token window | Static parse | 500-token window |
| **Hypothesis Routing** | Heuristic | Emergent | Emergent | 15-skill library | Hardcoded logic | 15-skill library |
| **Falsification Phase** | None | None | None | None | None | Active Counter-Probes |
| **Abstain Mechanism** | No | No | No | No | Implicit (rule miss) | Yes ("no fault found") |
| **Remediation Plan** | None | None | None | None | None | Validated + Human Gate |
| **Mean Cost / Run** | ~$0.001 | ~$0.015 - $0.035 | ~$0.030 - $0.055 | ~$0.012 - $0.025 | $0.000 | ~$0.010 - $0.022 |

---

## 3. Baseline Descriptions & Grounding

### Baseline 1: Zero-Shot LLM
- **Mechanism**: Receives the raw ticket text and topology overview. Outputs predicted root cause and faulty node in a single shot without running commands.
- **Purpose**: Establishes whether interactive network tool access is necessary or if LLM pre-training suffices.
- **Weakness**: Completely vulnerable to ticket misdirection and false-premise tickets.

### Baseline 2: ReAct Agent
- **Mechanism**: Implements the canonical `Thought -> Act -> Observe` iterative loop from the NIKA benchmark (Wang et al., 2025). Can invoke arbitrary tools from the environment.
- **Weakness**: Unbounded context accumulation leads to evidence dilution (RCLAgent findings); lacks an abstain option, resulting in severe over-diagnosis on healthy networks.

### Baseline 3: Generic Coding Agent
- **Mechanism**: Inspired by tools like Claude Code. Instead of calling predefined CLI endpoints, the model generates and executes small Python diagnostic scripts (e.g., using `subprocess` and socket tests).
- **Weakness**: High token consumption from code generation; prone to premature convergence on surface-level symptoms.

### Baseline 4: SADE-Style Agent
- **Mechanism**: Implements the SADE framework (Tseng et al., 2026). Enforces Cisco layer-by-layer escalation (L2 $\to$ L3 $\to$ L4 $\to$ Service) combined with a 15-fault-family skill library.
- **Distinction from Proposed**: SADE lacks explicit hypothesis falsification (Phase 4) and healthy-network abstention (Phase 5). On healthy networks, SADE over-diagnoses by elevating normal background lines into root causes.

### Baseline 5: Scripted Rule Checks
- **Mechanism**: Classical non-AI deterministic network monitoring. Executes fixed pings, interface checks, and route lookups against hardcoded thresholds.
- **Purpose**: Establishes the non-AI floor and evaluates whether generative AI provides measurable benefit over conventional scripted threshold monitors.

