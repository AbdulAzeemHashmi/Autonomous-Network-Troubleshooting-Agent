"""
Phase 4 analysis: derives every number, table and figure used in the paper from the
Phase 3 raw per-incident run log (results/raw_runs.csv) and ablation log.
No new agent runs are performed here; this script only re-analyses the logged runs.
Usage (from the Phase 3 repo root):  python3 analysis/phase4_analysis.py
"""
import json, os, sys, math
import numpy as np, pandas as pd
from scipy.stats import binom
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.environ.get("P3_REPO", ".")
OUT = os.environ.get("P4_OUT", "paper")
os.makedirs(f"{OUT}/figures", exist_ok=True); os.makedirs(f"{OUT}/data", exist_ok=True)
rng = np.random.default_rng(20261117)

raw = pd.read_csv(f"{REPO}/results/raw_runs.csv")
abl = pd.read_csv(f"{REPO}/results/ablation_results.csv")
ORDER = ["Baseline_Zero_Shot","Baseline_ReAct","Baseline_Generic_Coding","Baseline_SADE_Style","Baseline_Scripted_Rules","Proposed_7Phase_Agent"]
NAME = {"Baseline_Zero_Shot":"Zero-shot","Baseline_ReAct":"ReAct-style","Baseline_Generic_Coding":"Coding-style",
        "Baseline_SADE_Style":"SADE-style","Baseline_Scripted_Rules":"Scripted rules","Proposed_7Phase_Agent":"Proposed"}
inc_ids = sorted(raw.incident_id.unique()); N = len(inc_ids)
per = {m: raw[raw.model_name==m].set_index("incident_id").loc[inc_ids].reset_index() for m in ORDER}
truth = per[ORDER[0]]
has_fault = truth.ground_truth_has_fault.to_numpy(bool)
y_true = truth.ground_truth_fault_family.fillna("none").astype(str).to_numpy()
split = truth.split.to_numpy()
# Phase 3 logs the healthy ground-truth family as the string "healthy" while abstaining agents emit "none".
# y_true_h harmonises the two spellings (sensitivity analysis); y_true is the label set exactly as logged.
y_true_h = np.where(y_true == "healthy", "none", y_true)
FAMS7 = sorted(set(y_true) - {"none", "healthy"})
assert N == 120 and has_fault.sum() == 90

def macro_f1(yt, yp):
    labs = sorted(set(yt) | set(yp)); f = []
    for l in labs:
        tp = np.sum((yt==l)&(yp==l)); fp = np.sum((yt!=l)&(yp==l)); fn = np.sum((yt==l)&(yp!=l))
        f.append(0.0 if tp==0 else 2*tp/(2*tp+fp+fn))
    return float(np.mean(f))

def fam7_f1(yt, yp, hf):
    out = []
    for l in FAMS7:
        a, b = yt[hf], yp[hf]
        tp = np.sum((a==l)&(b==l)); fp = np.sum((a!=l)&(b==l)); fn = np.sum((a==l)&(b!=l))
        out.append(0.0 if tp==0 else 2*tp/(2*tp+fp+fn))
    return float(np.mean(out))

def metrics(m, idx=None):
    d = per[m]; idx = np.arange(N) if idx is None else idx
    det = d.detected.to_numpy(bool)[idx]; hf = has_fault[idx]
    yt = y_true[idx]; yp = d.root_cause.fillna("none").astype(str).to_numpy()[idx]
    loc = (d.ground_truth_device.to_numpy()[idx] == d.localized_device.to_numpy()[idx])
    out = dict(
        detection_acc=float(np.mean(det==hf)),
        fault_recall=float(np.mean(det[hf])) if hf.any() else np.nan,
        false_positive_rate=float(np.mean(det[~hf])) if (~hf).any() else np.nan,
        localization_acc=float(np.mean(loc[hf])) if hf.any() else np.nan,
        rca_macro_f1=macro_f1(yt, yp),
        rca_macro_f1_h=macro_f1(y_true_h[idx], yp),
        rca_f1_faulty7=fam7_f1(yt, yp, hf),
        rca_acc_all_h=float(np.mean(y_true_h[idx]==yp)),
        rca_acc_faulty=float(np.mean((yp==yt)[hf])) if hf.any() else np.nan)
    out["balanced_acc"] = 0.5*(out["fault_recall"] + (1-out["false_positive_rate"]))
    return out

