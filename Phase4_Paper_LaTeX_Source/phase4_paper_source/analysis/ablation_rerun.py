"""Re-executes the six ablation variants of Phase 3 (same code, offline mode) while keeping per-incident logs,
so that label-harmonised metrics can be computed.  Asserts that the logged ablation summary is reproduced.
Run from the Phase 3 repo root:  python3 analysis/ablation_rerun.py"""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.environ.get("P3_REPO", "."))
os.environ.setdefault("GEMINI_API_KEY", "unused")
from code.data.loader import IncidentDataset
from code.data.mock_network_env import MockNetworkEnv
from code.agent.orchestrator import TroubleshootingAgent
from sklearn.metrics import f1_score
OUT = os.environ.get("P4_OUT", "paper")
incs = IncidentDataset().generate_benchmark_dataset(total_target=60, healthy_ratio=0.30)
cfg = {"Full_Proposed_Agent": {}, "Ablation_No_Phase_Gating": dict(enable_ticket_validation=False, enable_falsification=False, enable_abstain=False, enable_evidence_filtering=False, enable_skills=False),
       "Ablation_No_Skills": dict(enable_skills=False), "Ablation_No_Falsification": dict(enable_falsification=False),
       "Ablation_No_Abstain": dict(enable_abstain=False), "Ablation_No_Evidence_Filtering": dict(enable_evidence_filtering=False)}
rows = []
for name, kw in cfg.items():
    ag = TroubleshootingAgent(llm_client=None, use_llm=False, **kw)
    for inc in incs:
        env = MockNetworkEnv(scenario=inc["scenario"], topology_size=inc["topology_size"], fault_injected=inc["ground_truth_has_fault"],
                             fault_family=inc["ground_truth_fault_family"], faulty_device=inc["ground_truth_device"])
        r = ag.troubleshoot(inc, env)
        rows.append(dict(variant=name, incident_id=inc["incident_id"], has_fault=inc["ground_truth_has_fault"], truth=str(inc["ground_truth_fault_family"]),
                         gt_dev=inc["ground_truth_device"], detected=bool(r["detected"]), root_cause=r["root_cause"], loc=r["localized_device"], steps=r["turns_used"]))
d = pd.DataFrame(rows); d.to_csv(f"{OUT}/data/ablation_raw.csv", index=False)
logged = pd.read_csv("results/ablation_results.csv").set_index("variant")
res = {}
for v, g in d.groupby("variant"):
    yt = g.truth.to_numpy(); yth = np.where(yt == "healthy", "none", yt); yp = g.root_cause.astype(str).to_numpy(); hf = g.has_fault.to_numpy(bool)
    det = g.detected.to_numpy(bool)
    res[v] = dict(n=int(len(g)), n_faulty=int(hf.sum()), detection_acc=float(np.mean(det == hf)), fault_recall=float(det[hf].mean()), fpr=float(det[~hf].mean()),
                  f1_logged=float(f1_score(yt, yp, average="macro", zero_division=0)), f1_harmonised=float(f1_score(yth, yp, average="macro", zero_division=0)),
                  acc_faulty=float(np.mean((yp == yt)[hf])), loc_acc=float(np.mean((g.gt_dev == g["loc"]).to_numpy()[hf])))
    col = "rca_f1_macro_raw" if "rca_f1_macro_raw" in logged.columns else "rca_f1_macro"
    assert abs(res[v]["f1_logged"] - logged.loc[v, col]) < 1e-3, (v, res[v]["f1_logged"], logged.loc[v, col])
    assert abs(res[v]["detection_acc"] - logged.loc[v, "detection_accuracy"]) < 1e-3
json.dump(res, open(f"{OUT}/data/ablation_stats.json", "w"), indent=1)
print(pd.DataFrame(res).T.round(3).to_string())
