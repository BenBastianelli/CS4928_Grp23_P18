# Audit - RQ1 bounded reproduction (G23 / P18)

Paper: Leven et al. (2024), "The broken windows theory applies to technical debt", Empirical Software Engineering 29:73. https://link.springer.com/article/10.1007/s10664-024-10456-6 <br>
Data: BWTSE/Data v1.4 (commit 84b05cd8300241ab836a896d17579a38b18796e8) <br>
Analysis: BWTSE/Analysis v1.6 (commit d8332c64550e427d79cba4713ba8146dbd5cfb44) <br>
Our run: `runModel1.R` and `RUN.md` on the `m2repro` branch (commit 1dff6e4)

This file covers what changed from our Week 5 frozen plan, any wrong assumptions we made, problems with the authors' artefact (old versions, broken links etc.) and how much we trust the paper's result and our own reproduction. The frozen plan itself hasn't been edited. Anything that changed is explained here instead.

Anything still marked TODO is not done yet. Page numbers refer to the published PDF.

## 1. Frozen plan (Week 5)

Copied from our row in the Student Tracker (RQs and Milestones, G23):

- **RQ1:** Can one broken-windows effect be reproduced from the study data?
- **Sample:** All submissions in data.csv from BWTSE/Data v1.4 (paper: 51 from 29 participants), unit = one submission, no sampling and no added exclusions, analysed with Analysis v1.6.
- **Method / rule:** Refit the authors' Model 1 (validation-logic reuse ~ high_debt_version + programming_experience + (1 | participant)) with brms 2.15.1 and the Rmd's priors, using a fixed seed. Reproduced if R-hat <= 1.01, no divergences, and the high_debt_version:false beta is negative with a 95% CrI that excludes zero and a mean inside the paper's [-3.12, -0.54].
- **Expected:** beta ~ -1.8 (CrI ~ [-3.1, -0.5]) as in Table 2, Model 1, meaning reuse of validation logic is more likely in the low-debt version, and programming_experience near zero (paper: 0.26).

Note on the `M1_PLAN` tag: it's commit 39a70cf from 20/10/2026, which is after the Week 5 freeze, and it doesn't have a plan document in it. So the real record of our frozen plan is the tracker row above, not the tag.

## 2. Result

