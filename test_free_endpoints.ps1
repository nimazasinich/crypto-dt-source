# Free Resources Self-Test (PowerShell)
# Tests connectivity to free crypto APIs and backend endpoints

$PORT = if ($env:PORT) { $env:PORT } else { "7860" }
$BACKEND_BASE = "http://localhost:$PORT"

$tests = @(
    @{
        Name = "CoinGecko Ping"
        Url = "https://api.coingecko.com/api/v3/ping"
        Required = $true
    },
    @{
        Name = "Binance Klines (BTC/USDT)"
        Url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=1"
        Required = $true
    },
    @{
        Name = "Alternative.me Fear & Greed"
        Url = "https://api.alternative.me/fng/"
        Required = $true
    },
    @{
        Name = "Backend Health"
        Url = "$BACKEND_BASE/health"
        Required = $true
    },
    @{
        Name = "Backend API Health"
        Url = "$BACKEND_BASE/api/health"
        Required = $false
    },
    @{
        Name = "HF Health"
        Url = "$BACKEND_BASE/api/hf/health"
        Required = $false
    },
    @{
        Name = "HF Registry Models"
        Url = "$BACKEND_BASE/api/hf/registry?kind=models"
        Required = $false
    }
)

Write-Host ("=" * 60)
Write-Host "Free Resources Self-Test"
Write-Host "Backend: $BACKEND_BASE"
Write-Host ("=" * 60)

$passed = 0
$failed = 0
$skipped = 0

foreach ($test in $tests) {
    Write-Host -NoNewline ("{0,-40} ... " -f $test.Name)
    
    try {
        $response = Invoke-RestMethod -Uri $test.Url -TimeoutSec 8 -ErrorAction Stop
        Write-Host -ForegroundColor Green "OK" -NoNewline
        Write-Host " $($test.Required ? 'REQ' : 'OPT')"
        $passed++
    }
    catch {
        Write-Host -ForegroundColor Red "ERROR" -NoNewline
        Write-Host " $($_.Exception.Message)"
        if ($test.Required) {
            $failed++
        } else {
            $skipped++
        }
    }
}

Write-Host ("=" * 60)
Write-Host "Results: $passed passed, $failed failed, $skipped skipped"
Write-Host ("=" * 60)

if ($failed -gt 0) {
    Write-Host -ForegroundColor Red "Some required tests failed!"
    exit 1
} else {
    Write-Host -ForegroundColor Green "All required tests passed!"
    exit 0
}
