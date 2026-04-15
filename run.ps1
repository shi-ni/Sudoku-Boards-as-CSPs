$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Prefer local virtual environments, then fall back to Python on PATH.
$pythonCandidates = @(
    (Join-Path $scriptDir ".venv\\Scripts\\python.exe"),
    (Join-Path $scriptDir "..\\.venv\\Scripts\\python.exe")
)

$pythonExe = $pythonCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $pythonExe) {
    $pythonExe = "python"
}

Push-Location $scriptDir
try {
    & $pythonExe -m main @args
}
finally {
    Pop-Location
}
