$ErrorActionPreference = "Continue"

$InstallDir = "D:\Backup\Documents\EC"
$RunDir = Join-Path $InstallDir "run"
$EmbeddingPidFile = Join-Path $RunDir "embedding.pid"
$BackendPidFile = Join-Path $RunDir "backend.pid"
$FrontendPidFile = Join-Path $RunDir "frontend.pid"

function Stop-FromPidFile($PidPath, $Name) {
  if (!(Test-Path -LiteralPath $PidPath)) {
    Write-Host "$Name is not running (no PID file)."
    return
  }
  $pidText = (Get-Content -LiteralPath $PidPath -ErrorAction SilentlyContinue | Select-Object -First 1)
  $pidValue = 0
  if (![int]::TryParse($pidText, [ref]$pidValue)) {
    Remove-Item -LiteralPath $PidPath -Force -ErrorAction SilentlyContinue
    Write-Host "$Name PID file was invalid and has been removed."
    return
  }
  $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
  if ($null -eq $proc) {
    Remove-Item -LiteralPath $PidPath -Force -ErrorAction SilentlyContinue
    Write-Host "$Name was not running; stale PID file removed."
    return
  }

  Write-Host "Stopping $Name PID $pidValue..."
  & taskkill.exe /PID $pidValue /T > $null 2> $null
  Start-Sleep -Seconds 3
  if (Get-Process -Id $pidValue -ErrorAction SilentlyContinue) {
    & taskkill.exe /PID $pidValue /T /F > $null 2> $null
  }
  if (Get-Process -Id $pidValue -ErrorAction SilentlyContinue) {
    Write-Host "$Name PID $pidValue could not be stopped." -ForegroundColor Red
  }
  Remove-Item -LiteralPath $PidPath -Force -ErrorAction SilentlyContinue
}

Stop-FromPidFile $FrontendPidFile "DeepTutor frontend"
Stop-FromPidFile $BackendPidFile "DeepTutor backend"
Stop-FromPidFile $EmbeddingPidFile "DeepTutor local embedding"
Write-Host "Done."
exit 0
