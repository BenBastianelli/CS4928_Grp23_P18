reuse0.all.exp <- brm(
  "mvbind(
    reused_logic_validation,
    reused_logic_constructor
  ) ~ 1 + high_debt_version + work_experience_programming.s + (1 |c| session)",
  prior = c(
    prior(normal(0, 1), class = "b"),
    prior(normal(0, 1), class = "Intercept"),
    prior(exponential(1), class = "sd", resp = reusedlogicconstructor),
    prior(exponential(1), class = "sd", resp = reusedlogicvalidation),
    prior(lkj(2), class = "L")
  ),
  family = bernoulli(),
  data = as.data.frame(d.completed),
  control = list(adapt_delta = 0.95),
  file = "fits/reuse0.all.exp",
  file_refit = "on_change",
  seed = 20210421
)
