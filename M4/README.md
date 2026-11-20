# M4 change-spread comparison

## Feature request

Report how many distinct Java source files are modified when implementing an
AI-generated feature.

## Comparison

This comparison uses the original high-debt snapshots as the common baseline:

- Event A: the existing high-debt AI-generated run;
- Event B: the isolated modernised snapshot created from the same high-debt
  source and the design improvement recorded in
  `event-a/DesignImplication.md`.

The comparison counts a file as changed when it is added, removed, or has
different content. Non-source files are excluded. The shared fixture files
`ComputerClassRoom.java` and `TicketTypeSeasonalRestricted.java` are included
in the baseline because the original scenario layout stores them one directory
above the variant-specific source directories.

## Results

The generated results are stored in `M4/change-spread.csv`. The
`build_validation` column confirms that each candidate snapshot compiles and
executes its package-qualified `Main` class.

The CSV also includes controlled Event B reproduction rows. Those rows compare
the modernised snapshots before and after adding the same extension-based
feature shape used in Event A. See `event-b/CONTROLLED_REPRODUCTION.md` for the
interpretation and limitation of that reproduction.

This is a change-spread comparison, not a new SonarQube scan. Existing Event A
smell and duplication results remain the saved evidence for Event A. The Event
B source changes are documented and can be scanned separately if a new
post-response smell count is required.

## Reproduce

Use the integrated checkout containing Event B for the full comparison.
Install Python 3.10 or later and a JDK with `java` and `javac` available
through `JAVA_HOME` or `PATH`.

Use the original Event A `Scenarios` folder. It should contain
`booking/high_debt/booking/`, `tickets/high_debt/tickets/`,
`booking/ComputerClassRoom.java`, and
`tickets/TicketTypeSeasonalRestricted.java`. The script looks for
`../Event_A_repo/Scenarios` relative to the repository root by default.

The script uses the high-debt Booking and Tickets runs under
`event-a/runs/` and the Java snapshots in these Event B directories:

- `event-b/modernised-snapshots/`
- `event-b/controlled-reproduction/modernised-before/`
- `event-b/controlled-reproduction/modernised-after/`

From the repository root in PowerShell, set the baseline path if your
`Scenarios` folder is elsewhere, then run the tool:

```powershell
$env:CS4928_SCENARIOS_DIR = 'C:\path\to\Scenarios'
python .\M4\compare_change_spread.py
```

Omit the environment variable assignment if you use the default layout.
The script writes `M4/change-spread.csv`. For the full comparison, expect
six rows with `PASS` in `build_validation`. The saved reference CSV is
`event-b/change-spread.csv` in the Event B snapshot.
