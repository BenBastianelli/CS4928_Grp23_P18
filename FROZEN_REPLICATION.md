# Frozen replication record

## Scope

This record freezes the four-scenario comparison of the baseline and AI-generated Java projects.
The source of truth is the saved SonarQube metrics and issue exports under `study/`.

## Frozen procedure

1. Match each baseline project to its corresponding AI project by scenario and debt level.
2. Use SonarQube `code_smells` as the code-smell measure.
3. Use SonarQube `duplicated_blocks` as the logic-reuse proxy. A value of zero means no duplicated blocks were reported; it does not prove semantic equivalence.
4. Count naming issues only when the SonarQube rule or issue message explicitly identifies naming, a class name, method name, or variable name.
5. Compile each baseline and AI source snapshot with `javac`, then execute its package-qualified `Main` class.

## Results

| Scenario | Baseline smells | AI smells | Net smells | Baseline duplicated blocks | AI duplicated blocks | Baseline naming issues | AI naming issues | Baseline validation | AI validation |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| Booking High TD | 183 | 206 | +23 | 0 | 0 | 0 | 0 | PASS | PASS |
| Booking Low TD | 172 | 198 | +26 | 0 | 0 | 0 | 0 | PASS | PASS |
| Tickets High TD | 205 | 231 | +26 | 0 | 0 | 0 | 0 | PASS | PASS |
| Tickets Low TD | 201 | 224 | +23 | 0 | 0 | 0 | 0 | PASS | PASS |

Total code smells: baseline **761**, AI-generated **859**, net **+98**.
AI static validation: **4/4** scenarios passed compilation and execution.

## Limitations

- Baseline source was validated from the external Scenarios repository supplied for this task. Booking runtime validation is affected by the source fixture's hard-coded 2021 dates; the result is recorded separately from compilation.
- The saved baseline and AI SonarQube exports report zero duplicated blocks for every scenario. This supports a zero structural-duplication result under this metric, not a proof that no logic was conceptually reused.
- The naming count is zero where no issue explicitly matches the frozen naming terms. General code smells such as magic numbers are not silently reclassified as naming issues.
- SonarQube project keys, timestamps, quality profile, and metric exports should remain unchanged for this record to be reproducible.

## Output artifacts

- `study/AI-Results/analysis/frozen-replication-validation.csv`
- `study/AI-Results/analysis/frozen-replication-validation.png`
- `FROZEN_REPLICATION.md`

## Reproduction setup

The following instructions describe the external tools and commands needed to
repeat the SonarQube and Java validation. The commands below assume Windows
PowerShell and the repository root as the current directory.

### Required tools

Install the following tools before starting:

1. **Git** for obtaining the repository and the source scenarios.
2. **Docker Desktop** with Linux containers enabled. The SonarQube scanner is
   run through Docker.
3. **SonarQube Server**, available at
   `http://localhost:9000`. The server may be run locally or through Docker.
4. **Java JDK 21 or another JDK compatible with the source files**. Both
   `java.exe` and `javac.exe` are required. Set `JAVA_HOME` to the JDK
   directory, for example:

   ```powershell
   $env:JAVA_HOME = "C:\Program Files\Java\jdk-21"
   $env:Path = "$env:JAVA_HOME\bin;$env:Path"
   java -version
   javac -version
   ```

5. **Python 3.10 or newer**, with the plotting dependency:

   ```powershell
   python -m pip install matplotlib
   ```

### SonarQube server setup

Start SonarQube and wait until `http://localhost:9000` opens successfully in a
browser. Log in to SonarQube and create a token for the account that will
collect the results. Keep the token private and set it only for the current
PowerShell session:

```powershell
$env:SONAR_TOKEN = "paste-your-token-here"
```

The scanner scripts expect the SonarQube server to be reachable at
`http://localhost:9000`. The Docker scanner uses
`host.docker.internal:9000` so that the container can reach a SonarQube server
running on the Windows host.

### Create the SonarQube projects

Create these eight SonarQube projects before scanning:

```text
PROJECT-BASELINE-TICKET-HTD
PROJECT-BASELINE-TICKET-LTD
PROJECT-BASELINE-BOOKING-HTD
PROJECT-BASELINE-BOOKING-LTD
run1-GPT5.6Luna-booking-htd
run2-GPT5.6Luna-booking-ltd
run3-GPT5.6Luna-tickets-htd
run4-GPT5.6Luna-tickets-ltd
```

The project keys must match exactly. The result-collection scripts use these
keys when calling the SonarQube API.

