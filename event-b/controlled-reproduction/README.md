# Controlled Event B reproduction

This directory reproduces the shape of the Event A AI experiment against the
modernised snapshots.

The controlled feature is the same feature used in Event A:

- Booking: add `ComputerClassRoom` by extending `ClassRoom` and delegating
  existing booking validation to `super.book(...)`.
- Tickets: add `TicketTypeSeasonalRestricted` by extending
  `TicketTypeSeasonal` and delegating existing season and zone validation to
  `super.isValidFor(...)`.

The feature classes are adapted only to the descriptive names and value-based
equality contracts of the modernised parents. They are not a new Copilot
interaction; the repository does not provide a way to invoke the historical
VS Code Copilot session reproducibly from this script.

## Snapshots

- `modernised-before/` contains the modernised parents without the controlled
  feature class.
- `modernised-after/` contains the same parents plus the reproduced feature.

The comparison therefore measures the change spread caused by the same feature
shape after modernisation. The generated `event-b/change-spread.csv` includes
these controlled-reproduction rows.
