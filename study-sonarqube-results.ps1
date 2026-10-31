$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($env:SONAR_TOKEN)) {
    throw "SONAR_TOKEN is not set in this PowerShell session."
}

$headers = @{
    Authorization = "Bearer $env:SONAR_TOKEN"
}

$projects = @(
    "PROJECT-TICKET-HTD-BASE",
    "PROJECT-TICKET-LTD-BASE",
    "PROJECT-BOOKING-HTD-BASE",
    "PROJECT-BOOKING-LTD-BASE"
)

$metrics = @(
    "ncloc",
    "code_smells",
    "violations",
    "sqale_index",
    "duplicated_lines",
    "duplicated_blocks",
    "duplicated_lines_density"
)

$metricKeys = [uri]::EscapeDataString(($metrics -join ","))

# Store all results in a directory named "study"
$outputDirectory = Join-Path (Get-Location) "study"

New-Item `
    -ItemType Directory `
    -Path $outputDirectory `
    -Force |
    Out-Null

$summary = @()

foreach ($project in $projects) {
    Write-Host "`n--- $project ---"

    $encodedProject = [uri]::EscapeDataString($project)

    $measuresUri =
        "http://localhost:9000/api/measures/component" +
        "?component=$encodedProject" +
        "&metricKeys=$metricKeys"

    $issuesUri =
        "http://localhost:9000/api/issues/search" +
        "?componentKeys=$encodedProject" +
        "&resolved=false" +
        "&ps=500"

    try {
        $measures = Invoke-RestMethod `
            -Uri $measuresUri `
            -Headers $headers `
            -ErrorAction Stop

        $issues = Invoke-RestMethod `
            -Uri $issuesUri `
            -Headers $headers `
            -ErrorAction Stop
    }
    catch {
        Write-Error "Failed to collect results for '$project': $($_.Exception.Message)"
        continue
    }

    $measureMap = @{}

    foreach ($measure in $measures.component.measures) {
        $measureMap[$measure.metric] = $measure.value
    }

    $record = [PSCustomObject][ordered]@{
        project_key              = $project
        collected_utc            = (Get-Date).ToUniversalTime().ToString("o")
        ncloc                    = $measureMap["ncloc"]
        code_smells              = $measureMap["code_smells"]
        violations               = $measureMap["violations"]
        sqale_index              = $measureMap["sqale_index"]
        duplicated_lines         = $measureMap["duplicated_lines"]
        duplicated_blocks        = $measureMap["duplicated_blocks"]
        duplicated_lines_density = $measureMap["duplicated_lines_density"]
        unresolved_issues        = $issues.total
    }

    $summary += $record

    $safeProjectName = $project -replace "[^A-Za-z0-9_.-]", "_"

    $measures |
        ConvertTo-Json -Depth 20 |
        Set-Content `
            -Path (Join-Path $outputDirectory "$safeProjectName-measures.json") `
            -Encoding UTF8

    $issues |
        ConvertTo-Json -Depth 30 |
        Set-Content `
            -Path (Join-Path $outputDirectory "$safeProjectName-issues.json") `
            -Encoding UTF8

    $issues.issues |
        Group-Object rule |
        Sort-Object Count -Descending |
        Select-Object Count, Name |
        Export-Csv `
            -Path (Join-Path $outputDirectory "$safeProjectName-issues-by-rule.csv") `
            -NoTypeInformation

    $issues.issues |
        Group-Object type, severity |
        Sort-Object Count -Descending |
        Select-Object Count, Name |
        Export-Csv `
            -Path (Join-Path $outputDirectory "$safeProjectName-issues-by-type-severity.csv") `
            -NoTypeInformation

    $record |
        Format-List
}

$summary |
    Export-Csv `
        -Path (Join-Path $outputDirectory "metrics-summary.csv") `
        -NoTypeInformation

Write-Host "`nResults saved to:"
Write-Host $outputDirectory