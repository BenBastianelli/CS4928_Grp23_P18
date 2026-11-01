Event A vs M2: M2 reproduced the published validation-logic reuse effect (β = -1.77 against -1.79 published, all reproduction criteria met), meaning high technical debt lowered reuse of existing validation logic. Event A tested whether that direction appears when Copilot (Ask mode, Auto model, one run per variant) makes the same change to matched high-debt and low-debt code.

What carried over: The comparison of high-debt against low-debt code and the outcome, carry over unchanged. Where Copilot extended the existing class, it reused the calidation logic directly.

What did not carry over:
1. effect size: 4 runs can't fit the M2 model so only the direction of the effect can be compared and no estimate it comparable to beta.
2. debt level tooling: the high and low debt variants differ little in SonarQube terms. Baseline smells are 183 against 172 in booking and 205 against 201 in tickets and duplication is 0% in all four so that can't test the prediction.
3. smell counts: introduced smells were the same in total (+23/+26 in booking, +26/+23 in tickets, 49 against 49). part of that is a scanning artefact which is identical within each pair.
4. Participants: the model is a tool, not a human with project knowledge.