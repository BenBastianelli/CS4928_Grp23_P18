# Event B modernised snapshots

These snapshots start from the original high-debt Booking and Tickets sources
in `D:\Projects\CS4928\Event_A_repo\Scenarios` and apply the smallest
modernisation justified in `event-a/DesignImplication.md`.

The changes are intentionally limited to:

- replacing single-letter names in `ClassRoom` and `TicketTypeSeasonal`;
- giving `ClassRoom` and `GroupRoom` value-based `equals()` and `hashCode()`
  implementations;
- preserving the existing interfaces, validation rules, and package layout.

The original high-debt sources and the Event A run folders are not modified.
These directories are the pre-Event-B modernised snapshots to which the
second feature request can be applied.
