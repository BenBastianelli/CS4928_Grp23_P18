# Overview
This file covers the assumptions, decisions made and the execution of ```m2repro/runModel1.R``` the R file that analyses the results of the authors fitted model against our fitted model to determine whether the results of the BWT for one case can be reproduce

# Frozen Plan Review (Week 5)
The frozen plan as of week 5 for our RQ1 was as follows :
|RQ |Bounded sample / case IDs |Method / decision rule:|
|---|---|---|
|Can one broken-windows effect be reproduced from the study data?| one submission, no sampling and no added exclusions, analysed with Analysis v1.6 |refit the authors' Model 1 , using a fixed seed. We count it as reproduced if the run converges and the high_debt_version:false beta is negative with a 95% CrI that excludes zero and a mean inside the paper's [-3.12, -0.54].| <br>
## Expected Result  
We expect beta ~ -1.8 (CrI ~ [-3.1, -0.5]) as in Table 2, Model 1, meaning reuse of validation logic is more likely in the low-debt version, and programming_experience near zero (paper: 0.26).

## Dated Clarifications
What changed, in week 7 the frozen Week 5 text is unchanged <br>
- The raw ```data.csv ``` has 73 rows from 43 sessions. The papers 51 rows / 29 participants is the authors own
- analysis set ```d.completed``` \(```task_completion = "Completed" ``` \). We added no further exclusions.<br>
- Variable names in the code: grouping is session; experience is work_experience_programming.s (scaled).<br>
- Installed brms is 2.15.0 (the authors' version), not 2.15.1 as written in the plan.

# Steps
All commands are run from the group repo root, with the authors' clone as a sibling folder named `analysis_v1.6` (see `Environment_setup.md` step 1).
 
1. **Make sure the models will really be refitted.** The authors' cached fits must not be in `analysis_v1.6/fits/`:
```
   ren analysis_v1.6\fits fits_authors_cached
   mkdir analysis_v1.6\fits
```
   (If you have run the script before, move your own previous fit aside too, e.g. `ren analysis_v1.6\fits\reuse0.all.exp.rds reuse0.all.exp_run1.rds` and then move it out of `fits\`. The script stops if `fits\` is not empty.)
2. **Run the script**, using R 4.0.5 (`where Rscript` shows which R will be used):
```
   Rscript run_model1.R > outputs\run_refit.log 2>&1
```
   To keep an earlier run's outputs, set a label first: `set RUN_LABEL=run2` (Command Prompt). Optional: `set ANALYSIS_DIR=path\to\analysis_v1.6`.<br>
3. Expected runtime: 46.5s based off Run 4. The first run compiles Stan, so expect several minutes.
4. The messages listed under "Known messages" below are expected.

## 3. What the script produces (in `outputs/`)
 
| File | Contains |
|---|---|
| `provenance.txt` | date, R / brms / rstan / StanHeaders versions, Analysis commit hash |
| `model_chunk_as_run.R` | the authors' model code exactly as extracted and run |
| `model1_checks.txt` | `summary(fit)` plus the numbers used by the rule |
| `sessioninfo_run.txt` | `sessionInfo()` from the run |
| `sanity_check.csv` | model-free counts and proportions of validation-logic reuse by debt level |
| `verdict.txt` | the five rule conditions as TRUE/FALSE |
| `run_refit.log` | full console log (only when run via `Rscript` as above) |

## 4. How each part of the rule is computed
 
| Rule item | Code | Where saved |
|---|---|---|
| R-hat <= 1.01 | `max(rhat(fit), na.rm = TRUE)` (all parameters; the validation-only maximum is also reported) | `model1_checks.txt` |
| Zero divergences | `sum(subset(nuts_params(fit), Parameter == "divergent__")$Value)` | `model1_checks.txt` |
| beta negative, CrI excludes 0 | `fixef(fit)["reusedlogicvalidation_high_debt_versionfalse", ]`, columns Estimate and Q97.5 | `model1_checks.txt` |
| Mean inside [-3.12, -0.54] | same row, Estimate | `verdict.txt` |
| Experience (reported, not part of the rule) | `fixef(fit)["reusedlogicvalidation_work_experience_programming.s", ]` | `model1_checks.txt` |

The frozen rule does not say whether R-hat covers all parameters or only the validation ones. We apply the stricter reading (all parameters). In our run both maxima are the same (1.0049), so the choice does not change the verdict.

## 5. Our results
 
First run: interactive R console, 2026-10-21, 4 chains x 2000 iterations, seed 20210421 (set in the authors' code), 51 observations from 29 sessions. No console log exists for this run.
 
| Quantity | Estimate | Est. error | 95% CrI |
|---|---|---|---|
| validation: high_debt_versionfalse (logit scale) | -1.77 | 0.69 | [-3.13, -0.48] |
| validation: experience (scaled) | 0.26 | 0.47 | [-0.66, 1.20] |
| constructor: high_debt_versionfalse | -1.64 | 0.66 | [-2.96, -0.39] |
| constructor: experience (scaled) | 0.32 | 0.47 | [-0.61, 1.28] |
 
Max R-hat 1.005 (all parameters and validation-only); divergences 0.
 
| Condition | Threshold | Observed | Met? |
|---|---|---|---|
| Convergence | R-hat <= 1.01 | 1.005 | yes |
| Divergences | 0 | 0 | yes |
| Sign | beta negative | -1.77 | yes |
| Interval | 95% CrI excludes 0 | [-3.13, -0.48] | yes |
| Magnitude | mean in [-3.12, -0.54] | -1.77 | yes |
 
**Verdict under the frozen rule: reproduced.**
RQ1: The frozen decision rule passed in run4. The analysis loaded the pinned dataset, verified the expected 73-row raw dataset and 51-row completed subset, extracted the authors’ multivariate reuse model directly from logic_reuse.Rmd, and reported that all five predefined diagnostic and effect criteria were satisfied. However, the compilation warnings and short execution time require verification before classifying this as a confirmed clean refit.

### Still pending
- [ ] Optional: compare with the authors' stored fit (`fits_authors_cached/reuse0.all.exp.rds`).

## 6. Guidance for a reviewing group
 
- Numbers will not be identical across rstan versions and platforms. Apply the same five conditions and report how far your estimates are from ours.
- Report any deviation: package versions, platform, anything that failed.
- Do not change the thresholds after seeing your numbers.

## 7. Known messages (observed, not resolved)
 
These appear while Stan compiles; sampling still completes and returns a fitted object.
- `Error in context_eval(...) : SyntaxError: Unexpected token .`
- `'C:/rtools40/usr/mingw_/bin/g++' not found`
- `Specifying global priors for regression coefficients in multivariate models is deprecated` (brms 2.15.0, from the authors' unchanged code)
- `Setting 'rescor' to FALSE by default for this model`