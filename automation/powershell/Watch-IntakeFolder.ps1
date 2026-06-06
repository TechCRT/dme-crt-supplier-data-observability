[CmdletBinding()]
param(
    [switch]$Once,
    [switch]$DryRun,
    [switch]$Reprocess,
    [switch]$ResetDatabase,
    [int]$PollSeconds = 10,
    [int]$MaxFiles = 0,
    [string]$FileName = "",
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

function Get-ReportPathFromOutput {
    param([string[]]$OutputLines)

    $reportLine = $OutputLines | Where-Object { $_ -match "^report_path=(.+)$" } | Select-Object -Last 1
    if (-not $reportLine) {
        return $null
    }

    return ($reportLine -replace "^report_path=", "").Trim()
}

function Get-RouteFromReport {
    param([string]$ReportPath)

    if ([string]::IsNullOrWhiteSpace($ReportPath) -or -not (Test-Path -LiteralPath $ReportPath)) {
        return [pscustomobject]@{
            RouteFolder = "rejected"
            RouteStatus = "FAILED_NO_REPORT"
            RunId = ""
            RowsRejected = 0
            RowsWarning = 0
        }
    }

    $payload = Get-Content -Raw -LiteralPath $ReportPath | ConvertFrom-Json
    $rowsRejected = [int]$payload.run.rows_rejected_validation
    $rowsWarning = [int]$payload.run.rows_warning
    $runStatus = [string]$payload.run.status

    if ($rowsRejected -gt 0) {
        return [pscustomobject]@{
            RouteFolder = "rejected"
            RouteStatus = "REJECTED"
            RunId = [string]$payload.run.run_id
            RowsRejected = $rowsRejected
            RowsWarning = $rowsWarning
        }
    }

    if ($rowsWarning -gt 0 -or $runStatus -eq "WARNING") {
        return [pscustomobject]@{
            RouteFolder = "review"
            RouteStatus = "REVIEW"
            RunId = [string]$payload.run.run_id
            RowsRejected = $rowsRejected
            RowsWarning = $rowsWarning
        }
    }

    return [pscustomobject]@{
        RouteFolder = "processed"
        RouteStatus = "PROCESSED"
        RunId = [string]$payload.run.run_id
        RowsRejected = $rowsRejected
        RowsWarning = $rowsWarning
    }
}

function Invoke-PythonValidator {
    param(
        [string]$ProcessingPath,
        [string]$Root,
        [string]$DatabasePath,
        [string]$ReportDirectory,
        [bool]$UseReset
    )

    $oldPythonPath = $env:PYTHONPATH
    $env:PYTHONPATH = Join-Path $Root "src"

    try {
        $pythonArgs = @(
            "-m",
            "dme_crt_supplier_observability.cli",
            "--db-path",
            $DatabasePath,
            "--report-dir",
            $ReportDirectory,
            "validate-file",
            $ProcessingPath
        )

        if ($UseReset) {
            $pythonArgs += "--reset-db"
        }

        Write-Host ("Invoking validator: {0} {1}" -f $PythonCommand, ($pythonArgs -join " "))
        $outputLines = @(& $PythonCommand @pythonArgs 2>&1 | ForEach-Object { $_.ToString() })
        $exitCode = if ($null -eq $LASTEXITCODE) { 0 } else { [int]$LASTEXITCODE }

        return [pscustomobject]@{
            ExitCode = $exitCode
            OutputLines = $outputLines
            ReportPath = Get-ReportPathFromOutput -OutputLines $outputLines
        }
    }
    finally {
        $env:PYTHONPATH = $oldPythonPath
    }
}

function Write-ProcessingMarker {
    param(
        [string]$MarkerPath,
        [string]$SourcePath,
        [string]$FileHash,
        [object]$Route,
        [string]$DestinationPath,
        [string]$ReportPath
    )

    $markerParent = Split-Path -Parent $MarkerPath
    Ensure-Directory -Path $markerParent

    $marker = [ordered]@{
        processed_at = (Get-Date).ToUniversalTime().ToString("o")
        source_path = $SourcePath
        file_hash = $FileHash
        run_id = $Route.RunId
        route_status = $Route.RouteStatus
        destination_path = $DestinationPath
        report_path = $ReportPath
        original_intake_file_preserved = $true
        public_safe_note = "Sample workflow is for mock/public-safe supplier product records only."
    }

    $marker | ConvertTo-Json -Depth 5 | Set-Content -Path $MarkerPath -Encoding utf8
}

function Process-IntakeFile {
    param(
        [System.IO.FileInfo]$CsvFile,
        [string]$Root,
        [bool]$UseReset
    )

    $fileHash = (Get-FileHash -LiteralPath $CsvFile.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $markerPath = Join-Path $script:MarkerDirectory ("{0}.json" -f $fileHash.Substring(0, 16))

    if ((Test-Path -LiteralPath $markerPath) -and -not $Reprocess) {
        Write-Host ("Skipping already processed intake file: {0}" -f $CsvFile.Name)
        return
    }

    $processingName = "{0}_{1}" -f (Get-Date -Format "yyyyMMddHHmmss"), $CsvFile.Name
    $processingPath = New-UniquePath -Directory $script:ProcessingDirectory -FileName $processingName

    if ($DryRun) {
        Write-Host ("[DRY RUN] Would copy {0} to {1}" -f $CsvFile.FullName, $processingPath)
        Write-Host ("[DRY RUN] Would invoke Python validator and route the processing copy.")
        return
    }

    Copy-Item -LiteralPath $CsvFile.FullName -Destination $processingPath
    Write-Host ("Copied intake file to processing: {0}" -f $processingPath)

    $validatorResult = Invoke-PythonValidator `
        -ProcessingPath $processingPath `
        -Root $Root `
        -DatabasePath $script:DatabasePath `
        -ReportDirectory $script:ReportDirectory `
        -UseReset $UseReset

    foreach ($line in $validatorResult.OutputLines) {
        Write-Host $line
    }

    if ($validatorResult.ExitCode -ne 0) {
        $route = [pscustomobject]@{
            RouteFolder = "rejected"
            RouteStatus = "VALIDATOR_FAILED"
            RunId = ""
            RowsRejected = 0
            RowsWarning = 0
        }
        $script:FailureCount += 1
    }
    else {
        $route = Get-RouteFromReport -ReportPath $validatorResult.ReportPath
    }

    $destinationDirectory = Join-Path $Root ("data\{0}" -f $route.RouteFolder)
    $destinationPath = New-UniquePath -Directory $destinationDirectory -FileName ([System.IO.Path]::GetFileName($processingPath))
    Move-Item -LiteralPath $processingPath -Destination $destinationPath

    Write-ProcessingMarker `
        -MarkerPath $markerPath `
        -SourcePath $CsvFile.FullName `
        -FileHash $fileHash `
        -Route $route `
        -DestinationPath $destinationPath `
        -ReportPath $validatorResult.ReportPath

    Write-Host ("Routed processing copy to {0}: {1}" -f $route.RouteStatus, $destinationPath)
}

$rootPath = Resolve-RepoRoot -RequestedRoot $RepoRoot
$script:IntakeDirectory = Join-Path $rootPath "data\intake"
$script:ProcessingDirectory = Join-Path $rootPath "data\processing"
$script:ProcessedDirectory = Join-Path $rootPath "data\processed"
$script:ReviewDirectory = Join-Path $rootPath "data\review"
$script:RejectedDirectory = Join-Path $rootPath "data\rejected"
$script:MarkerDirectory = Join-Path $script:IntakeDirectory ".processed_markers"
$script:DatabasePath = Join-Path $rootPath "data\runtime\supplier_observability.sqlite"
$script:ReportDirectory = Join-Path $rootPath "outputs\run_reports"
$script:FailureCount = 0

@(
    $script:IntakeDirectory,
    $script:ProcessingDirectory,
    $script:ProcessedDirectory,
    $script:ReviewDirectory,
    $script:RejectedDirectory,
    $script:MarkerDirectory,
    (Split-Path -Parent $script:DatabasePath),
    $script:ReportDirectory
) | ForEach-Object { Ensure-Directory -Path $_ }

$resetAvailable = [bool]$ResetDatabase

do {
    $files = @(Get-ChildItem -LiteralPath $script:IntakeDirectory -Filter "*.csv" -File | Sort-Object LastWriteTimeUtc, Name)

    if (-not [string]::IsNullOrWhiteSpace($FileName)) {
        $files = @($files | Where-Object { $_.Name -eq $FileName })
    }

    if ($MaxFiles -gt 0) {
        $files = @($files | Select-Object -First $MaxFiles)
    }

    if ($files.Count -eq 0) {
        Write-Host ("No CSV files detected in {0}" -f $script:IntakeDirectory)
    }

    foreach ($file in $files) {
        Process-IntakeFile -CsvFile $file -Root $rootPath -UseReset $resetAvailable
        if ($resetAvailable) {
            $resetAvailable = $false
        }
    }

    if ($Once) {
        break
    }

    Start-Sleep -Seconds $PollSeconds
} while ($true)

if ($script:FailureCount -gt 0) {
    throw ("{0} intake file(s) encountered validator execution failures." -f $script:FailureCount)
}
