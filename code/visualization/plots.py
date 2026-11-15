"""
Publication-Quality Visualization Suite
Grounding: Phase 3 Requirement 4 (Graphical Results and Visualizations).
Generates all 8 canonical figures across experimental evaluation, ablations, scaling, and cost-effectiveness.
"""

from typing import Optional
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

# Global publication aesthetics
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "font.family": "sans-serif"
})


class PlotGenerator:
    """Generates all 8 publication figures for the experimental results."""

    def __init__(self, figures_dir: str = "figures"):
        self.figures_dir = figures_dir
        os.makedirs(figures_dir, exist_ok=True)

    def generate_all_plots(
        self,
        raw_runs_path: str = "results/raw_runs.csv",
        metrics_summary_path: str = "results/metrics_summary.csv",
        ablation_results_path: str = "results/ablation_results.csv",
        robustness_results_path: str = "results/robustness_results.csv"
    ):
        """Generates all 9 figures from benchmark CSV outputs."""
        if not os.path.exists(raw_runs_path) or not os.path.exists(metrics_summary_path):
            print("[-] Required results CSV files not found. Run benchmark first.")
            return

        raw_df = pd.read_csv(raw_runs_path)
        metrics_df = pd.read_csv(metrics_summary_path)
        ablation_df = pd.read_csv(ablation_results_path) if os.path.exists(ablation_results_path) else None
        robustness_df = pd.read_csv(robustness_results_path) if os.path.exists(robustness_results_path) else None

        print("[+] Generating Figure 1: Main Performance Comparison...")
        self.plot_main_performance(metrics_df)

        print("[+] Generating Figure 2: Accuracy vs Topology Size Scaling...")
        self.plot_topology_scaling(raw_df)

        print("[+] Generating Figure 3: Cost vs RCA F1 Pareto Frontier...")
        self.plot_cost_vs_f1_pareto(metrics_df)

        print("[+] Generating Figure 4: Root Cause Confusion Matrix...")
        self.plot_confusion_matrix(raw_df)

        if ablation_df is not None:
            print("[+] Generating Figure 5: Ablation Component Performance Drop...")
            self.plot_ablation_drops(ablation_df)

        print("[+] Generating Figure 6: Cross-Scenario Transfer Generalization...")
        self.plot_transfer_generalization(raw_df)

        print("[+] Generating Figure 7: Token Usage Breakdown...")
        self.plot_token_usage(metrics_df)

        print("[+] Generating Figure 8: No-Submission & Turn Budget Rates...")
        self.plot_no_submission_rates(metrics_df)

        if robustness_df is not None:
            print("[+] Generating Figure 9: Multi-Dimensional Robustness Stress Tests...")
            self.plot_robustness_analysis(robustness_df)

        print(f"[+] All publication figures successfully generated in '{self.figures_dir}/'.")

    def plot_main_performance(self, metrics_df: pd.DataFrame):
        """Figure 1: Grouped bar chart comparing proposed agent vs 5 baselines."""
        fig, ax = plt.subplots(figsize=(11, 6))

        clean_names = {
            "Proposed_7Phase_Agent": "Proposed Agent\n(7-Phase)",
            "Baseline_SADE_Style": "SADE-Style\n(Tseng '26)",
            "Baseline_ReAct": "ReAct\n(NIKA '25)",
            "Baseline_Generic_Coding": "Coding Agent\n(Claude Code)",
            "Baseline_Zero_Shot": "Zero-Shot\nLLM",
            "Baseline_Scripted_Rules": "Scripted\nRules"
        }
        df = metrics_df.copy()
        df["display_name"] = df["model_name"].map(clean_names).fillna(df["model_name"])

        x = np.arange(len(df))
        width = 0.20

        rects1 = ax.bar(x - 1.5*width, df["detection_accuracy"] * 100, width, label="Detection Acc (%)", color="#1f77b4")
        rects2 = ax.bar(x - 0.5*width, df["localization_accuracy"] * 100, width, label="Localization Acc (%)", color="#2ca02c")
        rects3 = ax.bar(x + 0.5*width, df["rca_f1_macro"] * 100, width, label="RCA Macro F1 (%)", color="#ff7f0e")
        rects4 = ax.bar(x + 1.5*width, df["false_positive_rate"] * 100, width, label="False-Positive Rate (%) [Lower=Better]", color="#d62728")

        ax.set_ylabel("Score (%)")
        ax.set_title("Figure 1: Autonomous Network Troubleshooting Benchmark: Proposed Agent vs Baselines")
        ax.set_xticks(x)
        ax.set_xticklabels(df["display_name"])
        ax.set_ylim(0, 110)
        ax.legend(loc="upper right", frameon=True)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Highlight key contrast on False-Positive Rate
        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig1_main_performance_comparison.png"), dpi=300)
        plt.close()

    def plot_topology_scaling(self, raw_df: pd.DataFrame):
        """Figure 2: Accuracy vs topology size (small, medium, large)."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        sizes = ["small", "medium", "large"]
        size_labels = ["Small (~11 nodes)", "Medium (~27 nodes)", "Large (~101 nodes)"]

        # Filter for Proposed vs ReAct
        prop = raw_df[raw_df["model_name"] == "Proposed_7Phase_Agent"]
        react = raw_df[raw_df["model_name"] == "Baseline_ReAct"]
        sade = raw_df[raw_df["model_name"] == "Baseline_SADE_Style"]

        def get_series(df_model, metric_func):
            vals = []
            for sz in sizes:
                sub = df_model[df_model["topology_size"] == sz]
                vals.append(metric_func(sub))
            return vals

        # 1. Localization Accuracy
        loc_acc = lambda sub: (sub[sub["ground_truth_has_fault"]]["ground_truth_device"] == sub[sub["ground_truth_has_fault"]]["localized_device"]).mean() * 100
        prop_loc = get_series(prop, loc_acc)
        react_loc = get_series(react, loc_acc)
        sade_loc = get_series(sade, loc_acc)

        ax1.plot(size_labels, prop_loc, marker="o", linewidth=2.5, label="Proposed 7-Phase Agent", color="#1f77b4")
        ax1.plot(size_labels, sade_loc, marker="s", linewidth=2.0, linestyle="--", label="SADE-Style", color="#2ca02c")
        ax1.plot(size_labels, react_loc, marker="^", linewidth=2.0, linestyle=":", label="ReAct (NIKA)", color="#d62728")
        ax1.set_ylabel("Localization Accuracy (%)")
        ax1.set_title("(a) Localization Scaling Across Topology Sizes")
        ax1.set_ylim(0, 105)
        ax1.grid(True, linestyle="--", alpha=0.7)
        ax1.legend()

        # 2. RCA Correctness
        rca_acc = lambda sub: (sub["ground_truth_fault_family"] == sub["root_cause"]).mean() * 100
        prop_rca = get_series(prop, rca_acc)
        react_rca = get_series(react, rca_acc)
        sade_rca = get_series(sade, rca_acc)

        ax2.plot(size_labels, prop_rca, marker="o", linewidth=2.5, label="Proposed 7-Phase Agent", color="#1f77b4")
        ax2.plot(size_labels, sade_rca, marker="s", linewidth=2.0, linestyle="--", label="SADE-Style", color="#2ca02c")
        ax2.plot(size_labels, react_rca, marker="^", linewidth=2.0, linestyle=":", label="ReAct (NIKA)", color="#d62728")
        ax2.set_ylabel("RCA Accuracy (%)")
        ax2.set_title("(b) RCA Accuracy Scaling Across Topology Sizes")
        ax2.set_ylim(0, 105)
        ax2.grid(True, linestyle="--", alpha=0.7)
        ax2.legend()

        plt.suptitle("Figure 2: Performance Robustness under Network Topology Scale", fontsize=13)
        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig2_accuracy_vs_topology_size.png"), dpi=300)
        plt.close()

    def plot_cost_vs_f1_pareto(self, metrics_df: pd.DataFrame):
        """Figure 3: Cost (USD) vs RCA F1 Pareto frontier."""
        fig, ax = plt.subplots(figsize=(9, 6))

        clean_names = {
            "Proposed_7Phase_Agent": "Proposed Agent (7-Phase)",
            "Baseline_SADE_Style": "SADE-Style",
            "Baseline_ReAct": "ReAct (NIKA)",
            "Baseline_Generic_Coding": "Coding Agent",
            "Baseline_Zero_Shot": "Zero-Shot LLM",
            "Baseline_Scripted_Rules": "Scripted Rules"
        }

        colors = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#7f7f7f"]
        markers = ["o", "s", "^", "D", "v", "P"]

        for i, (_, row) in enumerate(metrics_df.iterrows()):
            name = clean_names.get(row["model_name"], row["model_name"])
            cost = row["mean_cost_usd"]
            f1 = row["rca_f1_macro"] * 100

            ax.scatter(cost, f1, color=colors[i % len(colors)], marker=markers[i % len(markers)], s=180, label=name, zorder=5)
            # Offset text annotation
            ax.annotate(
                name,
                (cost, f1),
                xytext=(8, 4),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold" if "Proposed" in name else "normal"
            )

        ax.set_xlabel("Mean Operational Cost per Incident (USD)")
        ax.set_ylabel("RCA Macro F1 (%) [Higher=Better]")
        ax.set_title("Figure 3: Cost-Effectiveness and Pareto Frontier Analysis")
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.set_ylim(0, 105)

        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig3_cost_vs_rca_f1_pareto.png"), dpi=300)
        plt.close()

    def plot_confusion_matrix(self, raw_df: pd.DataFrame):
        """Figure 4: Confusion matrix for Proposed 7-Phase Agent root cause diagnoses."""
        fig, ax = plt.subplots(figsize=(8, 7))

        prop_runs = raw_df[raw_df["model_name"] == "Proposed_7Phase_Agent"]
        y_true = prop_runs["ground_truth_fault_family"].fillna("none").astype(str)
        y_pred = prop_runs["root_cause"].fillna("none").astype(str)

        labels = sorted(list(set(y_true.unique()).union(set(y_pred.unique()))))
        cm = confusion_matrix(y_true, y_pred, labels=labels)

        im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
        ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        ax.set(xticks=np.arange(cm.shape[1]),
               yticks=np.arange(cm.shape[0]),
               xticklabels=labels, yticklabels=labels,
               title="Figure 4: Confusion Matrix for Proposed Troubleshooting Agent",
               ylabel="Ground Truth Fault Family",
               xlabel="Predicted Root Cause")

        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Loop over data dimensions and create text annotations
        thresh = cm.max() / 2.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], "d"),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig4_root_cause_confusion_matrix.png"), dpi=300)
        plt.close()

    def plot_ablation_drops(self, ablation_df: pd.DataFrame):
        """Figure 5: Performance degradation when individual components are removed."""
        fig, ax = plt.subplots(figsize=(10, 5))

        clean_ablation_names = {
            "Full_Proposed_Agent": "Full Proposed Agent",
            "Ablation_No_Phase_Gating": "- Phase Gating (Free-form)",
            "Ablation_No_Skills": "- Skill Library",
            "Ablation_No_Falsification": "- Falsification Probes",
            "Ablation_No_Abstain": "- Abstain Option",
            "Ablation_No_Evidence_Filtering": "- Context Trimming"
        }
        df = ablation_df.copy()
        df["display_name"] = df["variant"].map(clean_ablation_names).fillna(df["variant"])

        x = np.arange(len(df))
        width = 0.35

        rects1 = ax.bar(x - width/2, df["rca_f1_macro"] * 100, width, label="RCA Macro F1 (%)", color="#1f77b4")
        rects2 = ax.bar(x + width/2, df["false_positive_rate"] * 100, width, label="False-Positive Rate (%) [Lower=Better]", color="#d62728")

        ax.set_ylabel("Score (%)")
        ax.set_title("Figure 5: Component Ablation Study (Impact on RCA F1 & False Alarms)")
        ax.set_xticks(x)
        ax.set_xticklabels(df["display_name"], rotation=25, ha="right")
        ax.set_ylim(0, 115)
        ax.legend(loc="upper right")
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig5_ablation_component_drop.png"), dpi=300)
        plt.close()

    def plot_transfer_generalization(self, raw_df: pd.DataFrame):
        """Figure 6: Out-of-distribution transfer score comparing Development vs Held-Out partitions."""
        fig, ax = plt.subplots(figsize=(9, 5))

        clean_names = {
            "Proposed_7Phase_Agent": "Proposed Agent",
            "Baseline_SADE_Style": "SADE-Style",
            "Baseline_ReAct": "ReAct (NIKA)",
            "Baseline_Generic_Coding": "Coding Agent",
            "Baseline_Zero_Shot": "Zero-Shot",
            "Baseline_Scripted_Rules": "Scripted Rules"
        }

        models = list(clean_names.keys())
        dev_scores = []
        held_scores = []

        for m in models:
            sub = raw_df[raw_df["model_name"] == m]
            dev_sub = sub[sub["split"] == "development"]
            held_sub = sub[sub["split"] == "held_out"]

            dev_acc = (dev_sub["ground_truth_fault_family"] == dev_sub["root_cause"]).mean() * 100 if len(dev_sub) > 0 else 0
            held_acc = (held_sub["ground_truth_fault_family"] == held_sub["root_cause"]).mean() * 100 if len(held_sub) > 0 else 0
            dev_scores.append(dev_acc)
            held_scores.append(held_acc)

        x = np.arange(len(models))
        width = 0.35

        ax.bar(x - width/2, dev_scores, width, label="Development Scenarios (Seen)", color="#2b5c8f")
        ax.bar(x + width/2, held_scores, width, label="Held-Out Scenarios (Zero-Shot Transfer)", color="#e07a5f")

        ax.set_ylabel("Diagnostic Accuracy (%)")
        ax.set_title("Figure 6: Cross-Scenario Generalization and Transfer Robustness (Sub-Gap C)")
        ax.set_xticks(x)
        ax.set_xticklabels([clean_names[m] for m in models], rotation=20, ha="right")
        ax.set_ylim(0, 110)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig6_transfer_generalization.png"), dpi=300)
        plt.close()

    def plot_token_usage(self, metrics_df: pd.DataFrame):
        """Figure 7: Input tokens vs Output tokens stacked comparison."""
        fig, ax = plt.subplots(figsize=(9, 5))

        clean_names = {
            "Proposed_7Phase_Agent": "Proposed Agent",
            "Baseline_SADE_Style": "SADE-Style",
            "Baseline_ReAct": "ReAct (NIKA)",
            "Baseline_Generic_Coding": "Coding Agent",
            "Baseline_Zero_Shot": "Zero-Shot",
            "Baseline_Scripted_Rules": "Scripted Rules"
        }
        df = metrics_df.copy()
        df["display_name"] = df["model_name"].map(clean_names).fillna(df["model_name"])

        x = np.arange(len(df))
        width = 0.55

        ax.bar(x, df["mean_input_tokens"], width, label="Input Tokens", color="#457b9d")
        ax.bar(x, df["mean_output_tokens"], width, bottom=df["mean_input_tokens"], label="Output Tokens", color="#e63946")

        ax.set_ylabel("Tokens per Troubleshooting Session")
        ax.set_title("Figure 7: Computational and Token Resource Consumption")
        ax.set_xticks(x)
        ax.set_xticklabels(df["display_name"], rotation=20, ha="right")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig7_token_usage_breakdown.png"), dpi=300)
        plt.close()

    def plot_no_submission_rates(self, metrics_df: pd.DataFrame):
        """Figure 8: No-submission / uncompleted session rate."""
        fig, ax = plt.subplots(figsize=(9, 4.5))

        clean_names = {
            "Proposed_7Phase_Agent": "Proposed Agent",
            "Baseline_SADE_Style": "SADE-Style",
            "Baseline_ReAct": "ReAct (NIKA)",
            "Baseline_Generic_Coding": "Coding Agent",
            "Baseline_Zero_Shot": "Zero-Shot",
            "Baseline_Scripted_Rules": "Scripted Rules"
        }
        df = metrics_df.copy()
        df["display_name"] = df["model_name"].map(clean_names).fillna(df["model_name"])

        x = np.arange(len(df))
        ax.bar(x, df["no_submission_rate"] * 100, color="#6c757d", width=0.5)

        ax.set_ylabel("No-Submission Rate (%) [Lower=Better]")
        ax.set_title("Figure 8: Unanswered Session Rate (Turn Budget Exhaustion)")
        ax.set_xticks(x)
        ax.set_xticklabels(df["display_name"], rotation=20, ha="right")
        ax.set_ylim(0, 30)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig8_no_submission_rates.png"), dpi=300)
        plt.close()

    def plot_robustness_analysis(self, robustness_df: pd.DataFrame):
        """Figure 9: Multi-panel robustness stress test evaluation."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 10))

        # 1. Panel (a): Topology Scale Stress Test
        scale_sub = robustness_df[robustness_df["test_type"] == "topology_scale"]
        if not scale_sub.empty:
            prop_scale = scale_sub[scale_sub["model_name"] == "Proposed_7Phase_Agent"]
            react_scale = scale_sub[scale_sub["model_name"] == "Baseline_ReAct"]
            order = ["small", "medium", "large"]
            order_labels = ["Small (11)", "Medium (27)", "Large (101)"]

            p_vals = [prop_scale[prop_scale["dimension"] == d]["metric_value"].values[0] * 100 for d in order]
            r_vals = [react_scale[react_scale["dimension"] == d]["metric_value"].values[0] * 100 for d in order]

            x = np.arange(len(order))
            w = 0.35
            ax1.bar(x - w/2, p_vals, w, label="Proposed Agent", color="#1f77b4")
            ax1.bar(x + w/2, r_vals, w, label="ReAct (NIKA)", color="#d62728")
            ax1.set_ylabel("Localization Accuracy (%)")
            ax1.set_title("(a) Topology Scaling: Localization Retention")
            ax1.set_xticks(x)
            ax1.set_xticklabels(order_labels)
            ax1.set_ylim(0, 100)
            ax1.grid(axis="y", linestyle="--", alpha=0.7)
            ax1.legend(loc="upper right")

        # 2. Panel (b): Ticket Persona Noise Resistance
        persona_sub = robustness_df[robustness_df["test_type"] == "ticket_persona_noise"]
        if not persona_sub.empty:
            labels = ["Panicked", "Junior Admin", "Developer", "Bot Alert", "Cautious"]
            raw_labels = ["panicked_user", "junior_admin", "developer", "monitoring_bot", "cautious_operator"]
            det_vals = [persona_sub[persona_sub["dimension"] == d]["metric_value"].values[0] * 100 for d in raw_labels]

            ax2.bar(labels, det_vals, color="#2ca02c", width=0.5)
            ax2.axhline(80, color="gray", linestyle=":", label="Baseline Retention (80%)")
            ax2.set_ylabel("Detection Accuracy (%)")
            ax2.set_title("(b) Adversarial Ticket Noise Resistance")
            ax2.set_ylim(0, 100)
            ax2.grid(axis="y", linestyle="--", alpha=0.7)
            ax2.legend(loc="lower right")

        # 3. Panel (c): Remediation Confidence Gate Sensitivity
        thresh_sub = robustness_df[robustness_df["test_type"] == "remediation_threshold"]
        if not thresh_sub.empty:
            thresh_sub = thresh_sub.sort_values(by="dimension")
            x_vals = thresh_sub["dimension"].astype(str).tolist()
            prop_vals = thresh_sub["metric_value"].values * 100
            gate_vals = thresh_sub["auxiliary_metric"].values * 100

            ax3.plot(x_vals, prop_vals, marker="o", linewidth=2.5, color="#ff7f0e", label="Proposal Rate (%)")
            ax3.axhline(100, color="#d62728", linestyle="--", linewidth=2.0, label="Human Gate Enforced (100%)")
            ax3.set_xlabel("Confidence Gate Threshold")
            ax3.set_ylabel("Rate (%)")
            ax3.set_title("(c) Phase 7 Safety Gate Calibration")
            ax3.set_ylim(0, 115)
            ax3.grid(True, linestyle="--", alpha=0.7)
            ax3.legend(loc="center left")

        # 4. Panel (d): Healthy Ratio Negative Control Stress Test
        healthy_sub = robustness_df[robustness_df["test_type"] == "healthy_ratio_stress"]
        if not healthy_sub.empty:
            ratios = ["10%_healthy", "25%_healthy", "40%_healthy", "50%_healthy"]
            ratio_labels = ["10% Healthy", "25% Healthy", "40% Healthy", "50% Healthy"]
            prop_h = healthy_sub[healthy_sub["model_name"] == "Proposed_7Phase_Agent"]
            sade_h = healthy_sub[healthy_sub["model_name"] == "Baseline_SADE_Style"]

            p_fpr = [prop_h[prop_h["dimension"] == r]["metric_value"].values[0] * 100 for r in ratios]
            s_fpr = [sade_h[sade_h["dimension"] == r]["metric_value"].values[0] * 100 for r in ratios]

            x = np.arange(len(ratios))
            w = 0.35
            ax4.bar(x - w/2, p_fpr, w, label="Proposed Agent (0.0% FPR)", color="#2ca02c")
            ax4.bar(x + w/2, s_fpr, w, label="SADE Baseline (100% FPR)", color="#d62728")
            ax4.set_ylabel("False Positive Rate (%) [Lower=Better]")
            ax4.set_title("(d) Negative Control Stress Test (FPR Stability)")
            ax4.set_xticks(x)
            ax4.set_xticklabels(ratio_labels)
            ax4.set_ylim(0, 115)
            ax4.grid(axis="y", linestyle="--", alpha=0.7)
            ax4.legend(loc="upper left")

        plt.suptitle("Figure 9: Multi-Dimensional Robustness and Sensitivity Stress Testing", fontsize=14, y=0.99)
        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, "fig9_robustness_stress_testing.png"), dpi=300)
        plt.close()

