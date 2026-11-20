"""Builds LaTeX table bodies and scalar tokens from phase4_stats.json / ablation_stats.json -> data/tokens.json"""
import json, os
OUT = os.environ.get("P4_OUT", "paper")
S = json.load(open(f"{OUT}/data/phase4_stats.json")); A = json.load(open(f"{OUT}/data/ablation_stats.json"))
sc = json.load(open(f"{OUT}/data/scenario_table.json"))
ORDER = ["Baseline_Zero_Shot","Baseline_ReAct","Baseline_Generic_Coding","Baseline_SADE_Style","Baseline_Scripted_Rules","Proposed_7Phase_Agent"]
NAME = {"Baseline_Zero_Shot":"Zero-shot","Baseline_ReAct":"ReAct-style","Baseline_Generic_Coding":"Coding-style","Baseline_SADE_Style":"SADE-style","Baseline_Scripted_Rules":"Scripted rules","Proposed_7Phase_Agent":"\\textbf{Proposed}"}
P, C = S["point"], S["ci"]
pc = lambda x: f"{100*x:.1f}"
f3 = lambda x: f"{x:.3f}"
def ci3(m, k): lo, hi = C[m][k]; return f"[{lo:.3f}, {hi:.3f}]"
def cip(m, k): lo, hi = C[m][k]; return f"[{100*lo:.1f}, {100*hi:.1f}]"
def pv(p): return "$<10^{-9}$" if p < 1e-9 else (f"${p:.1e}$".replace("e-0","\\times10^{-").replace("e-","\\times10^{-")+"}$" if False else (f"{p:.3f}" if p >= 0.001 else f"$<0.001$"))
T = {}
# Table: detection / safety
rows = []
for m in ORDER:
    v = P[m]
    rows.append(f"{NAME[m]} & {pc(v['detection_acc'])} {cip(m,'detection_acc')} & {pc(v['fault_recall'])} & {pc(v['false_positive_rate'])} & {pc(v['balanced_acc'])} {cip(m,'balanced_acc')} \\\\")
T["tab_detect"] = "\n".join(rows)
rows = []
for m in ORDER:
    v = P[m]
    rows.append(f"{NAME[m]} & {pc(v['localization_acc'])} & {pc(v['rca_acc_faulty'])} & {f3(v['rca_f1_faulty7'])} {ci3(m,'rca_f1_faulty7')} & {f3(v['rca_macro_f1'])} & {f3(v['rca_macro_f1_h'])} {ci3(m,'rca_macro_f1_h')} \\\\")
T["tab_rca"] = "\n".join(rows)
# paired tests
rows = []
for m in ORDER[:-1]:
    q = S["paired"][m]
    rows.append(f"{NAME[m]} & {q['dF1h_point']:+.3f} [{q['dF1h_ci'][0]:+.3f}, {q['dF1h_ci'][1]:+.3f}] & {q['dF1_point']:+.3f} [{q['dF1_ci'][0]:+.3f}, {q['dF1_ci'][1]:+.3f}] & {q['healthy']['prop_only']}/{q['healthy']['base_only']} ({pv(q['healthy']['p'])}) & {q['detect']['prop_only']}/{q['detect']['base_only']} ({pv(q['detect']['p'])}) & {q['rca_faulty']['prop_only']}/{q['rca_faulty']['base_only']} ({pv(q['rca_faulty']['p'])}) \\\\")
T["tab_paired"] = "\n".join(rows)
# efficiency
rows = []
for m in ORDER:
    e = S["extra"][m]
    cc = e['mean_in_tok']*0.003/1000 + e['mean_out_tok']*0.015/1000   # common price schedule (USD per 1k tokens: 0.003 in / 0.015 out)
    rows.append(f"{NAME[m]} & {e['mean_steps']:.2f} & {e['mean_in_tok']:.0f} / {e['mean_out_tok']:.0f} & {cc*1000:.2f} \\\\")
    T['cc_'+m] = cc
T["tab_eff"] = "\n".join(rows)
# ablation
LAB = [("Full_Proposed_Agent","Full agent","--"),("Ablation_No_Evidence_Filtering","$-$ Evidence filtering","trimming to 500 tokens off"),("Ablation_No_Abstain","$-$ Abstain gate","abstention (and fast path) off"),
       ("Ablation_No_Falsification","$-$ Falsification","all hypotheses survive unchallenged"),("Ablation_No_Skills","$-$ Skill library","single generic hypothesis"),
       ("Ablation_No_Phase_Gating","$-$ Phase gating","validation, falsification, abstain, filtering, skills all off")]
rows = []
for k, lab, what in LAB:
    a = A[k]
    rows.append(f"{lab} & {what} & {pc(a['fault_recall'])} & {pc(a['fpr'])} & {pc(a['loc_acc'])} & {f3(a['f1_logged'])} & {f3(a['f1_harmonised'])} \\\\")
