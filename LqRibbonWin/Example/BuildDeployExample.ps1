param(
    [string]$QtBin = "D:\Qt\5.15.2\mingw81_64\bin",
    [string]$MingwBin = "D:\Qt\Tools\mingw810_64\bin",
    [string]$BuildDir = "$env:TEMP\LqRibbonExample-deploy",
    [switch]$KeepBuild,
    [switch]$Run
)

$ErrorActionPreference = "Stop"

function Invoke-CheckedCommand
{
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $FilePath $($Arguments -join ' ')"
    }
}

$projectPath = Join-Path $PSScriptRoot "LqRibbonExample.pro"
$qmakePath = Join-Path $QtBin "qmake.exe"
$deployPath = Join-Path $QtBin "windeployqt.exe"
$makePath = Join-Path $MingwBin "mingw32-make.exe"

foreach ($toolPath in @($qmakePath, $deployPath, $makePath)) {
    if (-not (Test-Path -LiteralPath $toolPath)) {
        throw "Required tool was not found: $toolPath"
    }
}

if ((Test-Path -LiteralPath $BuildDir) -and (-not $KeepBuild)) {
    Remove-Item -LiteralPath $BuildDir -Recurse -Force
}

New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null

$env:PATH = "$QtBin;$MingwBin;$env:PATH"

Push-Location $BuildDir
try {
    Invoke-CheckedCommand $qmakePath @($projectPath, "-spec", "win32-g++", "CONFIG+=release")
    Invoke-CheckedCommand $makePath @("-j4")
}
finally {
    Pop-Location
}

$exePath = Join-Path $BuildDir "release\LqRibbonExample.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
    throw "Example executable was not created: $exePath"
}

Invoke-CheckedCommand $deployPath @("--no-translations", $exePath)

Write-Host "Deployed example:"
Write-Host $exePath

if ($Run) {
    Start-Process -FilePath $exePath -WorkingDirectory (Split-Path $exePath)
}