Numbers below are from `RUN.md` section 5 (Ben's run). Model `reuse0.all.exp`, 4 chains x 2000 iterations, seed 20210421, 51 observations from 29 sessions.

| Condition | Threshold | Ours | Met? |
|---|---|---|---|
| Convergence | max R-hat <= 1.01 | 1.005 | yes |
| Divergences | 0 | 0 | yes |
| Sign | beta negative | -1.77 | yes |
| Interval | 95% CrI excludes 0 | [-3.13, -0.48] | yes |
| Magnitude | mean in [-3.12, -0.54] | -1.77 | yes |

Experience came out at 0.26, the same as the paper. That isn't part of the rule, but it was in our expected result.

Comparison with Table 2 in the paper. Models (1) and (2) in Table 2 are the validation and constructor outcomes, which the authors' code fits together as one model (`reuse0.all.exp`):

| Parameter | Paper | Ours |
|---|---|---|
| Validation: beta high_debt_version:false | -1.79 [-3.12, -0.54] | -1.77 [-3.13, -0.48] |
| Validation: beta experience | 0.26 [-0.67, 1.21] | 0.26 [-0.66, 1.20] |
| Constructor: beta high_debt_version:false | -1.63 [-2.95, -0.39] | -1.64 [-2.96, -0.39] |
| Constructor: beta experience | 0.31 [-0.66, 1.24] | 0.32 [-0.61, 1.28] |

All our means are within 0.02 of the paper's. Our validation interval is a little wider than the paper's, which is normal given MCMC sampling noise and our different Stan version (see D5). The rule checks the mean, not the interval edges, so this doesn't affect the verdict. The constructor rows aren't part of our rule, but they matching too shows the whole model reproduced, not just the one number we picked.

**Verdict: reproduced under the frozen rule (provisional).**

It's provisional for two reasons:
1. The output files that `runModel1.R` writes (`model1_checks.txt`, `verdict.txt` etc.) aren't in the repo yet. The script runs inside the `Analysis` folder, so `outputs/` was created in there, and that folder doesn't get uploaded to GitHub (see section 5). For now the numbers only exist in `RUN.md`.
2. `RUN.md` says the numbers are from the "first run: interactive R console", but later it says the rule "passed in run4", so it's not clear which run they came from.

### 2a. Check against the output files (Ben to fill in)

Once `outputs/` is pushed, copy each value from the file it names (not from `RUN.md`). If something doesn't match, don't change section 2. Flag it so we can sort it out together.

| What | Value above | Value in file | File | Match? |
|---|---|---|---|---|
| Max R-hat | 1.005 | | model1_checks.txt | |
| Divergences | 0 | | model1_checks.txt | |
| Validation beta mean | -1.77 | | model1_checks.txt | |
| Validation beta 95% CrI | [-3.13, -0.48] | | model1_checks.txt | |
| Experience mean | 0.26 | | model1_checks.txt | |
| All 5 conditions TRUE | yes | | verdict.txt | |
| R / brms version | R 4.0.5, brms 2.15.0 | | sessioninfo_run.txt | |
| Which run these files are from | | | | |
| Commit with outputs/ | | | | |
| `git ls-tree HEAD Analysis Data` | | | | |

If everything matches, remove "(provisional)" from the verdict.

### 2b. Was it a real refit?

brms saves fitted models in `fits/` and loads them instead of refitting if they're already there. If the authors' saved fits had been in `fits/` we'd just be getting their numbers back, so this matters.

- `runModel1.R` checks that `fits/` is empty before it runs (`stopifnot(length(list.files("fits")) == 0)`), so any run done through the script is a real refit.
- The first interactive run didn't go through the script, so there's no record of whether `fits/` was empty then.
- Ben noted in `RUN.md` that the short runtime (46.5s for run 4) and the compile warnings should be checked before calling it a clean refit.
- Optional extra check: compare our saved fit with the authors' (`fits_authors_cached/reuse0.all.exp.rds`). The draws should be close but not identical. Identical draws would mean the cached file was loaded.

### 2c. RUN.md and runModel1.R don't match

- `RUN.md` says to run `run_model1.R`, but the file is called `runModel1.R`.
- `RUN.md` says to run from the repo root with `analysis_v1.6` next to it, and mentions `ANALYSIS_DIR` and `RUN_LABEL`. The script actually uses relative paths, so it has to be run from inside `analysis_v1.6`, and it doesn't read either variable.
- `RUN.md` lists `provenance.txt` and `sanity_check.csv` as outputs, but the script doesn't create them.
- The overview says the script compares the authors' fit with ours, but it only fits ours.

One of them needs to be updated so someone else can follow `RUN.md` and get the same result.

## 3. Changes from the frozen plan

Ben already noted D1, D3 and D4 in the "Dated Clarifications" part of `RUN.md`.

| # | Plan said | What we did | Why | Effect |
|---|---|---|---|---|
| D1 | All submissions in data.csv, no exclusions | Used the authors' `d.completed` (51 rows, 29 sessions). The raw data.csv has 73 rows / 43 sessions. | The paper's 51/29 comes from the authors' own filter (`task_completion == "Completed"`). Our plan mixed up the raw file and the analysis set. We added no exclusions ourselves. | None, same set as the paper |
| D2 | One outcome, `(1 \| participant)` | The authors' model `reuse0.all.exp` fits validation and constructor together, grouped by `session` | We ran their model unchanged and only apply the rule to the validation beta | None. Checked against Table 2: rows (1) and (2) match our two outcomes, and section 6.1 (p.18) calls them "Table 2 (Models 1 & 2)" |
| D3 | `programming_experience` | `work_experience_programming.s` (scaled) | Just the variable name in their code | None |
| D4 | brms 2.15.1 | brms 2.15.0 | 2.15.0 is the authors' version, and 2.15.1 was a mistake in our plan. Confirmed by Ben and in `Environment_setup.md`. | None expected |
| D5 | Same setup as authors | rstan 2.21.2 / StanHeaders 2.21.0.7 (authors had 2.26.1), Windows instead of Linux | Couldn't get 2.26.1 working with R 4.0.5 and Rtools40 | Small numeric differences, as expected |
| D6 | Data v1.4 | The authors' `setup.Rmd` pulls data from `master` under their old organisation name. We swapped just that URL to v1.4 in a copy of the code and left their file alone. | So we actually use the version we froze | Same row count (73) either way |
| D7 | "a fixed seed" | Authors' seed, 20210421 | Plan didn't say which seed | Authors' README says not everything is seeded, so reruns can vary slightly |
| D8 | My Week 5 sample: first 12 SonarQube-scanned submissions | Not used for RQ1, replaced by the full d.completed set | The result we're checking is a model estimate over all participants. 12 rows from 6 people can't tell us if that estimate reproduces. That sample also used a different eligibility rule, and 2 of the 12 were "Invalid solution", which the authors exclude anyway. The project pack's "first 12" rule only applies when the task doesn't name a set, and here d.completed is that set. | The sample is still in our workbook (Sample (Step 2) tab) and could be used for RQ2 |
| D9 | R-hat <= 1.01 (didn't say for which parameters) | Checked all parameters | Stricter option | None, both give 1.005 |
| D10 | "Model 1" | The script pulls the authors' code chunk straight from `logic_reuse.Rmd` instead of us retyping it | Avoids copying mistakes | None |

## 4. Wrong or unclear assumptions

**The sign of beta.** Our rule says the beta for low debt should be negative, but our expected result says reuse is more likely in the low-debt version. That sounds contradictory, but it's right, because of how the authors coded their true/false variables. Their `encode.bool()` function in `setup.Rmd` puts "true" first:
- For `high_debt_version`, "true" (high debt) is the baseline, so the coefficient brms gives is for "false", i.e. the low-debt version.
- For `reused_logic_validation`, brms counts the second level as the outcome, which is "false" (not reused, so duplicated).
- So a negative beta means less duplication in the low-debt version, which means more reuse. That matches the paper.
- The note under Table 2 backs this up: intercepts are with Boolean values set to "true".

**Other things:**
- data.csv doesn't have 51 rows, it has 73 (D1).
- The model has two outcomes, not one (D2).
- `pkgbuild::has_build_tools()` said TRUE before Rtools40 was even installed, because it found a newer toolchain. Don't trust it. The Stan smoke test is the proper check.

## 5. Problems with the artefact / repo

- `setup.Rmd` loads data from an old URL (`BrokenWindowsInvestigation/Data/master`) instead of a tagged version. Fixed by swapping the URL (D6).
- Needs R 4.0.5, which is from 2021, so current CRAN packages won't install. We used the Posit snapshot from 2021-04-01.
- Needs Rtools40 specifically, plus a manual PATH line in `.Renviron`.
- rstan 2.26.1 wasn't available for our setup (D5).
- brms warns that global priors in multivariate models are deprecated, because of how the authors wrote their priors. It still works in 2.15.0, but a newer brms might not handle them the same way, which is another reason to stick to 2.15.0.
- We get two compile messages (`SyntaxError: Unexpected token .` and `g++ not found`), but compiling and sampling still work. We don't know the cause.
- The authors' saved fits in `fits/` would be loaded instead of refitting. We moved them to `fits_authors_cached/`.
- Our own repo: `Analysis/` and `Data/` on GitHub are embedded git repos without a `.gitmodules` file. They're just pointers to a commit, clicking them gives a 404, and nothing inside them is uploaded. That's why the outputs aren't visible.
  - TODO: record which commits they point to (`git ls-tree HEAD Analysis Data`), then either set them up as proper submodules or remove them, since `Environment_setup.md` already explains how to clone the authors' repos.
- The `m2repro` branch is 7 commits behind `main`, so the two need merging before we tag M2_REPRO.

## 6. How the paper defines debt

The project pack asks us to audit this.

**High vs low debt.** The authors made two versions of each Java system (booking and tickets). The high-debt version had bad variable names and lots of duplicated code added on purpose. The low-debt version had "no or few technical debt items apart from those purposefully introduced" (p.10). So debt isn't measured here, it's two fixed versions the authors designed. Each participant did one task in each version.

**The outcome (logic reuse).** This records whether the existing validation logic or constructor was "duplicated or reused while completing the task", and "any type of reuse qualified" (p.10). It's yes/no per submission.

**How it was scored.** Manually. The authors dropped SonarQube's duplication rules "in favor of manual inspection" because they didn't work well enough (p.11). Two of the authors went through every submission independently, compared results and resolved any differences (p.31). But:
- there's no detailed coding guide beyond the one-line definition
- they don't report an agreement score (like Cohen's kappa) or how many disagreements there were
- they don't say whether they knew which version each submission came from while scoring

We use their scored column as it is, so if there are mistakes in it, our reproduction has them too and can't catch them. Re-scoring the submissions was outside our RQ1 scope.

**Overlap between debt and outcome.** Duplicated code is part of how the authors made the high-debt version, and duplicated code is also what the outcome measures. Developers might reuse less in the high-debt version just because reuse is harder there (more copies, less clear what to reuse), not because they're copying the bad standard around them like the theory says. The data can't separate these two explanations. The authors admit a similar problem: bad names and duplication were added together, so they can't tell the two effects apart (p.25). Also, the result only covers this kind of debt (bad names and duplication in two small Java systems), not technical debt in general.

## 7. How much do we trust it?

**The paper's result**

Good:
- Data and code are public and versioned.
- Models and priors are all in the Rmd files.
- Each person did both versions.
- Results are reported as full posteriors.
- Two people scored the outcome.

Not so good:
- Only 29 participants, from snowball and convenience sampling (p.31).
- Only completed submissions are analysed, which drops about 30% of rows. If people were more likely to not finish one version, that could skew things.
- The debt/outcome overlap above.
- Manual scoring with no agreement score.
- Only two small Java tasks.

**Our reproduction**

We used the same data, code and model, refitted from scratch. So it shows the paper's numbers come from its data and code. It doesn't independently test whether broken windows effects are real. Remaining risks are the different package versions and OS (D5), incomplete seeding (D7), and the outputs not being committed yet (section 2).

TODO: Amy's clean re-run. Log it in the table at the end of `Environment_setup.md` and note whether her beta matches Ben's.

## 9. To do before tagging M2_REPRO
- [ ] Merge `main` into `m2repro`
- [ ] Remove the "Notes to move into audit.md" section from `Environment_setup.md`
- [ ] Change references to `audit.md` in `Environment_setup.md` to `Audit.md`
- [ ] Fill in "Reproduction result (brief)" and "Evidence link / commit / output" for G23 in the tracker
