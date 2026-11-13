# Event B change-spread comparison

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

The generated results are stored in `event-b/change-spread.csv`. The
`build_validation` column confirms that each candidate snapshot compiles and
executes its package-qualified `Main` class.

The CSV also includes controlled Event B reproduction rows. Those rows compare
the modernised snapshots before and after adding the same extension-based
feature shape used in Event A. See `CONTROLLED_REPRODUCTION.md` for the
interpretation and limitation of that reproduction.

This is a change-spread comparison, not a new SonarQube scan. Existing Event A
smell and duplication results remain the saved evidence for Event A. The Event
B source changes are documented and can be scanned separately if a new
post-response smell count is required.

## Reproduce

From the repository root:

```powershell
python .\event-b\compare_change_spread.py
```
