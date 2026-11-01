# Event A - Part 4: Design / maintainability implication

Written by Dara. Based on the four Copilot runs in `event-a/runs/` (29/10/2026), Amy's comparison in `event-a/ResultComparison.md` and the SonarQube results in `study/`. Scenario code is BWTSE/Scenarios tag persist1.3 (commit 512c24d).

## 1. How the high and low debt versions differ

In the low debt versions there's a base class (`Room` / `TicketType`) that holds the shared fields and the validation. Each subclass adds its own rule and then calls `super.book(...)` or `super.isValidFor(...)`, so every rule only exists once and the names are normal words.

In the high debt versions `Room` and `TicketType` are just interfaces, so each class has its own copy of the fields, getters and validation helpers. For example `available()` and `startBeforeEnd()` are in both `ClassRoom` and `GroupRoom`. Names are single letters like `n`, `d`, `p`, `bs`, `zs`. So the two smells are duplicated code and bad naming.

One thing worth noting is that reuse is still possible in the high debt version. The class the task builds on (`ClassRoom` for booking, `TicketTypeSeasonal` for tickets) is a normal public class in both versions, so you can extend it and call `super` either way. The only difference is the example the rest of the code sets.

## 2. What the AI did

I went through the new class from each run and used the same reuse rule as M2 (paper p.10, "any type of reuse qualified").

| Run | Variant | Reused validation logic? | Names | equals / hashCode |
|---|---|---|---|---|
| run1 | booking, high debt | yes, extends ClassRoom + super.book | used `n, d, p` and `i, u` like ClassRoom | not added |
| run2 | booking, low debt | yes, extends ClassRoom + super.book | normal names | added, same style as existing classes |
| run3 | tickets, high debt | yes, extends TicketTypeSeasonal + super.isValidFor | normal names | added, same getClass() style as the high debt classes |
| run4 | tickets, low debt | yes, extends TicketTypeSeasonal + super.isValidFor | normal names | added, same style as existing classes |

So the AI duplicated the validation logic in 0 of the 2 high debt runs and 0 of the 2 low debt runs. For comparison, in M2 the humans duplicated it in 50% of high debt and 11% of low debt submissions. None of the runs changed any existing files, they only added the new class.

What it did copy was the style of whatever class it was extending. In run1 that was the single letter names, and in runs 2-4 it matched how `equals()` was already written. It never copied the duplicated structure though.

Also, SonarQube says there are 0 duplicated blocks in all eight projects, even the original high debt ones where the duplication was put in on purpose. So SonarQube's duplication measure can't pick up this kind of duplication. The paper's authors had the same problem and checked it by hand instead (p.11), which is why I judged reuse by reading the code.

## 3. Implication

The broken windows effect from M2 didn't show up in how the AI structured its code. It found the reuse route every time because there was an obvious class to extend in both versions, and the duplicated code in other classes like `GroupRoom` didn't seem to affect it.

What did carry over was debt in the class being extended. In run1 the AI copied `ClassRoom`'s single letter names, and because it didn't add an `equals()` the new class just inherits the high debt `ClassRoom.equals()`. That one calls `Object.equals`, so it compares by identity instead of by name like the low debt version does. So the debt spread through inheritance and copying the parent class, not through duplication.

Based on that, I think the maintainability risk when using AI to extend this code is mostly in the class that gets extended. The smallest change that the evidence supports is:
- rename the single letter fields and parameters in `ClassRoom` and `TicketTypeSeasonal` to proper names
- fix `equals()` / `hashCode()` in the high debt `ClassRoom` and `GroupRoom` so they compare by value like the low debt version

Both are small changes in one or two classes, and the existing tests in `Main.java` can be used to check nothing broke.

This ties into a few things from the module. The new behaviour was added by extending rather than editing existing code (open/closed), but that only works well if the parent class is clean. A subclass also inherits its parent's `equals()` behaviour, bugs and all, so the parent's contract matters (Liskov). And in terms of code smells, the bad naming spread but the duplicated code didn't.

## 4. Other options we looked at

- Refactoring the whole high debt version into the low debt structure (Extract Superclass, Pull Up Method). We didn't go with this because the AI didn't add any duplication, so Event A doesn't show this would change anything. It might still be worth doing for people reading the code, but that's a different argument.
- Using the Decorator pattern for the extra restrictions (opening hours, occupations). Each scenario only adds one restriction, so there's nothing to combine, and extending the class with `super` already does it in a few lines. The brief says not to add a pattern unless there's a reason for it, and there isn't one here.
- Changing nothing. That's possible, but run1 shows bad names and the broken `equals()` getting carried into new code, so a small fix seems justified.

## 5. Limitations

- There were only 4 runs, one per variant, so this only shows a direction and a different run could easily go another way. The naming result is only 1 out of 2 high debt runs.
- The run notes say Copilot's model was on "auto" because we couldn't pick a specific model on our plan, but the SonarQube project names say "GPT5.6Luna". We need to confirm which model was used, and on auto it might not have been the same one each time.
- Copilot was in Ask mode, so it suggested the code and one of us copied it in. The exact prompt text isn't saved in the repo, only the `instructions.md` files that were used.
- The authors' example solutions have been on GitHub since 2021, and all four AI answers follow the same approach (extends + super). So the model might just remember them rather than be reacting to the code it was given.

## 6. Evidence

- AI runs: `event-a/runs/run1_booking_high_29-10-2026_1800`, `run2_booking_low_29-10-2026_1900`, `run3_tickets_high_29-10-2026_1915`, `run4_tickets_low_29-10-2026_1950` and the `run1-4_notes.txt` files
- SonarQube results: `study/AI-Results/`, `study/Baseline/`, `FROZEN_REPLICATION.md`
- Comparison with M2: `event-a/ResultComparison.md`
- M2 human numbers: data.csv from BWTSE/Data v1.4, completed submissions only (51 rows)