T["tab_abl"] = "\n".join(rows)
# scenarios
rows = []
for r in sc:
    n = r["nodes"]
    rows.append(f"\\texttt{{{r['scenario'].replace('_','\\_')}}} & {r['source'].replace('Course-','Course: ')} & {'Dev.' if r['split']=='development' else 'Held-out'} & {r['faulty']} & {r['healthy']} & {n[0]}/{n[1]}/{n[2]} \\\\")
T["tab_scen"] = "\n".join(rows)

# improvement table vs three re-implemented baselines
IMP = [("Detection accuracy (pp)","detection_acc",100,True),("Fault recall (pp)","fault_recall",100,True),("False-positive rate (pp)","false_positive_rate",100,True),
       ("Localization accuracy (pp)","localization_acc",100,True),("RCA macro-F1, as logged","rca_macro_f1",1,False),("RCA macro-F1, abstention credited","rca_macro_f1_h",1,False),("Faulty-family F1 (7 families)","rca_f1_faulty7",1,False)]
def cell(k, sc, base, isp):
    d = (P["Proposed_7Phase_Agent"][k]-P[base][k])*sc; b = P[base][k]*sc
    rel = "n/a" if b == 0 else f"{100*d/b:+.1f}\\%"
    return f"{d:+.1f} ({rel})" if isp else f"{d:+.3f} ({rel})"
rows = []
for lab, k, sc_, isp in IMP:
    rows.append(f"{lab} & " + " & ".join(cell(k, sc_, b, isp) for b in ["Baseline_SADE_Style","Baseline_Scripted_Rules","Baseline_Zero_Shot"]) + " \\\\")
T["tab_improve"] = "\n".join(rows)

