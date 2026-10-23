# Overview
This repository serves as a living record for the investigation of RQ's defined in our Student tracker for BWTSE (P_18)


# Work to date

Instructional files for environment set up and running the model, refitted model and results extraction made.
Audit file made for general overview of the trustworthiness of our reproduction
# Bounded Reproduction of one broken windows effect

# How to reproduce our result (short guide)

For testers who want to validate our result with minimal reading. Windows only. You need internet access. The package install (step 6) is the slow step, and the model run takes a few minutes, mostly compiling Stan.

More detail, if something goes wrong: `Environment_setup.md` (environment), `RUN.md` (the run and the decision rule), `audit.md` (deviations and how much to trust the result).

## 1. Install (once)
- **R 4.0.5**: https://cran.r-project.org/bin/windows/base/old/4.0.5/ (the Windows `.exe`). Other R versions will not work with the 2021 package snapshot we use.
- **Rtools40**, the build for R 4.0.0 to 4.1.x (not Rtools42 or newer): https://cran.r-project.org/bin/windows/Rtools/ . Install to the default `C:\rtools40`.
- **Git**.

## 2. Tell R where Rtools is (once)
Open R 4.0.5 (the R GUI or RStudio with R 4.0.5 selected) and run this line. It appends to `~/.Renviron` and does not overwrite an existing file:
```r
cat('\nPATH="${RTOOLS40_HOME}\\usr\\bin;${PATH}"\n', file = "~/.Renviron", append = TRUE)
```
Then close and reopen R. The setting is only read at startup.

## 3. Get the authors' code, pinned to v1.6
In Command Prompt:
```
git clone https://github.com/BWTSE/Analysis.git analysis_v1.6
cd analysis_v1.6
git checkout v1.6
git rev-parse HEAD
```
Expected last line: `d8332c64550e427d79cba4713ba8146dbd5cfb44`. Git prints a "detached HEAD" notice. That is expected when checking out a tag and is harmless.

## 4. Copy our scripts into the clone
From this repository, copy `install_packages.R`, `environment_setup.R` and `runModel1.R` into the `analysis_v1.6` folder.

## 5. Point the terminal at R 4.0.5
In Command Prompt, from inside `analysis_v1.6` (adjust the folder if you installed R elsewhere):
```
set PATH=%PATH%;C:\Program Files\R\R-4.0.5\bin
Rscript --version
```
The second line must report 4.0.5. In PowerShell, use `$env:Path += ";C:\Program Files\R\R-4.0.5\bin"` instead. The `set PATH` setting only lasts until you close the window.

## 6. Install the packages (slow)
```
Rscript install_packages.R
```
It ends by printing package versions (brms should be 2.15.0). If it stops with an error, send us the first error line.

## 7. Record your environment
```
Rscript environment_setup.R
```
This prints your working directory and writes `outputs\sessioninfo.txt` and `outputs\package_versions.csv`: a record of your R and package versions. It does not install or verify anything. The Stan compiler is tested by the next step.

## 8. Run the model
`analysis_v1.6\fits\` must contain nothing except `.gitkeep`. The authors' v1.6 tag ships no saved fits. If you have run this before, move the old fit out of `fits\` first, or brms will reuse it instead of refitting.
```
Rscript runModel1.R
```
There is a lot of output. At the end you should see five `TRUE` values and a final `[1] TRUE`:
```
convergence_rhat_le_1.01  zero_divergences  sign_negative  ci_excludes_zero  mean_in_paper_interval
```
Our result is "reproduced" when all five are `TRUE`.

## 9. Check the numbers
Open `outputs\model1_checks.txt`. In our runs (two separate installs, identical to seven digits):

| Quantity | Our value |
|---|---|
| Validation high-debt coefficient (mean) | -1.77 |
| 95% credible interval | [-3.13, -0.48] |
| Experience coefficient (mean) | 0.26 |
| Max R-hat | 1.005 |
| Divergences | 0 |

The paper's Table 2 gives -1.79 [-3.12, -0.54] and 0.26 for the same model (details in `RUN.md`). Your numbers may differ slightly if your package versions or platform differ from ours. The five `TRUE` values are the pass criterion. Files created in `outputs\` by this step: [confirm with `dir outputs`: expected `model1_checks.txt`, `verdict.txt`, `model_chunk_as_run.R`, `sessioninfo_run.txt`].

## Messages that are expected
While Stan compiles you may see `'make' not found`, `Specifying global priors for regression coefficients in multivariate models is deprecated`, or (on some machines) `SyntaxError: Unexpected token .`. Compilation and sampling still complete in our runs. We have not identified the cause of the first and last.
