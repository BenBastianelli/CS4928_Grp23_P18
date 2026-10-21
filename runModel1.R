# ---- 1. Load data, pinned to v1.4 (Environment_setup.md step 6) ----
options(mc.cores = 4)
src  <- knitr::purl("setup.Rmd", output = tempfile(), quiet = TRUE)
code <- readLines(src)
old  <- "BrokenWindowsInvestigation/Data/master/data.csv"
new  <- "BWTSE/Data/v1.4/data.csv"
stopifnot(sum(grepl(old, code, fixed = TRUE)) == 1)
code <- sub(old, new, code, fixed = TRUE)
eval(parse(text = code))
stopifnot(nrow(d.orig) == 73, length(unique(d.orig$session)) == 43)
stopifnot(nrow(d.completed) == 51, length(unique(d.completed$session)) == 29)
stopifnot("work_experience_programming.s" %in% names(d.completed))
stopifnot(length(list.files("fits")) == 0)     # empty fits/ forces a real refit

# ---- 2. Extract the authors' model chunk (no retyping) ----
dir.create("outputs", showWarnings = FALSE)
rmd <- readLines("logic_reuse.Rmd")
s <- grep("^`{3}\\{r variation.all.exp,", rmd)
stopifnot(length(s) == 1)
e <- s + which(rmd[(s + 1):length(rmd)] == strrep("`", 3))[1]
chunk <- rmd[(s + 1):(e - 1)]
writeLines(chunk, "outputs/model_chunk_as_run.R")
cat(chunk, sep = "\n")                          # check it matches what you saw

# ---- 3. Fit (first run compiles Stan; several minutes) ----
eval(parse(text = chunk))
fit <- reuse0.all.exp

# ---- 4. Extract exactly what the frozen rule needs ----
p_hd  <- "reusedlogicvalidation_high_debt_versionfalse"
p_exp <- "reusedlogicvalidation_work_experience_programming.s"
fe    <- fixef(fit)
rh    <- rhat(fit)
div   <- sum(subset(nuts_params(fit), Parameter == "divergent__")$Value)
est   <- fe[p_hd, ]

res <- list(
  highdebt   = est,
  experience = fe[p_exp, ],
  max_rhat_all        = max(rh, na.rm = TRUE),
  max_rhat_validation = max(rh[grepl("reusedlogicvalidation", names(rh))], na.rm = TRUE),
  divergences = div
)
sink("outputs/model1_checks.txt"); print(summary(fit)); print(res); sink()
writeLines(capture.output(sessionInfo()), "outputs/sessioninfo_run.txt")

# ---- 5. Frozen decision rule, unchanged ----
verdict <- c(
  convergence_rhat_le_1.01 = unname(res$max_rhat_all <= 1.01),
  zero_divergences         = div == 0,
  sign_negative            = unname(est["Estimate"] < 0),
  ci_excludes_zero         = unname(est["Q97.5"] < 0),
  mean_in_paper_interval   = unname(est["Estimate"] >= -3.12 && est["Estimate"] <= -0.54)
)
print(verdict); print(all(verdict))
capture.output(print(verdict), file = "outputs/verdict.txt")