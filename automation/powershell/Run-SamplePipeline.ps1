[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$NoResetDatabase,
    [string]$PythonCommand = "python",
    [string]$RepoRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    param([string]$RequestedRoot)

    if ([string]::IsNullOrWhiteSpace($RequestedRoot)) {
        return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
    }

    return (Resolve-Path -LiteralPath $RequestedRoot).Path
}

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function New-UniquePath {
    param(
        [string]$Directory,
        [string]$FileName
    )

    $candidate = Join-Path $Directory $FileName
    if (-not (Test-Path -LiteralPath $candidate)) {
        return $candidate
    }

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
    $extension = [System.IO.Path]::GetExtension($FileName)
    $counter = 1

    while ($true) {
        $nextName = "{0}_{1}{2}" -f $baseName, $counter, $extension
        $candidate = Join-Path $Directory $nextName
        if (-not (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
        $counter += 1
    }
}

$rootPath = Resolve-RepoRoot -RequestedRoot $RepoRoot
$sampleFile = Join-Path $rootPath "data\sample_input\supplier_product_records_sample.csv"
$intakeDirectory = Join-Path $rootPath "data\intake"
$watchScript = Join-Path $rootPath "automation\powershell\Watch-IntakeFolder.ps1"

Ensure-Directory -Path $intakeDirectory

if (-not (Test-Path -LiteralPath $sampleFile)) {
    throw ("Sample file not found: {0}" -f $sampleFile)
}

$sampleName = "phase2_sample_{0}.csv" -f (Get-Date -Format "yyyyMMddHHmmss")
$intakeCopy = New-UniquePath -Directory $intakeDirectory -FileName $sampleName

if ($DryRun) {
    Write-Host ("[DRY RUN] Would copy sample file to intake: {0}" -f $intakeCopy)
}
else {
    Copy-Item -LiteralPath $sampleFile -Destination $intakeCopy
    Write-Host ("Copied public-safe sample file to intake: {0}" -f $intakeCopy)
}

$watchParams = @{
    Once = $true
    Reprocess = $true
    FileName = [System.IO.Path]::GetFileName($intakeCopy)
    PythonCommand = $PythonCommand
    RepoRoot = $rootPath
}

if ($DryRun) {
    $watchParams.DryRun = $true
}

if (-not $NoResetDatabase) {
    $watchParams.ResetDatabase = $true
}

Write-Host ("Invoking intake workflow: {0} -Once -Reprocess -FileName {1}" -f $watchScript, $watchParams.FileName)
if ($DryRun) {
    Write-Host "[DRY RUN] Sample file was not copied. No watcher execution performed."
    return
}

& $watchScript @watchParams
