<#
.SYNOPSIS
  Builds HANA Script Studio for Windows: runs the tests, publishes a self-contained app,
  creates a portable zip and, if Inno Setup 6 is installed, the Setup.exe installer.

.EXAMPLE
  .\build-windows.ps1                 # version 1.0.0
  .\build-windows.ps1 -Version 1.2.0
  .\build-windows.ps1 -SkipTests

Output goes to .\artifacts (installer, portable zip) and .\publish\win-x64 (raw app files).
Requirements: .NET SDK 8. The installer additionally needs Inno Setup 6 (https://jrsoftware.org/isdl.php).
#>
param(
    [string]$Version = "1.0.0",
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    throw ".NET SDK 8 was not found. Install it from https://dotnet.microsoft.com/download/dotnet/8.0 and run this script again."
}

if (-not $SkipTests) {
    Write-Host "== Running tests" -ForegroundColor Cyan
    dotnet test -c Release
    if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
}

Write-Host "== Publishing (self-contained, win-x64)" -ForegroundColor Cyan
if (Test-Path publish\win-x64) { Remove-Item publish\win-x64 -Recurse -Force }
dotnet publish src\HanaScriptStudio -c Release -r win-x64 --self-contained -p:DebugType=none -p:Version=$Version -o publish\win-x64
if ($LASTEXITCODE -ne 0) { throw "Publish failed." }

New-Item -ItemType Directory -Force artifacts | Out-Null

Write-Host "== Creating portable zip" -ForegroundColor Cyan
$zip = "artifacts\HanaScriptStudio-portable-win-x64.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path publish\win-x64\* -DestinationPath $zip

$iscc = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($iscc) {
    Write-Host "== Building installer" -ForegroundColor Cyan
    & $iscc "/DAppVersion=$Version" installer\HanaScriptStudio.iss
    if ($LASTEXITCODE -ne 0) { throw "Installer build failed." }
} else {
    Write-Warning "Inno Setup 6 not found, skipping the installer. Install it from https://jrsoftware.org/isdl.php and run the script again."
}

Write-Host ""
Write-Host "Done. Files in .\artifacts:" -ForegroundColor Green
Get-ChildItem artifacts | Format-Table Name, @{N="Size (MB)"; E={[math]::Round($_.Length/1MB,1)}}
Write-Host "Quick test without installing: .\publish\win-x64\HanaScriptStudio.exe"
