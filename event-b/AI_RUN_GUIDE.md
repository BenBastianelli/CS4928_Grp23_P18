# Event B clean AI runs

This guide prepares two clean Event B runs using the same task files and
workflow used in Event A, but starting from the M4-modernised parents.

## Run folders

- `event-b/ai-runs/booking-modernised/input/`
- `event-b/ai-runs/tickets-modernised/input/`

The `input` folders contain the modernised sources before the Event A feature
is added. The `output` folders are empty and are reserved for the files
produced or copied after each Copilot run.

The original task files are available beside the inputs:

- `event-b/ai-runs/booking-modernised/instructions.md`
- `event-b/ai-runs/tickets-modernised/instructions.md`

Do not edit the Event A run folders or
`event-b/modernised-snapshots/`.

## Fixed workflow

Use the same workflow as Event A:

1. Open one run folder (`booking-modernised` or `tickets-modernised`) as a
   separate VS Code workspace.
2. Copy every `.java` file from its `input` folder into its `output` folder.
   The `input` folder is the untouched pre-run baseline; Copilot works against
   the copied source set in `output`.
3. Use Copilot in Ask mode.
4. Use the same model setting available during Event A. If it is `Auto`, record
   that it is still `Auto`.
5. Open the matching `instructions.md` and submit its task text as the prompt.
   Do not use the shortened prompts from an earlier version of this guide.
6. Save the complete resulting Java source set in the matching `output` folder.
7. Record the date, VS Code version, Copilot mode, model setting, prompt,
   response, and whether compilation succeeded in a run-notes file.

Do not include the existing Event A feature class in the input. The Booking
input intentionally has no `ComputerClassRoom.java`, and the Tickets input
intentionally has no `TicketTypeSeasonalRestricted.java`.

The original task wording is intentionally preserved, including its spelling
and phrasing, so the Event B run can be compared with Event A without silently
changing the prompt.

## Build checks

From the repository root, compile each completed output folder. Set
`JAVA_HOME` to a JDK containing `javac.exe` and `java.exe`.

```powershell
$out = Join-Path $env:TEMP "event-b-booking-ai"
New-Item -ItemType Directory -Force $out | Out-Null
javac -d $out .\event-b\ai-runs\booking-modernised\output\*.java
java -cp $out booking.Main
```

```powershell
$out = Join-Path $env:TEMP "event-b-tickets-ai"
New-Item -ItemType Directory -Force $out | Out-Null
javac -d $out .\event-b\ai-runs\tickets-modernised\output\*.java
java -cp $out tickets.Main
```

Record compilation and runtime results even if the existing fixture prints
warnings. The original Booking fixture contains hard-coded 2021 dates, so
date-related output may be expected.

## Comparison

After both runs are complete:

1. Copy the completed Java files into the corresponding `output` folder.
2. Record the AI response and implementation notes.
3. Compare each output against its matching modernised input:
   - files added;
   - files modified;
   - files removed;
   - reuse through `super`;
   - build result;
   - new smells and duplication, if SonarQube is run.
4. Compare those results descriptively with the Event A rows in
   `event-b/change-spread.csv`.

Do not combine the Event A and Event B runs into a statistical sample. They are
matched, descriptive case comparisons.

## SonarQube scans

Start SonarQube at `http://localhost:9000`, create four projects with these
exact keys, and set a token for the current PowerShell session:

```powershell
$env:SONAR_TOKEN = "your-token"
```

```text
event-b-booking-modernised-before
event-b-booking-modernised-after
event-b-tickets-modernised-before
event-b-tickets-modernised-after
```

From the repository root, run:

```powershell
.\event-b\sonarqube-scan.ps1
```

The script uses the same Docker scanner approach as Event A. It compiles each
folder into an excluded `out` directory before scanning when possible. The
modernised-before fixtures still reference the feature class that has not yet
been added, so those two scans may report a compile warning and run without
`sonar.java.binaries`; record that limitation with the results.

After each scan finishes, collect `code_smells`, `duplicated_blocks`, and
`duplicated_lines_density` from SonarQube. Compare after minus before for each
system. Keep the token private and do not commit it.
