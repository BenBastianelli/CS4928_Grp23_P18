#Check the working directory and prepare the output folders
print(getwd())

stopifnot(file.exists("setup.Rmd"))
stopifnot(file.exists("logic_reuse.Rmd"))

dir.create("outputs", showWarnings = FALSE)

#Record the R Environment
writeLines(
  capture.output(sessionInfo()),
  "outputs/sessioninfo.txt"
)

write.csv(
  installed.packages()[, c("Package", "Version")],
  "outputs/package_versions.csv"
  row.names = FALSE
)

