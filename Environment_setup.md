# Environment setup (Windows)

Goal: reproduce Model 1 (frozen plan) from BWTSE/Analysis v1.6 using Data v1.4.
Scope: environment only. Running the model, extracting results and applying the decision rule go in `RUN.md`; interpretation goes in `audit.md`.
Tested on: Windows [version], 2026-10-21, by [name].

Only write what has been run and checked. Leave anything unverified marked as such.

## Prerequisites
- R 4.0.5 (`R.version.string` must say `R version 4.0.5`)
- Rtools40 (the build for R 4.0.0-4.1.x, NOT Rtools42+)
- RStudio, git

## 1. Get the authors' code
```
git clone https://github.com/BWTSE/Analysis.git analysis_v1.6
cd analysis_v1.6
git checkout v1.6
git rev-parse HEAD
```
Expected: `d8332c64550e427d79cba4713ba8146dbd5cfb44`

Git prints a "detached HEAD" notice. That is expected when checking out a tag and is harmless: this clone is only read and run, never committed to.

Move the authors' cached model fits aside so the models are genuinely refitted:
```
ren fits fits_authors_cached
mkdir fits
```
(Command Prompt syntax; `mv` does not exist there. In PowerShell use `Rename-Item fits fits_authors_cached`.)

Verify in R: `list.files("fits")` returns `character(0)`.

## 2. Install Rtools40
Install to the default `C:\rtools40`. Then check whether `~/.Renviron` exists:
```r
file.exists("~/.Renviron")
```
- If `FALSE`, create it:
  ```r
  writeLines('PATH="${RTOOLS40_HOME}\\usr\\bin;${PATH}"', con = "~/.Renviron")
  ```
- If `TRUE`, append that line; do not overwrite.

Restart RStudio fully (close and reopen; `.Renviron` is only read at startup).

Verify:
```r
dir.exists("C:/rtools40")       # TRUE
Sys.getenv("RTOOLS40_HOME")     # [record the value you see]
Sys.which("make")               # [record: should point inside rtools40]
Rcpp::evalCpp("1 + 1")          # 2   <- compiler test (needs Rcpp installed; see step 3)
```
Note: `pkgbuild::has_build_tools()` can return TRUE even without Rtools40. In our run it printed TRUE before Rtools40 was installed, because it found a newer toolchain at `C:/RBuildTools/4.0` (folders `ucrt64`, `clang64`, which belong to R 4.2+). Do not rely on it. The Stan smoke test in step 7 is the real end-to-end check.

## 3. Install packages from the April 2021 snapshot
```r
options(repos = c(CRAN = "https://packagemanager.posit.co/cran/2021-04-01"))
install.packages(c("plyr","dplyr","tidyr","reshape2","tibble","scales","curl",
  "hashr","ggplot2","likert","bayesplot","ggpubr","HDInterval","ggridges",
  "knitr","rmarkdown","brms"))
```
Answer "No" if asked to install from source. `options(repos = ...)` resets when R restarts, so set it again in any new session before installing.

## 4. Verify versions
| Package | Authors' | Ours (fill in) | Match? |
|---|---|---|---|
| R | 4.0.5 | 4.0.5 | yes |
| brms | 2.15.0 | 2.15.0 | yes |
| rstan | 2.26.1 | 2.21.2 | no |
| StanHeaders | 2.26.1 | 2.21.0.7 | no |
| V8 | 3.4.0 | 3.4.0 | yes |
| loo | 2.4.1 | [record] | |
| bayesplot | 1.8.0 | [record] | |

## 5. Record the environment
```r
dir.create("outputs", showWarnings = FALSE)
writeLines(capture.output(sessionInfo()), "outputs/sessioninfo.txt")
write.csv(installed.packages()[, c("Package","Version")], "outputs/package_versions.csv")
```
Copy these into the group repo's `outputs/` folder so they are committed with the other evidence.

