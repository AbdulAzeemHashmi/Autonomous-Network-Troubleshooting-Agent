"""
Single-Command End-to-End Experimental Pipeline
Grounding: Phase 3 Requirement (Reproducible experimental evaluation).
Usage:
    python run_all.py --config configs/experiment_config.yaml
"""

import argparse
import os
import sys
import time

from code.experiments.runner import ExperimentRunner
from code.experiments.ablation import AblationStudy
from code.experiments.error_analysis import ErrorTaxonomyAnalyzer
from code.visualization.plots import PlotGenerator
from export_pdf import convert_markdown_to_pdf


def main():
    parser = argparse.ArgumentParser(description="Autonomous Network Troubleshooting Agent - Phase 3 Pipeline")
    parser.add_argument("--config", type=str, default="configs/experiment_config.yaml", help="Path to experiment config YAML")
    parser.add_argument("--num_incidents", type=int, default=120, help="Number of benchmark incidents to evaluate")
    parser.add_argument("--num_ablations", type=int, default=60, help="Number of ablation incidents to evaluate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--use_live_llm", action="store_true", help="Enable live Google Gemini LLM API calls")
    parser.add_argument("--gemini_api_key", type=str, default=None, help="Google Gemini API Key")
    parser.add_argument("--gemini_model", type=str, default="gemini-1.5-flash", help="Gemini model name (gemini-1.5-flash, gemini-2.0-flash, gemini-1.5-pro)")
    parser.add_argument("--skip_pdf", action="store_true", help="Skip compilation of Phase3_Report.pdf")
    args = parser.parse_args()

    print("================================================================================")
    print("AUTONOMOUS NETWORK TROUBLESHOOTING AGENT - PHASE 3 EXPERIMENTAL EVALUATION")
    print("Course: Computer Networks | FAST-NUCES")
    print("Authors: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)")
    print("LLM Engine: Google Gemini API (gemini-1.5-flash / gemini-2.0-flash)")
    print("================================================================================")

    start_time = time.time()

    # Step 1: Run Main Experimental Benchmark
    print("\n>>> STEP 1 / 4: Executing Multi-Model Benchmark Suite...")
    runner = ExperimentRunner(
        config_path=args.config,
        use_live_llm=args.use_live_llm,
        gemini_api_key=args.gemini_api_key,
        gemini_model=args.gemini_model
    )
    raw_df = runner.run_benchmark(
        num_incidents=args.num_incidents,
        output_csv="results/raw_runs.csv",
        seed=args.seed
    )

    # Step 2: Run Component Ablation Studies
    print("\n>>> STEP 2 / 4: Executing Component Ablation Studies...")
    ablation_study = AblationStudy(
        num_incidents=args.num_ablations,
        seed=args.seed,
        use_live_llm=args.use_live_llm,
        gemini_api_key=args.gemini_api_key,
        gemini_model=args.gemini_model
    )
    ablation_df = ablation_study.run_ablations(output_csv="results/ablation_results.csv")

    # Step 3: Failure Taxonomy & Error Analysis
    print("\n>>> STEP 3 / 4: Analyzing Pitfall Taxonomy (Kim et al. 2026)...")
    error_analyzer = ErrorTaxonomyAnalyzer()
    summary_tax_df, classified_records = error_analyzer.classify_run_failures(raw_df)
    error_analyzer.generate_error_report(
        summary_tax_df,
        classified_records,
        output_csv="results/failure_taxonomy.csv",
        output_md="docs/error_analysis.md"
    )

    # Step 4: Publication Visualization Generation
    print("\n>>> STEP 4 / 4: Generating Publication-Grade Visualizations...")
    plotter = PlotGenerator(figures_dir="figures")
    plotter.generate_all_plots(
        raw_runs_path="results/raw_runs.csv",
        metrics_summary_path="results/metrics_summary.csv",
        ablation_results_path="results/ablation_results.csv"
    )

    # Optional Step 5: Export Academic PDF Report
    pdf_path = "docs/Phase3_Report.pdf"
    if not args.skip_pdf and os.path.exists("docs/Phase3_Report.md"):
        print("\n>>> STEP 5 / 5: Compiling Publication-Grade Academic PDF Report...")
        try:
            convert_markdown_to_pdf("docs/Phase3_Report.md", pdf_path)
            print(f"[+] Successfully compiled academic report to '{pdf_path}'")
        except Exception as e:
            print(f"[-] PDF compilation notice: {e}")

    total_elapsed = time.time() - start_time
    print("\n================================================================================")
    print(f"[SUCCESS] Complete experimental pipeline finished in {total_elapsed:.2f} seconds.")
    print("Artifacts generated:")
    print("  - Raw Execution Runs:      results/raw_runs.csv")
    print("  - Summary Metrics & CIs:   results/metrics_summary.csv")
    print("  - Statistical Tests:       results/statistical_tests.csv")
    print("  - Ablation Results:        results/ablation_results.csv")
    print("  - Failure Taxonomy:        results/failure_taxonomy.csv")
    print("  - Error Analysis Report:   docs/error_analysis.md")
    print("  - Publication Figures:     figures/ (8 PNG figures)")
    if not args.skip_pdf and os.path.exists(pdf_path):
        print(f"  - Academic PDF Report:     {pdf_path}")
    print("================================================================================")


if __name__ == "__main__":
    main()
