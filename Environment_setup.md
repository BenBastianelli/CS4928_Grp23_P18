# Environment setup (Windows)

Goal: reproduce Model 1 from BWTSE/Analysis v1.6 using Data v1.4.
Tested on: [Windows version], [date], by [name].

## Prerequisites
- R 4.0.5
- Rtools40 (the build for R 4.0.0–4.1.x, NOT Rtools42+)
- RStudio, git

## 1. Get the authors' code
git clone https://github.com/BWTSE/Analysis.git analysis_v1.6
cd analysis_v1.6
git checkout v1.6
git rev-parse HEAD
Expected: d8332c64550e427d79cba4713ba8146dbd5cfb44

## 2. Install Rtools40
Install to the default C:\rtools40. Then check whether ~/.Renviron exists
(file.exists("~/.Renviron")). If not, create it with:
PATH="${RTOOLS40_HOME}\usr\bin;${PATH}"
If it exists, append that line; do not overwrite. Restart RStudio fully.
Verify:
dir.exists("C:/rtools40")        # TRUE
Sys.getenv("RTOOLS40_HOME")      # [expected value]
Rcpp::evalCpp("1 + 1")           # 2   <- the real compiler test
Note: pkgbuild::has_build_tools() can return TRUE even without Rtools40
(it may find a newer Rtools); do not rely on it.

## 3. Install packages from the April 2021 snapshot
options(repos = c(CRAN = "https://packagemanager.posit.co/cran/2021-04-01"))
install.packages(c("plyr","dplyr","tidyr","reshape2","tibble","scales","curl",
  "hashr","ggplot2","likert","bayesplot","ggpubr","HDInterval","ggridges",
  "knitr","rmarkdown","brms"))
Answer "No" if asked to install from source.

## 4. Verify versions
| Package | Authors' | Ours (fill in) |
|---|---|---|
| R | 4.0.5 | |
| brms | 2.15.0 | |
| rstan | 2.26.1 | |
| StanHeaders | 2.26.1 | |
| loo | 2.4.1 | |
| bayesplot | 1.8.0 | |

## 5. Record the environment
writeLines(capture.output(sessionInfo()), "outputs/sessioninfo.txt")
write.csv(installed.packages()[, c("Package","Version")], "outputs/package_versions.csv")

## 6. Pin the data version
[Describe the URL substitution in run_model1.R: main -> BWTSE/Data/v1.4]
Check: nrow(d.orig) == 51 and 29 sessions.

## 7. Smoke test (Needs to be added)
[Command to run, expected output, expected runtime]

## Known issues / deviations (Needs to be added)
- [e.g. brms version differs from the frozen plan; reason]
- [anything that failed, and the fix]