## 6. Pin the data version
The authors' `setup.Rmd` downloads data from `master` under the old organisation name (`BrokenWindowsInvestigation/Data/master/data.csv`). We run their file unchanged except for swapping that one URL for the `v1.4` tag. Run from the `analysis_v1.6` folder (`getwd()` must end in `analysis_v1.6`):
```r
options(mc.cores = 4)
src  <- knitr::purl("setup.Rmd", output = tempfile(), quiet = TRUE)
code <- readLines(src)
old  <- "BrokenWindowsInvestigation/Data/master/data.csv"
new  <- "BWTSE/Data/v1.4/data.csv"
sum(grepl(old, code, fixed = TRUE))     # 1: the line to replace exists
code <- sub(old, new, code, fixed = TRUE)
sum(grepl(new, code, fixed = TRUE))     # 1: swap applied
eval(parse(text = code))
```
Check (counts observed in our run):
```r
stopifnot(nrow(d.orig) == 73, length(unique(d.orig$session)) == 43)           # raw data.csv
stopifnot(nrow(d.completed) == 51, length(unique(d.completed$session)) == 29) # authors' analysis set
```
| Object | Rows | Sessions | Definition |
|---|---|---|---|
| `d.orig` | 73 | 43 | raw `data.csv` (v1.4; same count on master) |
| `d.completed` | 51 | 29 | rows with `task_completion == "Completed"` |
| `d.both_completed` | 44 | 22 | rows from sessions where both tasks were completed |

The 51 rows / 29 sessions in the paper correspond to `d.completed`, not to the raw file.

## 7. Smoke test
Purpose: prove Stan compiles and samples. It is deliberately tiny and is **not** the analysis. Do not save or commit its output, and do not record anything it prints as a result.
```r
smoke <- brm(reused_logic_validation ~ 1 + high_debt_version,
             data = as.data.frame(d.completed), family = bernoulli(),
             chains = 1, iter = 200, refresh = 0)
class(smoke)     # "brmsfit"
summary(smoke)   # prints a table (51 observations)
```
Optional, to see whether messages come from brms or rstan:
```r
m <- rstan::stan_model(model_code = "parameters { real y; } model { y ~ normal(0, 1); }")
f <- rstan::sampling(m, chains = 1, iter = 200, refresh = 0)
print(f)
```
Expected output: a fitted object and a summary table. R-hat and ESS warnings are expected (1 chain, 200 iterations) and say nothing about the toolchain.
Expected runtime: [record]; the first compile takes a few minutes.

Afterwards check `fits/` is still empty: `list.files("fits")`.

## Known issues / deviations
Observed, not resolved:
1. `Error in context_eval(...) : SyntaxError: Unexpected token .` appears during compilation, both through brms and through plain `rstan::stan_model`. Compilation and sampling still complete and return a fitted object. Cause not identified; treat as cosmetic until shown otherwise.
2. `'C:/rtools40/usr/mingw_/bin/g++' not found` appears as a warning during compilation. Compilation still succeeds. Cause not identified.
3. `pkgbuild::has_build_tools()` returns TRUE without Rtools40 (see step 2).
4. `mv` fails in Command Prompt; use `ren`.

Deviations from the versions in the authors' environment: rstan 2.21.2 and StanHeaders 2.21.0.7 instead of 2.26.1 (step 4).

## Handoff to RUN.md
The environment is ready when steps 1-7 are checked off. Next, in `RUN.md`:
- the target model in `logic_reuse.Rmd` is `reuse0.all.exp` (fitted on `d.completed`, seed 20210421, includes `work_experience_programming.s`)
- the chunk that creates the scaled column `work_experience_programming.s` still has to be located and copied unchanged into the run script
- results extraction, the decision rule and the verdict belong in `RUN.md`

## Notes to move into audit.md later (do not expand here)
Placeholders only; move them to `audit.md`, expand there, and delete them from this file.
- Deviations from the frozen plan: brms 2.15.0 installed vs 2.15.1 in the frozen entry; rstan and StanHeaders versions differ from the authors'; Windows vs the authors' Linux; data pinned via a URL substitution in a purl-generated copy of `setup.Rmd`, not an edit to the authors' file.
- Sample definition: raw `data.csv` is 73 rows / 43 sessions; the analysis set `d.completed` is 51 rows / 29 sessions, a completed-tasks-only selection made by the authors' pipeline. No exclusions added by our group.
- Model identification: `reuse0.all.exp` is multivariate (validation and constructor outcomes, correlated session intercepts), so the frozen entry's single-outcome wording needs a dated clarification note. Still to confirm against Table 2 which paper model this is, and that the [-3.12, -0.54] interval belongs to it.
- Naming: the experience predictor is `work_experience_programming` (scaled as `.s`); the grouping variable is `session`.
- Environment observations: the two compile-time messages above, the `has_build_tools()` false positive, and the authors' README note that loo and posterior sampling are not fully seeded.
- Debt-definition audit: how the paper defines high debt and logic reuse, and the overlap between treatment and outcome. To be written from the paper.

## Clean re-run log (second person)
| Date | Person | Machine / OS | Steps completed | Problems and fixes |
|---|---|---|---|---|
| | | | | |