# scalars
Pp = P["Proposed_7Phase_Agent"]; Ps = P["Baseline_SADE_Style"]; Pr = P["Baseline_Scripted_Rules"]; Pz = P["Baseline_Zero_Shot"]; Pre = P["Baseline_ReAct"]
pa = S["paired"]
T.update(dict(
  p_det=pc(Pp["detection_acc"]), p_det_ci=cip("Proposed_7Phase_Agent","detection_acc"), p_rec=pc(Pp["fault_recall"]), p_rec_ci=cip("Proposed_7Phase_Agent","fault_recall"),
  p_f1l=f3(Pp["rca_macro_f1"]), p_f1l_ci=ci3("Proposed_7Phase_Agent","rca_macro_f1"), p_f1h=f3(Pp["rca_macro_f1_h"]), p_f1h_ci=ci3("Proposed_7Phase_Agent","rca_macro_f1_h"),
  p_f7=f3(Pp["rca_f1_faulty7"]), p_f7_ci=ci3("Proposed_7Phase_Agent","rca_f1_faulty7"), s_f7=f3(Ps["rca_f1_faulty7"]), s_f7_ci=ci3("Baseline_SADE_Style","rca_f1_faulty7"),
  s_f1l=f3(Ps["rca_macro_f1"]), s_f1h=f3(Ps["rca_macro_f1_h"]), s_det=pc(Ps["detection_acc"]), r_f1l=f3(Pr["rca_macro_f1"]), r_f1h=f3(Pr["rca_macro_f1_h"]), r_det=pc(Pr["detection_acc"]), r_rec=pc(Pr["fault_recall"]),
  z_f1h=f3(Pz["rca_macro_f1_h"]), re_f1l=f3(Pre["rca_macro_f1"]), z_accf=pc(Pz["rca_acc_faulty"]), s_accf=pc(Ps["rca_acc_faulty"]), p_accf=pc(Pp["rca_acc_faulty"]), re_accf=pc(Pre["rca_acc_faulty"]),
  loc=pc(Pp["localization_acc"]), bal=pc(Pp["balanced_acc"]),
  d_s_h=f"{pa['Baseline_SADE_Style']['dF1h_point']:+.3f}", d_s_h_ci=f"[{pa['Baseline_SADE_Style']['dF1h_ci'][0]:+.3f}, {pa['Baseline_SADE_Style']['dF1h_ci'][1]:+.3f}]",
  d_s_l=f"{pa['Baseline_SADE_Style']['dF1_point']:+.3f}", d_s_l_ci=f"[{pa['Baseline_SADE_Style']['dF1_ci'][0]:+.3f}, {pa['Baseline_SADE_Style']['dF1_ci'][1]:+.3f}]",
  d_r_h=f"{pa['Baseline_Scripted_Rules']['dF1h_point']:+.3f}", d_r_h_ci=f"[{pa['Baseline_Scripted_Rules']['dF1h_ci'][0]:+.3f}, {pa['Baseline_Scripted_Rules']['dF1h_ci'][1]:+.3f}]",
  d_z_h=f"{pa['Baseline_Zero_Shot']['dF1h_point']:+.3f}", d_re_h=f"{pa['Baseline_ReAct']['dF1h_point']:+.3f}",
  rel_s_h=f"{100*(Pp['rca_macro_f1_h']/Ps['rca_macro_f1_h']-1):.1f}", rel_s_l=f"{100*(Pp['rca_macro_f1']/Ps['rca_macro_f1']-1):.1f}", rel_r_h=f"{100*(Pp['rca_macro_f1_h']/Pr['rca_macro_f1_h']-1):.1f}", rel_z_h=f"{100*(Pp['rca_macro_f1_h']/Pz['rca_macro_f1_h']-1):.1f}",
  p_rca_s=f"{pa['Baseline_SADE_Style']['rca_faulty']['p']:.2f}", p_rca_z=f"{pa['Baseline_Zero_Shot']['rca_faulty']['p']:.2f}", p_rca_r=f"{pa['Baseline_Scripted_Rules']['rca_faulty']['p']:.3f}",
  s_rca_s=f"{pa['Baseline_SADE_Style']['rca_faulty']['prop_only']}/{pa['Baseline_SADE_Style']['rca_faulty']['base_only']}",
  scen_p=f"{100*S['scen_acc']['Proposed_7Phase_Agent']['mean']:.1f} $\\pm$ {100*S['scen_acc']['Proposed_7Phase_Agent']['sd']:.1f}",
  scen_s=f"{100*S['scen_acc']['Baseline_SADE_Style']['mean']:.1f} $\\pm$ {100*S['scen_acc']['Baseline_SADE_Style']['sd']:.1f}",
  scen_r=f"{100*S['scen_acc']['Baseline_Scripted_Rules']['mean']:.1f} $\\pm$ {100*S['scen_acc']['Baseline_Scripted_Rules']['sd']:.1f}",
  dev_rec=pc(S["bysplit"]["Proposed_7Phase_Agent"]["development"]["fault_recall"]), ho_rec=pc(S["bysplit"]["Proposed_7Phase_Agent"]["held_out"]["fault_recall"]),
  dev_f1h=f3(S["bysplit"]["Proposed_7Phase_Agent"]["development"]["rca_macro_f1_h"]), ho_f1h=f3(S["bysplit"]["Proposed_7Phase_Agent"]["held_out"]["rca_macro_f1_h"]),
  dev_det=pc(S["bysplit"]["Proposed_7Phase_Agent"]["development"]["detection_acc"]), ho_det=pc(S["bysplit"]["Proposed_7Phase_Agent"]["held_out"]["detection_acc"]),
  s_dev_f1h=f3(S["bysplit"]["Baseline_SADE_Style"]["development"]["rca_macro_f1_h"]), s_ho_f1h=f3(S["bysplit"]["Baseline_SADE_Style"]["held_out"]["rca_macro_f1_h"]),
  sz_small=pc(S["bysize"]["Proposed_7Phase_Agent"]["small"]["fault_recall"]), sz_med=pc(S["bysize"]["Proposed_7Phase_Agent"]["medium"]["fault_recall"]), sz_large=pc(S["bysize"]["Proposed_7Phase_Agent"]["large"]["fault_recall"]),
  steps_p=f"{S['extra']['Proposed_7Phase_Agent']['mean_steps']:.2f}", steps_s=f"{S['extra']['Baseline_SADE_Style']['mean_steps']:.2f}",
  rem_rate=pc(S["extra"]["Proposed_7Phase_Agent"]["remediation_rate_detected"]),
  fam_min=pc(min(v['recall'] for k,v in S['fam'].items() if k!='healthy')), fam_max=pc(max(v['recall'] for k,v in S['fam'].items() if k!='healthy')),
  a_full=f3(A["Full_Proposed_Agent"]["f1_harmonised"]), a_full_l=f3(A["Full_Proposed_Agent"]["f1_logged"]), a_noabs=f3(A["Ablation_No_Abstain"]["f1_harmonised"]), a_noabs_l=f3(A["Ablation_No_Abstain"]["f1_logged"]),
  a_nofal=f3(A["Ablation_No_Falsification"]["f1_harmonised"]), a_nosk=f3(A["Ablation_No_Skills"]["f1_harmonised"]), a_nopg=f3(A["Ablation_No_Phase_Gating"]["f1_harmonised"]),
  a_nofal_rec=pc(A["Ablation_No_Falsification"]["fault_recall"]), a_full_rec=pc(A["Full_Proposed_Agent"]["fault_recall"]),
))
T["cc_ratio_s"]=f"{T['cc_Proposed_7Phase_Agent']/T['cc_Baseline_SADE_Style']:.2f}"; T["cc_ratio_re"]=f"{T['cc_Proposed_7Phase_Agent']/T['cc_Baseline_ReAct']:.1f}"; T["cc_p"]=f"{T['cc_Proposed_7Phase_Agent']:.4f}"; T["cc_s"]=f"{T['cc_Baseline_SADE_Style']:.4f}"
json.dump(T, open(f"{OUT}/data/tokens.json", "w"), indent=1)
print("tokens:", len(T))
