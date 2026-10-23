# install_packages.R
# Installs the R packages used by the reproduction from a dated CRAN snapshot (2021-04-01).
# Run with R 4.0.5, from inside the analysis_v1.6 folder:
#   Rscript install_packages.R
# This is the slow step. It needs internet access. Rtools40 must already be installed.

stopifnot(getRversion() == "4.0.5")

options(repos = c(CRAN = "https://packagemanager.posit.co/cran/2021-04-01"))

pkgs <- c("plyr", "dplyr", "tidyr", "reshape2", "tibble", "scales", "curl", "hashr",
          "ggplot2", "likert", "bayesplot", "ggpubr", "HDInterval", "ggridges",
          "knitr", "rmarkdown", "brms")

todo <- setdiff(pkgs, rownames(installed.packages()))
if (length(todo) > 0) {
  install.packages(todo, type = "win.binary")
} else {
  message("All packages already installed.")
}

still <- setdiff(pkgs, rownames(installed.packages()))
if (length(still) > 0) stop("Not installed: ", paste(still, collapse = ", "))

ver <- function(p) tryCatch(as.character(packageVersion(p)), error = function(e) "not installed")
print(sapply(c("brms", "rstan", "StanHeaders", "loo", "bayesplot", "V8"), ver))
# For comparison, the authors' sessionInfo lists: brms 2.15.0, rstan 2.26.1, StanHeaders 2.26.1,
# loo 2.4.1, bayesplot 1.8.0, V8 3.4.0. Our own runs used rstan 2.21.2 and StanHeaders 2.21.0.7.
