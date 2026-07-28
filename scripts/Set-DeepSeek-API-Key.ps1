$ErrorActionPreference = "Stop"

$InstallDir = "D:\Backup\Documents\EC"
$CatalogPath = Join-Path $InstallDir "data\user\settings\model_catalog.json"

if (!(Test-Path -LiteralPath $CatalogPath)) {
  Write-Host "DeepTutor model catalog not found: $CatalogPath" -ForegroundColor Red
  exit 1
}

Write-Host "Enter your DeepSeek API key."
Write-Host "Input will be hidden and will only be written to the local DeepTutor model catalog."
Write-Host "Do not paste the key into chat, screenshots, GitHub, README files, or logs."
$SecureKey = Read-Host "DeepSeek API Key" -AsSecureString

$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureKey)
try {
  $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
  if ([string]::IsNullOrWhiteSpace($plain)) {
    Write-Host "No API key was entered. Configuration was not changed." -ForegroundColor Yellow
    exit 1
  }

  $catalog = Get-Content -LiteralPath $CatalogPath -Encoding UTF8 -Raw | ConvertFrom-Json
  $llm = $catalog.services.llm
  if (!$llm.profiles -or $llm.profiles.Count -eq 0) {
    throw "model_catalog.json does not contain an LLM profile."
  }

  $profile = $llm.profiles | Where-Object { $_.id -eq $llm.active_profile_id } | Select-Object -First 1
  if ($null -eq $profile) {
    $profile = $llm.profiles[0]
  }
  $profile.api_key = $plain
  $catalog | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $CatalogPath -Encoding UTF8

  $acl = Get-Acl -LiteralPath $CatalogPath
  $acl.SetAccessRuleProtection($true, $false)
  $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
  $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($user, "FullControl", "Allow")
  $acl.SetAccessRule($rule)
  Set-Acl -LiteralPath $CatalogPath -AclObject $acl

  Write-Host "DeepSeek API key was written to the local DeepTutor configuration."
  Write-Host "Restart DeepTutor, then run scripts\Test-DeepSeek-API.ps1."
} finally {
  if ($bstr -ne [IntPtr]::Zero) {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  }
  Remove-Variable plain -ErrorAction SilentlyContinue
  Remove-Variable SecureKey -ErrorAction SilentlyContinue
}
