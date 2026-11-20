# Event B - Part 2: Realistic responses

Feature request (from our tracker): report how many distinct source files are modified when implementing an AI-generated feature (change spread).

## Response 1 - No structural change: count it by hand

Diff each run folder in event-a/runs/ against its matching original scenario folder and record files added/changed in a table.

Trade-off: quickest and needs no code, but it's manual, easy to get wrong and has to be redone for every new run.

## Response 2 - Extend the existing frozen script

Add a change-spread column to validate_frozen_replication.py, reusing its SCENARIOS / AI_RUNS / BASELINE_RUNS mappings so it diffs each run against its baseline.

Trade-off: repeatable, and reuses the mapping we already have instead of copying it, but it edits a frozen script. Our FROZEN_REPLICATION.md says a changed script must not be compared as the same frozen replication, so the original Event A output would have to be kept separately before rerunning.

## Response 3 - Separate small script

A new compare_change_spread.py that writes its own CSV and leaves the frozen package untouched.

Trade-off: keeps the frozen record safe, but the run-to-baseline mapping would be duplicated in two scripts (the same duplicated-code smell this project is about), unless the mapping is moved into one shared place.

## Response 4 - Full automated pipeline (scan + diff + metrics in one)

We already rejected this in Week 9 (column N) as too large for the scope.

Trade-off: most complete, but adds architecture the feature doesn't need.

## Smallest justified response

Response 3, with the run-to-baseline mapping moved into one shared module so it isn't duplicated. It answers the feature, keeps the frozen Event A record unchanged, and avoids copying code.
