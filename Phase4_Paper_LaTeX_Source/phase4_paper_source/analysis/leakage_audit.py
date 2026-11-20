"""Validity check: do the proposed agent's outputs change if the ground-truth `is_healthy_control`
flag (read by the Phase 3 orchestrator's fast path) is hidden from it?  Run from the Phase 3 repo root."""
import copy, os, sys, pandas as pd
sys.path.insert(0, os.environ.get("P3_REPO", "."))
os.environ.setdefault("GEMINI_API_KEY", "unused")
from code.data.loader import IncidentDataset
from code.data.mock_network_env import MockNetworkEnv
from code.agent.orchestrator import TroubleshootingAgent
raw = pd.read_csv("results/raw_runs.csv"); p = raw[raw.model_name == "Proposed_7Phase_Agent"].set_index("incident_id")
agent = TroubleshootingAgent(turn_budget=20, llm_client=None, use_llm=False); diff = 0
incs = IncidentDataset().generate_benchmark_dataset(120, 0.25)
for inc in incs:
    env = MockNetworkEnv(scenario=inc["scenario"], topology_size=inc["topology_size"], fault_injected=inc["ground_truth_has_fault"],
                         fault_family=inc["ground_truth_fault_family"], faulty_device=inc["ground_truth_device"])
    blind = copy.deepcopy(inc); blind["is_healthy_control"] = False
    r = agent.troubleshoot(blind, env); row = p.loc[inc["incident_id"]]
    diff += int(bool(r["detected"]) != bool(row.detected) or r["root_cause"] != row.root_cause or r["localized_device"] != row.localized_device)
print(f"{len(incs)} incidents; outputs that differ when the label is hidden: {diff}")
