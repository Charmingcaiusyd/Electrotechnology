$ErrorActionPreference = "Stop"

$InstallDir = "D:\Backup\Documents\EC"
$VenvDir = "D:\Backup\Documents\EC.venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$DeepTutorExe = Join-Path $VenvDir "Scripts\deeptutor.exe"
$EmbeddingPort = 8791
$BackendPort = 8001
$FrontendPort = 3782
$EmbeddingUrl = "http://127.0.0.1:$EmbeddingPort"
$BackendUrl = "http://127.0.0.1:$BackendPort"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"
$RunDir = Join-Path $InstallDir "run"
$LogDir = Join-Path $InstallDir "logs"
$EmbeddingPidFile = Join-Path $RunDir "embedding.pid"
$BackendPidFile = Join-Path $RunDir "backend.pid"
$FrontendPidFile = Join-Path $RunDir "frontend.pid"
$EmbeddingScript = Join-Path $InstallDir "scripts\LocalEmbeddingServer.py"

function Fail($Message, $Code = 1) {
  Write-Host ""
  Write-Host "Error: $Message" -ForegroundColor Red
  exit $Code
}

function Test-Http($Url, $TimeoutSec = 2) {
  try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec $TimeoutSec
    return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
  } catch {
    return $false
  }
}

function Test-PidAlive($PidPath) {
  if (!(Test-Path -LiteralPath $PidPath)) { return $false }
  $pidText = (Get-Content -LiteralPath $PidPath -ErrorAction SilentlyContinue | Select-Object -First 1)
  $pidValue = 0
  if (![int]::TryParse($pidText, [ref]$pidValue)) { return $false }
  return [bool](Get-Process -Id $pidValue -ErrorAction SilentlyContinue)
}

function Test-PortFreeOrOwned($Port, $PidPath, $Name) {
  $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($null -eq $conn) { return }
  if (Test-PidAlive $PidPath) { return }
  $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
  $procName = if ($proc) { $proc.ProcessName } else { "unknown" }
  Fail "$Name port $Port is already used by PID $($conn.OwningProcess) ($procName). I will not stop an unknown process."
}

function Wait-HttpReady($Url, $Name, $TimeoutSec) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    if (Test-Http $Url 2) {
      Write-Host "$Name ready: $Url"
      return
    }
    Start-Sleep -Milliseconds 500
  }
  Fail "$Name did not become ready within $TimeoutSec seconds: $Url"
}

Set-Location -LiteralPath $InstallDir
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (!(Test-Path -LiteralPath $PythonExe)) { Fail "Python venv not found: $PythonExe" }
if (!(Test-Path -LiteralPath $DeepTutorExe)) { Fail "DeepTutor executable not found: $DeepTutorExe" }
if (!(Test-Path -LiteralPath (Join-Path $InstallDir "data\user\settings\model_catalog.json"))) {
  Fail "DeepTutor settings not found. Re-run installation or initialize the workspace."
}

$EmbeddingRunning = (Test-PidAlive $EmbeddingPidFile) -and (Test-Http "$EmbeddingUrl/health" 2)
$BackendRunning = (Test-PidAlive $BackendPidFile) -and (Test-Http $BackendUrl 2)
$FrontendRunning = (Test-PidAlive $FrontendPidFile) -and (Test-Http $FrontendUrl 2)

if ((Test-PidAlive $EmbeddingPidFile) -and !$EmbeddingRunning) {
  Fail "Embedding PID exists but the health check failed. Run Stop_DeepTutor.bat first."
}
if ((Test-PidAlive $BackendPidFile) -and !$BackendRunning) {
  Fail "Backend PID exists but the health check failed. Run Stop_DeepTutor.bat first."
}
if ((Test-PidAlive $FrontendPidFile) -and !$FrontendRunning) {
  Fail "Frontend PID exists but the health check failed. Run Stop_DeepTutor.bat first."
}

if ($EmbeddingRunning -and $BackendRunning -and $FrontendRunning) {
  Write-Host "DeepTutor is already running."
  Write-Host "Embedding: $EmbeddingUrl/"
  Write-Host "Frontend: $FrontendUrl/"
  Write-Host "Backend:  $BackendUrl/"
  Start-Process "$FrontendUrl/"
  exit 0
}

Test-PortFreeOrOwned $EmbeddingPort $EmbeddingPidFile "Embedding"
Test-PortFreeOrOwned $BackendPort $BackendPidFile "Backend"
Test-PortFreeOrOwned $FrontendPort $FrontendPidFile "Frontend"

