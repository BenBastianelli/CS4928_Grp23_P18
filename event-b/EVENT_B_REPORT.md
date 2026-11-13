# Event B report

## 1. Purpose

Event B applies the same feature request used in Event A to an explicitly
modernised version of the high-debt systems. The comparison asks whether the
modernisation changes:

- change spread;
- newly reported code smells;
- duplication;
- reuse of existing logic;
- build and runtime behavior.

The Event B feature request is the original scenario task:

- Booking: add `ComputerClassRoom`;
- Tickets: add `TicketTypeSeasonalRestricted`.

The original task instructions were copied unchanged from the source
repository into the Event B run folders:

- `ai-runs/booking-modernised/instructions.md`;
- `ai-runs/tickets-modernised/instructions.md`.

## 2. Starting point and modernisation

The Event A design implication identified poor names and equality risks in the
high-debt code. The smallest justified modernisation was applied to isolated
copies of the original high-debt Booking and Tickets sources.

### Booking

- renamed unclear fields and parameters in `ClassRoom`;
- renamed unclear fields and parameters in `GroupRoom`;
- changed `ClassRoom.equals()` and `ClassRoom.hashCode()` to use room identity
  data and projector state;
- changed `GroupRoom.equals()` and `GroupRoom.hashCode()` to use room identity
  data and whiteboard state.

### Tickets

- renamed unclear fields and parameters in `TicketTypeSeasonal`;
- preserved its existing public API and validation behavior.

No new superclass, decorator, or other architecture was introduced. The
original Event A runs, original high-debt sources, and frozen replication
files were not modified.

The isolated modernised snapshots are in
`event-b/modernised-snapshots/`.

## 3. Fresh Event B AI runs

Clean run inputs were created in:

- `event-b/ai-runs/booking-modernised/input/`;
- `event-b/ai-runs/tickets-modernised/input/`.

The input folders intentionally exclude the feature being requested. The
completed AI outputs are in:

- `event-b/ai-runs/booking-modernised/output/`;
- `event-b/ai-runs/tickets-modernised/output/`.

The run followed the Event A workflow as closely as possible:

- VS Code;
- Copilot Ask mode;
- the original task instruction file;
- a separate output copy so the before-state remained unchanged.

The historical Event A notes recorded VS Code 1.144.0, Copilot Ask mode, and
an Auto model setting. The exact Event B client metadata should be retained in
the run notes if it differs.

## 4. Build and runtime verification

Both Event B output folders compiled and their package-qualified `Main` classes
ran successfully:

| System | Compilation | Runtime |
|---|---|---|
| Booking | PASS | PASS, exit code 0 |
| Tickets | PASS | PASS, exit code 0 |

The Booking fixture printed warnings associated with hard-coded 2021 test
dates. Those warnings are inherited from the fixture and were not silently
changed as part of this experiment.

## 5. Change spread

The comparison script is
`event-b/compare_change_spread.py`, and its output is
`event-b/change-spread.csv`.

The fresh AI outputs changed one source file relative to the modernised
inputs:

| System | Files before | Files after | Added | Removed | Modified | Build |
|---|---:|---:|---:|---:|---:|---|
| Booking | 7 | 8 | 1 | 0 | 0 | PASS |
| Tickets | 10 | 11 | 1 | 0 | 0 | PASS |

The requested feature therefore remained local to one new source file in both
fresh Event B runs.

For context, the Event A high-debt runs also added one feature file per
scenario. This is a descriptive matched comparison, not a statistically
meaningful increase in sample size.

## 6. Reuse decisions

Reuse was evaluated by inspecting whether the new feature delegated existing
validation through the parent implementation. Inheritance alone was not
counted as reuse.

### Booking

`ComputerClassRoom.book(...)` checks its additional opening-hours rule and
then calls:

```java
super.book(interval, user)
```

Decision: **reuse confirmed**. Existing classroom booking and availability
validation was delegated to `ClassRoom`.

### Tickets

`TicketTypeSeasonalRestricted` implements `TicketType` directly. Its
`isValidFor(...)` method independently checks valid zones and the season
instead of extending `TicketTypeSeasonal` and calling
`super.isValidFor(...)`.

Decision: **reuse not confirmed**. The fresh AI implementation reimplemented
the existing seasonal and zone validation.

## 7. SonarQube results

The scans used four separate projects:

- `event-b-booking-modernised-before`;
- `event-b-booking-modernised-after`;
- `event-b-tickets-modernised-before`;
- `event-b-tickets-modernised-after`.

All four scanner executions completed successfully. Raw values are in
`event-b/sonarqube-results.csv`; calculated deltas are in
`event-b/sonarqube-deltas.csv`.

| System | Smells before | Smells after | New smells | Duplicated blocks before | Duplicated blocks after | New duplicated blocks |
|---|---:|---:|---:|---:|---:|---:|
| Booking | 198 | 213 | +15 | 0 | 0 | 0 |
| Tickets | 215 | 244 | +29 | 0 | 0 | 0 |

Duplicated lines and duplicated-lines density were zero before and after for
both systems.

The scans used the existing Event A Docker scanner approach. The before
folders could not compile independently because their original `Main.java`
files refer to the feature classes that are intentionally absent from those
pre-feature folders. Those scans therefore ran without
`sonar.java.binaries`, and SonarQube reported unresolved types and reduced
Java-analysis precision. The before smell counts must therefore be described
as source-level baseline measurements with this limitation.

## 8. Conclusion

The Week 9 modernisation is **partly supported** for this feature.

The positive evidence is:

- both features remained local to one added source file;
- both output projects compiled and ran;
- Booking reused the existing classroom validation through `super.book(...)`;
- SonarQube detected no duplicated blocks or duplicated lines.

The negative evidence is:

- Booking introduced 15 additional SonarQube code smells;
- Tickets introduced 29 additional SonarQube code smells;
- the Tickets implementation did not reuse `TicketTypeSeasonal` validation and
  instead duplicated the season and zone checks.

The result does not support a claim that modernisation automatically makes AI
implementations cleaner. It does support a narrower claim: the modernised
Booking design preserved the intended extension and reuse path for this
feature. The Tickets result shows that an AI assistant can still bypass an
available abstraction and reimplement logic, even after modernisation.

## 9. Trade-off and remaining risk

The chosen modernisation avoided a larger superclass extraction or design
pattern, keeping the change small and preserving the frozen Event A record.
The trade-off is that duplicated validation remains in the high-debt-derived
structure, and the AI may still ignore the intended parent abstraction, as
shown by the Tickets result.

The main remaining risk is therefore not only structural duplication detected
by SonarQube. It is also behavioral duplication and inconsistent reuse that
requires source inspection.

## 10. Reproduction commands

From the repository root:

```powershell
python .\event-b\compare_change_spread.py
```

After starting SonarQube at `http://localhost:9000` and setting a private
token in the current PowerShell session:

```powershell
.\event-b\sonarqube-scan.ps1
.\event-b\collect-sonarqube-results.ps1
```

The token must not be committed or included in the report.

## 11. Evidence

- `event-a/DesignImplication.md`;
- `event-a/runs/run1_notes.txt`;
- `event-a/runs/run3_notes.txt`;
- `event-b/modernised-snapshots/`;
- `event-b/ai-runs/`;
- `event-b/change-spread.csv`;
- `event-b/sonarqube-results.csv`;
- `event-b/sonarqube-deltas.csv`;
- `event-b/compare_change_spread.py`;
- `event-b/sonarqube-scan.ps1`;
- `event-b/collect-sonarqube-results.ps1`.
