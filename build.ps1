<#
.SYNOPSIS
    Launches a local HTTP server for the Play Pass Directory web app and opens it in the default browser.

.PARAMETER Port
    Starting port to bind the local HTTP server to (auto-increments if already in use). Default: 8090.

.PARAMETER Sync
    Fetch the latest Google Play Pass catalog from Ytechb before starting the server.

.PARAMETER NoRun
    Only run the data check/sync step without starting the HTTP server or opening the browser.
#>
param(
    [int]$Port = 8090,
    [switch]$Sync,
    [switch]$NoRun
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Sync dataset if requested or if data.js is missing
if ($Sync -or -not (Test-Path (Join-Path $ScriptDir "data.js"))) {
    Write-Host "[PlayPass] Syncing dataset from Ytechb..." -ForegroundColor Cyan
    python (Join-Path $ScriptDir "sync.py")
}

if ($NoRun) {
    Write-Host "[PlayPass] Ready (-NoRun specified, skipping server launch)." -ForegroundColor Green
    exit 0
}

# 2. Find an available port starting at $Port
function Test-PortAvailable([int]$TestPort) {
    $listener = $null
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $TestPort)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    } finally {
        if ($null -ne $listener) {
            $listener.Stop()
        }
    }
}

while (-not (Test-PortAvailable $Port)) {
    Write-Host "[PlayPass] Port $Port is busy, trying $($Port + 1)..." -ForegroundColor Yellow
    $Port++
}

$Url = "http://localhost:$Port/"

# 3. Start background Python HTTP server in a new window or process and open browser
Write-Host ""
Write-Host "==========================================================" -ForegroundColor DarkGray
Write-Host "  Google Play Pass Directory" -ForegroundColor Green
Write-Host "  Serving from : $ScriptDir" -ForegroundColor Gray
Write-Host "  Local URL    : $Url" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor DarkGray
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Launch default browser after a brief moment
Start-Process $Url

# Run Python's built-in HTTP server attached to this console so Ctrl+C cleanly stops it
python -m http.server $Port --bind 127.0.0.1 --directory $ScriptDir