# ---------- point estimates + bootstrap CIs ----------
B = 5000
boot_idx = rng.integers(0, N, size=(B, N))
point = {m: metrics(m) for m in ORDER}
boot = {m: {k: [] for k in point[m]} for m in ORDER}
for b in range(B):
    idx = boot_idx[b]
    for m in ORDER:
        r = metrics(m, idx)
        for k, v in r.items(): boot[m][k].append(v)
ci = {m: {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] for k, v in boot[m].items()} for m in ORDER}
extra = {}
for m in ORDER:
    d = per[m]
    extra[m] = dict(mean_steps=float(d.turns_used.mean()), mean_in_tok=float(d.input_tokens.mean()),
                    mean_out_tok=float(d.output_tokens.mean()), mean_cost=float(d.cost_usd.mean()),
                    remediation_rate_detected=float(d[d.detected].remediation_proposed.mean()) if d.detected.any() else 0.0)

# ---------- paired tests vs Proposed ----------
def mcnemar(a_correct, b_correct):
    b = int(np.sum(a_correct & ~b_correct)); c = int(np.sum(~a_correct & b_correct)); n = b + c
    p = 1.0 if n == 0 else float(min(1.0, 2*binom.cdf(min(b, c), n, 0.5)))
    return dict(prop_only=b, base_only=c, p=p)
P = "Proposed_7Phase_Agent"
def correct_detect(m): return (per[m].detected.to_numpy(bool) == has_fault)
def correct_rca(m): return (per[m].root_cause.fillna("none").astype(str).to_numpy() == y_true)
def correct_rca_h(m): return (per[m].root_cause.fillna("none").astype(str).to_numpy() == y_true_h)
paired = {}
for m in ORDER[:-1]:
    dF1 = [macro_f1(y_true[boot_idx[b]], per[P].root_cause.fillna("none").astype(str).to_numpy()[boot_idx[b]]) -
           macro_f1(y_true[boot_idx[b]], per[m].root_cause.fillna("none").astype(str).to_numpy()[boot_idx[b]]) for b in range(2000)]
    dF1h = [macro_f1(y_true_h[boot_idx[b]], per[P].root_cause.fillna("none").astype(str).to_numpy()[boot_idx[b]]) -
            macro_f1(y_true_h[boot_idx[b]], per[m].root_cause.fillna("none").astype(str).to_numpy()[boot_idx[b]]) for b in range(2000)]
    paired[m] = dict(
        rca_h=mcnemar(correct_rca_h(P), correct_rca_h(m)),
        dF1h_point=point[P]["rca_macro_f1_h"]-point[m]["rca_macro_f1_h"], dF1h_ci=[float(np.percentile(dF1h, 2.5)), float(np.percentile(dF1h, 97.5))],
        detect=mcnemar(correct_detect(P), correct_detect(m)),
        rca=mcnemar(correct_rca(P), correct_rca(m)),
        rca_faulty=mcnemar(correct_rca(P)[has_fault], correct_rca(m)[has_fault]),
        healthy=mcnemar(correct_detect(P)[~has_fault], correct_detect(m)[~has_fault]),
        dF1_point=point[P]["rca_macro_f1"]-point[m]["rca_macro_f1"],
        dF1_ci=[float(np.percentile(dF1, 2.5)), float(np.percentile(dF1, 97.5))])


# ---------- split / size / family / scenario breakdowns ----------
bysplit = {m: {s: metrics(m, np.where(split==s)[0]) for s in ["development","held_out"]} for m in ORDER}
size = truth.topology_size.to_numpy()
bysize = {m: {s: metrics(m, np.where((size==s)&has_fault)[0]) for s in ["small","medium","large"]} for m in ORDER}
size_n = {s: int(np.sum((size==s)&has_fault)) for s in ["small","medium","large"]}
fam = truth.ground_truth_fault_family.fillna("none").to_numpy()
pd_ = per[P]
fam_tab = {}
for f in sorted(set(fam)-{"none"}):
    ii = np.where(fam==f)[0]
    fam_tab[f] = dict(n=int(len(ii)), recall=float(np.mean(pd_.detected.to_numpy(bool)[ii])),
                      rca_correct=float(np.mean((pd_.root_cause.to_numpy()[ii]==f))))
scen = truth.scenario.to_numpy()
scen_acc = {}
for m in ORDER:
    accs = [np.mean((per[m].detected.to_numpy(bool)==has_fault)[scen==s]) for s in sorted(set(scen))]
    scen_acc[m] = dict(mean=float(np.mean(accs)), sd=float(np.std(accs, ddof=1)), n=len(accs))

