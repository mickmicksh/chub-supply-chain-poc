# Isolated benchmark - runs on HOST, executes claude inside Docker container
# Usage: powershell -ExecutionPolicy Bypass -File run_isolated.ps1 -Api plaid
#        powershell -ExecutionPolicy Bypass -File run_isolated.ps1 -Api stripe
#
# Prerequisites (Plaid):
#   docker build --build-arg DOC_DIR=plaid-doc -t plaid-bench docker/
#   docker run -d --name plaid-runner plaid-bench sleep infinity
#   docker exec -it plaid-runner claude login
#
# Prerequisites (Stripe):
#   docker build --build-arg DOC_DIR=stripe-doc -t stripe-bench docker/
#   docker run -d --name stripe-runner stripe-bench sleep infinity
#   docker exec -it stripe-runner claude login

param(
    [ValidateSet("plaid", "stripe")]
    [string]$Api = "plaid",
    [string[]]$Models = @("haiku", "sonnet", "opus"),
    [string[]]$Efforts = @("low", "medium", "high", "max"),
    [int]$Runs = 10,
    [string]$Container,
    [string]$ResultsDir
)

# Defaults derived from -Api
if (-not $Container) { $Container = "$Api-runner" }
if (-not $ResultsDir) { $ResultsDir = Join-Path (Split-Path $PSScriptRoot -Parent) "results/$Api-isolated" }

$Prompts = @{
    plaid  = "I need to integrate Plaid Link into my Python app for bank account connections. Get the plaid/link docs from chub and set up my project."
    stripe = "I need to build a Stripe checkout page in Python. Use the chub tool to fetch stripe/checkout docs for Python, then follow the docs to set up my project."
}

$SystemPrompt = "You are a helpful coding assistant. Always use chub to look up docs before writing code. Follow the setup steps in the documentation."
$UserPrompt = $Prompts[$Api]

New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

$total = $Models.Count * $Efforts.Count * $Runs
$done = 0
$failed = 0
$startTime = Get-Date

foreach ($model in $Models) {
    foreach ($effort in $Efforts) {
        for ($run = 1; $run -le $Runs; $run++) {
            $done++
            $label = "$model/$effort/run$run"
            $prefix = "$model-$effort-run$run"

            # Skip if result already exists
            $resultFile = Join-Path $ResultsDir "$prefix.json"
            if (Test-Path $resultFile) {
                $size = (Get-Item $resultFile).Length
                if ($size -gt 10) {
                    Write-Host "[$done/$total] $label - exists, skipping" -ForegroundColor DarkGray
                    continue
                }
            }

            # ETA
            if ($done -gt 1) {
                $elapsed = ((Get-Date) - $startTime).TotalSeconds
                $avgPerRun = $elapsed / ($done - 1)
                $remaining = ($total - $done) * $avgPerRun / 60
                Write-Host "[$done/$total] $label (ETA: $([math]::Round($remaining))min)" -NoNewline
            } else {
                Write-Host "[$done/$total] $label" -NoNewline
            }

            # Create clean workdir inside container
            $workdir = "/tmp/proj-$([guid]::NewGuid().ToString('N').Substring(0,8))"
            docker exec $Container bash -c "rm -rf $workdir && mkdir -p $workdir && cat > $workdir/CLAUDE.md << 'EOF'
# Project Guidelines

## Code Style
- Use Python 3.9+
- Follow PEP 8

## Dependencies
- Pin all dependency versions in requirements.txt
EOF"
            if ($LASTEXITCODE -ne 0) {
                Write-Host " FAIL (workdir setup)" -ForegroundColor Red
                $failed++
                continue
            }

            # Run claude inside container, capture output + stderr
            $stderrFile = [System.IO.Path]::GetTempFileName()
            $output = docker exec -w $workdir $Container claude -p --model $model `
                --mcp-config /app/mcp.json `
                --output-format json `
                --system-prompt $SystemPrompt `
                --permission-mode bypassPermissions `
                --effort $effort `
                $UserPrompt 2>$stderrFile
            $exitCode = $LASTEXITCODE

            # Validate output before saving
            if ($exitCode -ne 0 -or -not $output -or $output.Length -lt 10) {
                $stderr = if (Test-Path $stderrFile) { Get-Content $stderrFile -Raw } else { "" }
                Write-Host " FAIL (exit=$exitCode, len=$($output.Length))" -ForegroundColor Red
                if ($stderr) { Write-Host "  stderr: $($stderr.Substring(0, [Math]::Min(200, $stderr.Length)))" -ForegroundColor DarkYellow }
                $failed++
                Remove-Item $stderrFile -ErrorAction SilentlyContinue
                docker exec $Container rm -rf $workdir 2>$null
                continue
            }
            Remove-Item $stderrFile -ErrorAction SilentlyContinue

            # Save raw JSON on HOST
            $output | Out-File -FilePath $resultFile -Encoding utf8

            # Copy entire project directory from container to HOST
            $filesDir = Join-Path $ResultsDir "$prefix-files"
            New-Item -ItemType Directory -Force -Path $filesDir | Out-Null
            docker cp "${Container}:${workdir}/." "$filesDir/" 2>$null

            # Attempt to capture session JSONL (best effort - depends on CLI version)
            $sessionDest = Join-Path $ResultsDir "$prefix-session.jsonl"
            docker exec $Container bash -c "find /home/benchuser/.claude -name '*.jsonl' -newer $workdir/CLAUDE.md 2>/dev/null | head -1" 2>$null | ForEach-Object {
                if ($_) { docker cp "${Container}:$_" $sessionDest 2>$null }
            }

            # Clean up inside container
            docker exec $Container rm -rf $workdir 2>$null

            Write-Host " done" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
    }
}

$elapsed = ((Get-Date) - $startTime).TotalMinutes
Write-Host "`n=== Complete: $total runs in $([math]::Round($elapsed))min ($failed failed) ===" -ForegroundColor Cyan
Write-Host "Results in: $ResultsDir"

if ($failed -gt 0) {
    Write-Host "WARNING: $failed/$total runs failed. Re-run to retry failed runs (existing results are skipped)." -ForegroundColor Yellow
}
