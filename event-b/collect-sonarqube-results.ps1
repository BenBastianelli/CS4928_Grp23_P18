$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($env:SONAR_TOKEN)) {
    throw "SONAR_TOKEN is not set in this PowerShell session."
}

$metrics = @(
    "code_smells",
    "duplicated_blocks",
    "duplicated_lines",
    "duplicated_lines_density"
)

$projects = @(
    "event-b-booking-modernised-before",
    "event-b-booking-modernised-after",
    "event-b-tickets-modernised-before",
    "event-b-tickets-modernised-after"
)

$encodedToken = [Convert]::ToBase64String(
    [Text.Encoding]::ASCII.GetBytes("$($env:SONAR_TOKEN):")
)
$headers = @{ Authorization = "Basic $encodedToken" }
$metricKeys = [uri]::EscapeDataString(($metrics -join ","))
$records = @()

foreach ($project in $projects) {
    $component = [uri]::EscapeDataString($project)
    $uri = "http://localhost:9000/api/measures/component?component=$component&metricKeys=$metricKeys"
    $response = Invoke-RestMethod -Uri $uri -Headers $headers
    $values = @{}

    foreach ($measure in $response.component.measures) {
        $values[$measure.metric] = [double]$measure.value
    }

    $records += [PSCustomObject][ordered]@{
        project_key = $project
        code_smells = $values["code_smells"]
        duplicated_blocks = $values["duplicated_blocks"]
        duplicated_lines = $values["duplicated_lines"]
        duplicated_lines_density = $values["duplicated_lines_density"]
    }
}

$output = Join-Path $PSScriptRoot "sonarqube-results.csv"
$records | Export-Csv -Path $output -NoTypeInformation

$pairs = @(
    @{ name = "Booking"; before = "event-b-booking-modernised-before"; after = "event-b-booking-modernised-after" },
    @{ name = "Tickets"; before = "event-b-tickets-modernised-before"; after = "event-b-tickets-modernised-after" }
)

$deltas = foreach ($pair in $pairs) {
    $before = $records | Where-Object project_key -eq $pair.before
    $after = $records | Where-Object project_key -eq $pair.after
    [PSCustomObject][ordered]@{
        scenario = $pair.name
        code_smells_before = $before.code_smells
        code_smells_after = $after.code_smells
        new_code_smells = $after.code_smells - $before.code_smells
        duplicated_blocks_before = $before.duplicated_blocks
        duplicated_blocks_after = $after.duplicated_blocks
        new_duplicated_blocks = $after.duplicated_blocks - $before.duplicated_blocks
        duplicated_lines_before = $before.duplicated_lines
        duplicated_lines_after = $after.duplicated_lines
        new_duplicated_lines = $after.duplicated_lines - $before.duplicated_lines
        duplicated_density_before = $before.duplicated_lines_density
        duplicated_density_after = $after.duplicated_lines_density
        duplicated_density_delta = $after.duplicated_lines_density - $before.duplicated_lines_density
    }
}

$deltaOutput = Join-Path $PSScriptRoot "sonarqube-deltas.csv"
$deltas | Export-Csv -Path $deltaOutput -NoTypeInformation

Write-Host "Raw metrics: $output"
Write-Host "Before/after deltas: $deltaOutput"
$deltas | Format-Table -AutoSize