# ---------- failure attribution for the proposed agent (faulty incidents) ----------
sys.path.insert(0, REPO); os.environ.setdefault("GEMINI_API_KEY", "unused")
from code.data.mock_network_env import MockNetworkEnv
from code.data.loader import IncidentDataset
ds = {i["incident_id"]: i for i in IncidentDataset().generate_benchmark_dataset(150, 0.25)}
rows = []
for _, r in pd_[pd_.ground_truth_has_fault].iterrows():
    i = ds[r.incident_id]
    env = MockNetworkEnv(scenario=i["scenario"], topology_size=i["topology_size"], fault_injected=True,
                         fault_family=i["ground_truth_fault_family"], faulty_device=i["ground_truth_device"])
    nodes = env.topo.get_nodes(); t = i["ticket_text"].lower()
    first = next((n for n in nodes if n.lower() in t), None)
    k = int(r.incident_id.split("-")[1]) - 1
    decoy = (k % 5 == 0)
    cause = "detected" if r.detected else ("misdirected_ticket" if decoy else ("name_collision" if first != r.ground_truth_device else "other"))
    rows.append(dict(incident_id=r.incident_id, size=r.topology_size, cause=cause, decoy=decoy,
                     parsed_correct=(first == r.ground_truth_device)))
fa = pd.DataFrame(rows)
fail = dict(total_faulty=int(len(fa)), detected=int((fa.cause=="detected").sum()),
            misdirected=int((fa.cause=="misdirected_ticket").sum()), collision=int((fa.cause=="name_collision").sum()),
            other=int((fa.cause=="other").sum()),
            by_size={s: fa[fa["size"]==s].cause.value_counts().to_dict() for s in ["small","medium","large"]},
            recall_when_ticket_ok=float(fa[(~fa.decoy)&fa.parsed_correct].cause.eq("detected").mean()),
            n_ticket_ok=int(((~fa.decoy)&fa.parsed_correct).sum()))
fa.to_csv(f"{OUT}/data/proposed_failure_attribution.csv", index=False)

# ---------- ablation ----------
abl = abl.set_index("variant")
ablation = abl[["total_runs","detection_accuracy","localization_accuracy","rca_f1_macro","false_positive_rate","mean_steps","mean_input_tokens"]].round(4).to_dict("index")

result = dict(N=N, n_faulty=int(has_fault.sum()), n_healthy=int((~has_fault).sum()), point=point, ci=ci, extra=extra, paired=paired,
              bysplit=bysplit, bysize=bysize, size_n=size_n, fam=fam_tab, scen_acc=scen_acc, fail=fail, ablation=ablation,
              split_counts={s: dict(total=int((split==s).sum()), faulty=int(((split==s)&has_fault).sum())) for s in ["development","held_out"]})
json.dump(result, open(f"{OUT}/data/phase4_stats.json", "w"), indent=1)
pd.DataFrame({NAME[m]: point[m] for m in ORDER}).T.round(4).to_csv(f"{OUT}/data/main_metrics_point.csv")

# =============================== FIGURES ===============================
plt.rcParams.update({"font.family":"serif","font.size":8,"axes.spines.top":False,"axes.spines.right":False,
                     "axes.linewidth":0.6,"pdf.fonttype":42,"figure.dpi":300})
C = {"fr":"#0072B2","sp":"#D55E00","loc":"#009E73","f1":"#CC79A7"}

# Fig: main diagnostic results with CIs
fig, ax = plt.subplots(figsize=(6.6, 3.0))
metr = [("fault_recall","Fault recall (90 faulty)",C["fr"]),("spec","Healthy specificity, $1-$FPR (30 healthy)",C["sp"]),
        ("localization_acc","Localization accuracy (faulty)",C["loc"]),("rca_macro_f1_h","RCA macro-F1, abstention credited (all 120)",C["f1"])]
w = 0.19; x = np.arange(len(ORDER))
for j,(k,lab,col) in enumerate(metr):
    if k=="spec":
        v = [1-point[m]["false_positive_rate"] for m in ORDER]
        lo = [1-ci[m]["false_positive_rate"][1] for m in ORDER]; hi = [1-ci[m]["false_positive_rate"][0] for m in ORDER]
    else:
        v = [point[m][k] for m in ORDER]; lo=[ci[m][k][0] for m in ORDER]; hi=[ci[m][k][1] for m in ORDER]
    ax.bar(x+(j-1.5)*w, v, w, color=col, label=lab, edgecolor="white", linewidth=0.3)
    ax.errorbar(x+(j-1.5)*w, v, yerr=[np.array(v)-np.array(lo), np.array(hi)-np.array(v)], fmt="none", ecolor="black", elinewidth=0.5, capsize=1.2)
