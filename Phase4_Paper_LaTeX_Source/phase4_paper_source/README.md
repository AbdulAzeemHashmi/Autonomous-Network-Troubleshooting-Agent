# Phase 4 paper: LaTeX source and reproducibility bundle

Compile (Springer Nature `sn-jnl` class, `sn-basic` style, two-column option):

    pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper

Every number, table and figure derives from the Phase 3 logs:

    # from the Phase 3 repository root (needs results/raw_runs.csv and results/ablation_results.csv)
    export P3_REPO=. P4_OUT=<output folder>
    python analysis/ablation_rerun.py      # per-incident ablation logs + label-harmonised F1
    python analysis/leakage_audit.py       # hides the ground-truth healthy flag from the proposed agent
    python analysis/phase4_analysis.py     # bootstrap CIs, McNemar tests, breakdowns, figures
    python analysis/build_tables.py        # LaTeX table rows and numeric tokens (data/tokens.json)

`results/` holds the per-incident log (raw_runs.csv) and the ablation summary used by the scripts.
`data/` holds all derived statistics (phase4_stats.json, ablation_stats.json, failure attribution).
The scripts import the Phase 3 modules (`code/data`, `code/agent`), so run them inside the Phase 3 repository.
