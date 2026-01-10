
Param(
	[string]$OutDir = (Join-Path $PSScriptRoot '..\.deploy'),
	[string]$KeyName = 'bhrikutimandap_actions',
	[string]$KeyComment = 'github-actions-bhrikutimandap'
)

$ErrorActionPreference = 'Stop'

function Assert-Command([string]$Name) {
	if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
		throw "Required command not found: $Name. Install OpenSSH Client (Windows Optional Features) or Git for Windows."
	}
}

Assert-Command ssh-keygen

$OutDir = [IO.Path]::GetFullPath($OutDir)
$null = New-Item -ItemType Directory -Force -Path $OutDir

$PrivateKeyPath = Join-Path $OutDir $KeyName
$PublicKeyPath = "$PrivateKeyPath.pub"

if ((Test-Path $PrivateKeyPath) -or (Test-Path $PublicKeyPath)) {
	Write-Host "ERROR: Key files already exist:" -ForegroundColor Red
	if (Test-Path $PrivateKeyPath) { Write-Host "- $PrivateKeyPath" }
	if (Test-Path $PublicKeyPath) { Write-Host "- $PublicKeyPath" }
	Write-Host "Delete/rename them or pass a different -KeyName." -ForegroundColor Yellow
	exit 1
}

Write-Host "Generating new deploy key (NO passphrase)..." -ForegroundColor Cyan

# PowerShell can drop empty-string args for native commands; invoke via cmd.exe to reliably pass: -N ""
$sshKeygenExe = (Get-Command ssh-keygen).Source
$cmdLine = ('"{0}" -t ed25519 -f "{1}" -N "" -C "{2}"' -f $sshKeygenExe, $PrivateKeyPath, $KeyComment)
cmd.exe /c $cmdLine | Out-Null
if ($LASTEXITCODE -ne 0) {
	throw "ssh-keygen failed with exit code $LASTEXITCODE"
}

# Basic sanity checks (do not print key material)
$privateBytes = [IO.File]::ReadAllBytes($PrivateKeyPath)
$privateText = Get-Content -Raw -Path $PrivateKeyPath
$lines = $privateText -split "`n" | ForEach-Object { $_.TrimEnd("`r") }
$firstLine = $lines | Select-Object -First 1
$lastNonEmpty = $lines | Where-Object { $_ -ne "" } | Select-Object -Last 1

Write-Host "Private key file:" -ForegroundColor Green
Write-Host "- $PrivateKeyPath"
Write-Host "  size(bytes): $($privateBytes.Length)"
Write-Host "  first line:  $firstLine"
Write-Host "  last line:   $lastNonEmpty"

Write-Host "Public key file:" -ForegroundColor Green
Write-Host "- $PublicKeyPath"

# Copy base64 to clipboard for GitHub Secret VPS_SSH_KEY_B64
$b64 = [Convert]::ToBase64String($privateBytes)
$b64 | Set-Clipboard
Write-Host "Copied base64(private key bytes) to clipboard." -ForegroundColor Cyan
Write-Host "Create/Update GitHub Secret: VPS_SSH_KEY_B64" -ForegroundColor Cyan
Write-Host "(Paste clipboard content as the value.)" -ForegroundColor Cyan

$pub = Get-Content -Raw -Path $PublicKeyPath
Write-Host ""
Write-Host "Next: add this PUBLIC key to your VPS authorized_keys (safe to share):" -ForegroundColor Yellow
Write-Host $pub
Write-Host ""
Write-Host "Tip: Copy public key to clipboard: Get-Content -Raw '$PublicKeyPath' | Set-Clipboard" -ForegroundColor DarkGray

