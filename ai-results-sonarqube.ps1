$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($env:SONAR_TOKEN)) {
    throw "SONAR_TOKEN is not set in this PowerShell session."
}

$headers = @{
    Authorization = "Bearer $env:SONAR_TOKEN"
}

$projects = @(
    [PSCustomObject]@{
        ProjectKey = "run1-GPT5.6Luna-booking-htd"
        OutputPath = @("AI-Results-Booking", "High_TD")
    },
    [PSCustomObject]@{
        ProjectKey = "run2-GPT5.6Luna-booking-ltd"
        OutputPath = @("AI-Results-Booking", "Low_TD")
    },
    [PSCustomObject]@{
        ProjectKey = "run3-GPT5.6Luna-tickets-htd"
        OutputPath = @("AI-Results-Tickets", "High-TD")
    },
    [PSCustomObject]@{
        ProjectKey = "run4-GPT5.6Luna-tickets-ltd"
        OutputPath = @("AI-Results-Tickets", "Low-TD")
    }
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
$outputDirectory = Join-Path (Get-Location) "AI-Results"

New-Item `
    -ItemType Directory `
    -Path $outputDirectory `
    -Force |
    Out-Null

$summary = @()

foreach ($project in $projects) {
    $projectKey = $project.ProjectKey
    $projectOutputDirectory = $outputDirectory

    foreach ($directoryName in $project.OutputPath) {
        $projectOutputDirectory = Join-Path $projectOutputDirectory $directoryName
    }

    New-Item `
        -ItemType Directory `
        -Path $projectOutputDirectory `
        -Force |
        Out-Null

    Write-Host "`n--- $projectKey ---"

    $encodedProject = [uri]::EscapeDataString($projectKey)

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
        Write-Error "Failed to collect results for '$projectKey': $($_.Exception.Message)"
        continue
    }

    $measureMap = @{}

    foreach ($measure in $measures.component.measures) {
        $measureMap[$measure.metric] = $measure.value
    }

    $record = [PSCustomObject][ordered]@{
        project_key              = $projectKey
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

    $safeProjectName = $projectKey -replace "[^A-Za-z0-9_.-]", "_"

    $measures |
        ConvertTo-Json -Depth 20 |
        Set-Content `
            -Path (Join-Path $projectOutputDirectory "$safeProjectName-measures.json") `
            -Encoding UTF8

    $issues |
        ConvertTo-Json -Depth 30 |
        Set-Content `
            -Path (Join-Path $projectOutputDirectory "$safeProjectName-issues.json") `
            -Encoding UTF8

    $issues.issues |
        Group-Object rule |
        Sort-Object Count -Descending |
        Select-Object Count, Name |
        Export-Csv `
            -Path (Join-Path $projectOutputDirectory "$safeProjectName-issues-by-rule.csv") `
            -NoTypeInformation

    $issues.issues |
        Group-Object type, severity |
        Sort-Object Count -Descending |
        Select-Object Count, Name |
        Export-Csv `
            -Path (Join-Path $projectOutputDirectory "$safeProjectName-issues-by-type-severity.csv") `
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