ax.set_xticks(x); ax.set_xticklabels([NAME[m] for m in ORDER]); ax.set_ylim(0,1.12); ax.set_ylabel("Score")
ax.legend(frameon=False, fontsize=6.5, ncol=2, loc="upper left", bbox_to_anchor=(0,1.18))
fig.tight_layout(); fig.savefig(f"{OUT}/figures/fig_main_results.pdf"); plt.close(fig)

# Fig: failure attribution
fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={"width_ratios":[1,1.35]})
ax = axs[0]
parts = [("Detected", fail["detected"], "#0072B2"), ("Missed: misdirected ticket", fail["misdirected"], "#D55E00"), ("Missed: device-name collision", fail["collision"], "#E69F00")]
left = 0
for lab, v, col in parts:
    ax.barh([0], [v], left=left, color=col, edgecolor="white", label=f"{lab} ({v})"); left += v
ax.set_yticks([]); ax.set_xlim(0, 90); ax.set_xlabel("Faulty incidents (n = 90)")
ax.legend(frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, 1.5), ncol=1)
ax = axs[1]
sizes = ["small","medium","large"]; labels = [f"{s}\n(n={size_n[s]})" for s in sizes]
for i,s in enumerate(sizes):
    c = fail["by_size"][s]; n = size_n[s]; bot = 0
    for key, col in [("detected","#0072B2"),("misdirected_ticket","#D55E00"),("name_collision","#E69F00")]:
        v = c.get(key,0)/n; ax.bar(i, v, bottom=bot, color=col, edgecolor="white", width=0.55); bot += v
ax.set_xticks(range(3)); ax.set_xticklabels(labels); ax.set_ylabel("Share of faulty incidents"); ax.set_ylim(0,1)
fig.tight_layout(); fig.savefig(f"{OUT}/figures/fig_failure_attribution.pdf", bbox_inches="tight"); plt.close(fig)

# Fig: ablation (per-incident re-run of the six Phase 3 variants; see analysis/ablation_rerun.py)
astats = json.load(open(f"{OUT}/data/ablation_stats.json"))
fig, ax = plt.subplots(figsize=(6.6, 2.8))
variants = ["Full_Proposed_Agent","Ablation_No_Evidence_Filtering","Ablation_No_Abstain","Ablation_No_Falsification","Ablation_No_Skills","Ablation_No_Phase_Gating"]
vl = ["Full","$-$Evidence\nfiltering","$-$Abstain","$-$Falsification","$-$Skill\nlibrary","$-$Phase\ngating"]
x = np.arange(len(variants)); w = 0.26
for j,(k,lab,col) in enumerate([("f1_harmonised","RCA macro-F1 (abstention credited)","#CC79A7"),("fault_recall","Fault recall","#0072B2"),("fpr","False-positive rate","#D55E00")]):
    ax.bar(x+(j-1)*w, [astats[v][k] for v in variants], w, label=lab, color=col, edgecolor="white", linewidth=0.3)
ax.set_xticks(x); ax.set_xticklabels(vl); ax.set_ylim(0,1.05); ax.set_ylabel("Score"); ax.legend(frameon=False, ncol=3, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5,1.17))
fig.tight_layout(); fig.savefig(f"{OUT}/figures/fig_ablation.pdf"); plt.close(fig)

# Fig: dev vs held-out
fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.5), sharey=False)
x = np.arange(len(ORDER)); w = 0.36
for ax, (k, ttl) in zip(axs, [("rca_macro_f1_h","RCA macro-F1 (abstention credited)"),("fault_recall","Fault recall")]):
    ax.bar(x-w/2, [bysplit[m]["development"][k] for m in ORDER], w, label="Development (10 scenarios)", color="#56B4E9", edgecolor="white")
    ax.bar(x+w/2, [bysplit[m]["held_out"][k] for m in ORDER], w, label="Held-out (5 scenarios)", color="#E69F00", edgecolor="white")
    ax.set_xticks(x); ax.set_xticklabels([NAME[m].replace("-style","\n-style").replace("Scripted rules","Scripted\nrules") for m in ORDER], fontsize=6.5)
    ax.set_title(ttl, fontsize=8); ax.set_ylim(0, 1.05)
axs[0].legend(frameon=False, fontsize=6.5, loc="upper left")
fig.tight_layout(); fig.savefig(f"{OUT}/figures/fig_split_transfer.pdf"); plt.close(fig)

print(json.dumps({"point":point["Proposed_7Phase_Agent"], "fail":fail}, indent=1))
