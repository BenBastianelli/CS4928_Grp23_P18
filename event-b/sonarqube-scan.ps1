$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($env:SONAR_TOKEN)) {
    throw "SONAR_TOKEN is not set in this PowerShell session."
}

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$scans = @(
    [PSCustomObject]@{
        Name = "booking-modernised-before"
        ProjectKey = "event-b-booking-modernised-before"
        SourcePath = Join-Path $PSScriptRoot "ai-runs\booking-modernised\input"
    },
    [PSCustomObject]@{
        Name = "booking-modernised-after"
        ProjectKey = "event-b-booking-modernised-after"
        SourcePath = Join-Path $PSScriptRoot "ai-runs\booking-modernised\output"
    },
    [PSCustomObject]@{
        Name = "tickets-modernised-before"
        ProjectKey = "event-b-tickets-modernised-before"
        SourcePath = Join-Path $PSScriptRoot "ai-runs\tickets-modernised\input"
    },
    [PSCustomObject]@{
        Name = "tickets-modernised-after"
        ProjectKey = "event-b-tickets-modernised-after"
        SourcePath = Join-Path $PSScriptRoot "ai-runs\tickets-modernised\output"
    }
)

foreach ($scan in $scans) {
    $sourcePath = (Resolve-Path $scan.SourcePath).Path
    Write-Host "`n--- $($scan.Name) ---"

    $outPath = Join-Path $sourcePath "out"
    if (Test-Path $outPath) {
        Remove-Item -LiteralPath $outPath -Recurse -Force
    }
    New-Item -ItemType Directory -Force $outPath | Out-Null

    $javaFiles = Get-ChildItem -LiteralPath $sourcePath -Filter "*.java" -File
    $javac = Join-Path $env:JAVA_HOME "bin\javac.exe"
    if (-not (Test-Path $javac)) {
        $javac = (Get-Command javac -ErrorAction SilentlyContinue).Source
    }

    $compiled = $false
    if ($javac) {
        & $javac -d $outPath ($javaFiles.FullName)
        $compiled = $LASTEXITCODE -eq 0
    }

    $scannerArguments = @(
        "run", "--rm",
        "-e", "SONAR_HOST_URL=http://host.docker.internal:9000",
        "-e", "SONAR_TOKEN=$env:SONAR_TOKEN",
        "-v", "${sourcePath}:/usr/src",
        "sonarsource/sonar-scanner-cli",
        "-Dsonar.projectKey=$($scan.ProjectKey)",
        "-Dsonar.sources=.",
        "-Dsonar.exclusions=out/**,.scannerwork/**"
    )

    if ($compiled) {
        $scannerArguments += "-Dsonar.java.binaries=out"
        Write-Host "Java compilation: PASS"
    }
    else {
        Write-Warning "Java compilation did not pass; scanning without sonar.java.binaries."
        Write-Warning "This is expected for modernised-before until the requested feature is added."
    }

    & docker $scannerArguments
    if ($LASTEXITCODE -ne 0) {
        throw "SonarQube scan failed for $($scan.Name)."
    }
}
