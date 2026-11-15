@echo off
REM Autonomous Network Troubleshooting Agent: Phase 3 One-Click Runner
REM Course: Computer Networks (CS-3001) | FAST-NUCES
REM Authors: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)

echo ================================================================================
echo AUTONOMOUS NETWORK TROUBLESHOOTING AGENT: ONE-CLICK REPRODUCIBILITY SUITE
echo ================================================================================

echo.
echo [1/2] Running automated unit test suite (32 tests)...
pytest tests/ -v
if errorlevel 1 (
    echo [-] Unit test suite encountered failures!
    exit /b %errorlevel%
)

echo.
echo [2/2] Running complete Phase 3 benchmark pipeline...
python run_all.py --config configs/experiment_config.yaml
if errorlevel 1 (
    echo [-] Benchmark pipeline encountered an error!
    exit /b %errorlevel%
)

echo.
echo ================================================================================
echo [SUCCESS] All 32 unit tests passed and experimental evaluation completed.
echo Publication figures saved to: figures/ (9 figures)
echo Academic research report saved to: docs/Phase3_Report.pdf
echo ================================================================================
