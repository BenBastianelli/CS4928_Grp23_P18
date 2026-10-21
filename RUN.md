# Running and checking Model 1

Prerequisite: SETUP.md completed. Tested by [name], [date].

## 1. Prepare a clean refit
In analysis_v1.6: ren fits fits_authors_cached, then mkdir fits.
Verify: list.files("fits") returns character(0)

## 2. Run the script
Rscript run_model1.R   (or run it in RStudio from analysis_v1.6)
The script: loads setup.Rmd with the data URL pinned to v1.4, checks
51 rows / 29 sessions, fits Model 1 with the authors' formula and priors,
and writes outputs/.
Expected runtime: [fill in]. First run compiles Stan.

## 3. Outputs produced
| File | Contains |
|---|---|
| outputs/model1_summary.txt | summary(fit) |
| outputs/model1_checks.txt | R-hat, divergences, beta mean and 95% CrI, experience estimate |
| outputs/sanity_check.csv | proportions from raw data by debt level |
| outputs/sessioninfo.txt | environment record |

## 4. Apply the frozen rule
| Condition | Threshold | Observed | Met? |
|---|---|---|---|
| Convergence | R-hat <= 1.01 | | |
| Divergences | 0 | | |
| Sign | beta negative | | |
| Interval | 95% CrI excludes 0 | | |
| Magnitude | mean in [-3.12, -0.54] | | |
Verdict: [reproduced / partly / not reproduced]

## 5. Optional comparison run
[Run with the authors' cached fits and compare.]

## Deviations during this run
[Anything changed from the frozen plan, and why.]
