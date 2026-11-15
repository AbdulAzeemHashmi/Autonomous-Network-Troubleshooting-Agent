# Autonomous Network Troubleshooting Agent: Phase 3 One-Click Runner (PowerShell)
# Course: Computer Networks (CS-3001) | FAST-NUCES
# Authors: Abdul Azeem (24I-2013), Taha Amjad (24K-0007)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AUTONOMOUS NETWORK TROUBLESHOOTING AGENT: ONE-CLICK REPRODUCIBILITY SUITE" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Running automated unit test suite (32 tests)..." -ForegroundColor Yellow
pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Unit test suite encountered failures!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n[2/2] Running complete Phase 3 benchmark pipeline..." -ForegroundColor Yellow
python run_all.py --config configs/experiment_config.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Benchmark pipeline encountered an error!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "[SUCCESS] All 32 unit tests passed and experimental evaluation completed." -ForegroundColor Green
Write-Host "Publication figures saved to: figures/ (9 figures)" -ForegroundColor Green
Write-Host "Academic research report saved to: docs/Phase3_Report.pdf" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