### Create the sonarqube rules
On the top of your sonarqube local host click the Quality Profile button.
- From this screen create a new Quality Profile
- Name it whatever and select Java as the language.
- Once created scroll to the bottom of the new page and click 'activate more'
- On this page click the 'Bulk change' drop down toggle and select "activate in NAME"
- Return to the quality profile page
- Search Java in the 'Filter by' drop down combo box
- click the three dotted lines next to the newly created quality profile
- Select set as Default.

### Scan the baseline scenarios

The baseline source repository must be available as a sibling directory or at
the path configured in the validation script:

```text
D:\Projects\CS4928\Event_A_repo\Scenarios
```

For each baseline scenario, copy the corresponding Java source files into a
temporary scan directory. Include the shared solution file required by the
scenario:

| Project key | Source directory | Additional source |
|---|---|---|
| `PROJECT-BASELINE-BOOKING-HTD` | `Scenarios\booking\high_debt\booking` | `Scenarios\booking\ComputerClassRoom.java` |
| `PROJECT-BASELINE-BOOKING-LTD` | `Scenarios\booking\low_debt\booking` | `Scenarios\booking\ComputerClassRoom.java` |
| `PROJECT-BASELINE-TICKET-HTD` | `Scenarios\tickets\high_debt\tickets` | `Scenarios\tickets\TicketTypeSeasonalRestricted.java` |
| `PROJECT-BASELINE-TICKET-LTD` | `Scenarios\tickets\low_debt\tickets` | `Scenarios\tickets\TicketTypeSeasonalRestricted.java` |

Compile each scenario before scanning:

```powershell
javac *.java
```

Run the scanner from the directory containing the scenario source. Set the
project key in `event-a\sonarQubescan.ps1` to the project being scanned, then
run:

```powershell
.\event-a\sonarQubescan.ps1
```

The scanner uses the Docker image
`sonarsource/sonar-scanner-cli` and excludes compiled output and
`.scannerwork`. Repeat the scan for all four baseline projects.

### Scan the AI scenarios

The AI source snapshots are stored in:

```text
event-a\runs\run1_booking_high_29-10-2026_1800
event-a\runs\run2_booking_low_29-10-2026_1900
event-a\runs\run3_tickets_high_29-10-2026_1915
event-a\runs\run4_tickets_low_29-10-2026_1950
```

Compile each directory and then scan it with the matching project key:

```powershell
Get-ChildItem .\event-a\runs -Directory |
    Where-Object { $_.Name -like "run*" } |
    ForEach-Object {
        Push-Location $_.FullName
        try {
            javac *.java
        }
        finally {
            Pop-Location
        }
    }
```

Use the following project-key mapping when running the scanner:

| Source directory | SonarQube project key |
|---|---|
| `run1_booking_high_29-10-2026_1800` | `run1-GPT5.6Luna-booking-htd` |
| `run2_booking_low_29-10-2026_1900` | `run2-GPT5.6Luna-booking-ltd` |
| `run3_tickets_high_29-10-2026_1915` | `run3-GPT5.6Luna-tickets-htd` |
| `run4_tickets_low_29-10-2026_1950` | `run4-GPT5.6Luna-tickets-ltd` |

After all four AI scans finish, collect their SonarQube results:

```powershell
.\ai-results-sonarqube.ps1
```

This creates `study\AI-Results` with the metrics, issue JSON, rule summaries,
and type/severity summaries.

Collect the baseline results with:

```powershell
.\study-sonarqube-results.ps1
```

This creates `study\Baseline` with the corresponding baseline exports.

### Generate the frozen comparison

From the repository root, run:

```powershell
python .\validate_frozen_replication.py
```

The script:

- matches each baseline project to its AI counterpart;
- reads `code_smells`, `duplicated_blocks`, and issue exports;
- counts explicit naming-rule matches;
- compiles and executes all baseline and AI `Main` classes;
- writes the final comparison CSV and graph.

The expected outputs are:

```text
study\AI-Results\analysis\frozen-replication-validation.csv
study\AI-Results\analysis\frozen-replication-validation.png
```

### Reproduction checks

A successful reproduction should show:

- `PASS` for baseline and AI static validation in every scenario;
- `0` duplicated blocks for all eight SonarQube projects;
- `0` explicit naming issues for all eight projects;
- baseline code smells totaling `761`;
- AI code smells totaling `859`;
- a net increase of `98` AI code smells.

If any project key, source snapshot, SonarQube quality profile, metric export,
or tool version changes, record that change and do not compare the new output
as an identical frozen replication.