$env:DEEPTUTOR_HOME = $InstallDir
$env:BACKEND_PORT = "$BackendPort"
$env:FRONTEND_PORT = "$FrontendPort"
$env:NEXT_PUBLIC_API_BASE = $BackendUrl
$env:DEEPTUTOR_API_BASE_URL = $BackendUrl
$env:NEXT_PUBLIC_AUTH_ENABLED = "false"
$env:DEEPTUTOR_AUTH_ENABLED = "false"
$env:DEEPTUTOR_EMBEDDING_HOST = "127.0.0.1"
$env:DEEPTUTOR_EMBEDDING_PORT = "$EmbeddingPort"
$env:DEEPTUTOR_LOCAL_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
$env:DEEPTUTOR_FASTEMBED_CACHE = Join-Path $InstallDir "data\user\models\fastembed"
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8:replace"

$runtimeWeb = & $PythonExe -c "from pathlib import Path; import os; os.environ['DEEPTUTOR_HOME']=r'$InstallDir'; from deeptutor.runtime.launcher import _packaged_web_dir, _copy_packaged_web_if_needed; packaged=_packaged_web_dir(); assert packaged is not None, 'packaged web assets not found'; print(_copy_packaged_web_if_needed(packaged, home=Path(r'$InstallDir'), api_base=r'$BackendUrl', auth_enabled=False))"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($runtimeWeb)) {
  Fail "Could not prepare packaged DeepTutor Web runtime."
}
$runtimeWeb = $runtimeWeb.Trim()
$serverJs = Join-Path $runtimeWeb "server.js"
if (!(Test-Path -LiteralPath $serverJs)) { Fail "Frontend server.js not found: $serverJs" }

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$embeddingOutLog = Join-Path $LogDir "embedding_$timestamp.out.log"
$embeddingErrLog = Join-Path $LogDir "embedding_$timestamp.err.log"
$backendOutLog = Join-Path $LogDir "backend_$timestamp.out.log"
$backendErrLog = Join-Path $LogDir "backend_$timestamp.err.log"
$frontendOutLog = Join-Path $LogDir "frontend_$timestamp.out.log"
$frontendErrLog = Join-Path $LogDir "frontend_$timestamp.err.log"

if (!(Test-Path -LiteralPath $EmbeddingScript)) { Fail "Embedding server script not found: $EmbeddingScript" }
if ($EmbeddingRunning) {
  Write-Host "Reusing local embedding service: $EmbeddingUrl/"
} else {
  Write-Host "Starting local embedding service..."
  $embedding = Start-Process -FilePath $PythonExe -ArgumentList @($EmbeddingScript) -WorkingDirectory $InstallDir -PassThru -WindowStyle Hidden -RedirectStandardOutput $embeddingOutLog -RedirectStandardError $embeddingErrLog
  Set-Content -LiteralPath $EmbeddingPidFile -Value $embedding.Id -Encoding ASCII
  Wait-HttpReady "$EmbeddingUrl/health" "Embedding" 180
}

if ($BackendRunning) {
  Write-Host "Reusing DeepTutor backend: $BackendUrl/"
} else {
  Write-Host "Starting DeepTutor backend..."
  $backend = Start-Process -FilePath $DeepTutorExe -ArgumentList @("serve", "--host", "127.0.0.1", "--port", "$BackendPort") -WorkingDirectory $InstallDir -PassThru -WindowStyle Hidden -RedirectStandardOutput $backendOutLog -RedirectStandardError $backendErrLog
  Set-Content -LiteralPath $BackendPidFile -Value $backend.Id -Encoding ASCII
  Wait-HttpReady "$BackendUrl/" "Backend" 60
}

$env:PORT = "$FrontendPort"
$env:HOSTNAME = "127.0.0.1"
$node = (Get-Command node.exe -ErrorAction Stop).Source
if ($FrontendRunning) {
  Write-Host "Reusing DeepTutor frontend: $FrontendUrl/"
} else {
  Write-Host "Starting DeepTutor frontend..."
  $frontend = Start-Process -FilePath $node -ArgumentList @($serverJs) -WorkingDirectory $runtimeWeb -PassThru -WindowStyle Hidden -RedirectStandardOutput $frontendOutLog -RedirectStandardError $frontendErrLog
  Set-Content -LiteralPath $FrontendPidFile -Value $frontend.Id -Encoding ASCII
  Wait-HttpReady "$FrontendUrl/" "Frontend" 120
}

Write-Host ""
Write-Host "DeepTutor started."
Write-Host "Embedding: $EmbeddingUrl/"
Write-Host "Frontend: $FrontendUrl/"
Write-Host "Backend:  $BackendUrl/"
Write-Host "Logs:     $LogDir"
Start-Process "$FrontendUrl/"
exit 0
