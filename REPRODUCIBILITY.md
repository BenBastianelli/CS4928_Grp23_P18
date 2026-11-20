# Reproducing Group 23's P18 submission

Use the integrated submission at tag `final`. The commands below use Windows PowerShell and start at the repository root unless a step changes directory.

```powershell
git clone https://github.com/BenBastianelli/CS4928_Grp23_P18.git
Set-Location CS4928_Grp23_P18
git switch --detach refs/tags/final
```

## 1. M2 — Refit Model 1

Install R 4.0.5 and Rtools40. Follow the Rtools setup in [the root README](README.md), restart R after updating `.Renviron`, and confirm the terminal uses R 4.0.5. The setup script uses the 2021-04-01 Posit CRAN snapshot. The refit script reads [Data v1.4](https://raw.githubusercontent.com/BWTSE/Data/v1.4/data.csv) and checks that the analysis includes 51 completed observations from 29 sessions.

```powershell
git clone --branch v1.6 https://github.com/BWTSE/Analysis.git ..\analysis_v1.6
git -C ..\analysis_v1.6 rev-parse HEAD
Copy-Item -Path install_packages.R,environment_setup.R,runModel1.R -Destination ..\analysis_v1.6
$env:Path = 'C:\Program Files\R\R-4.0.5\bin;' + $env:Path
Rscript --version
Push-Location ..\analysis_v1.6
Rscript install_packages.R
Rscript environment_setup.R
Rscript runModel1.R
Pop-Location
```

The Analysis revision should be `d8332c64550e427d79cba4713ba8146dbd5cfb44`. Use a fresh Analysis checkout or move saved fits out of its `fits/` directory before rerunning the refit. Check the newly generated files in `analysis_v1.6/outputs/`. All five entries in `verdict.txt` should be `TRUE`: R-hat at most 1.01, zero divergences, a negative high-debt coefficient, a 95% credible interval excluding zero, and a posterior mean within the paper's interval. The recorded reference estimate is −1.77 with a 95% credible interval of [−3.13, −0.48]. See [saved model checks](outputs/model1_checks.txt) and [the audit](Audit.md).

## 2. Event A — Reproduce the frozen Java and SonarQube comparison

Get the original Java scenarios at the revision recorded in the [Event A command log](event-a/runs/CommandPromptsForRuns.txt). The JDK must provide both `javac` and `java`.

```powershell
git clone https://github.com/BWTSE/Scenarios.git ..\Event_A_repo\Scenarios
git -C ..\Event_A_repo\Scenarios switch --detach 512c24d
$env:CS4928_SCENARIOS_DIR = (Resolve-Path ..\Event_A_repo\Scenarios).Path
```

1. Review the four saved Java outputs and accompanying run notes in [event-a/runs](event-a/runs/). Runs 1–4 are Booking high debt, Booking low debt, Tickets high debt, and Tickets low debt. The original feature requests came from each scenario's `instructions.md`. To repeat the AI procedure, make separate working copies of the four baseline variants, submit the matching task text in VS Code Copilot Ask mode with the Auto model setting, and save the resulting Java files and run metadata. Use the saved outputs for the frozen comparison because a fresh response can vary.
2. Use the saved SonarQube exports in [study/Baseline](study/Baseline/) and [study/AI-Results](study/AI-Results/) to reconstruct the frozen metrics. To regenerate the exports, follow [FROZEN_REPLICATION.md](FROZEN_REPLICATION.md) for scanner setup, the quality profile, project keys, and export commands.
3. Install `matplotlib` and run the validation script. Its baseline constant currently points to `D:\Projects\CS4928\Event_A_repo\Scenarios`. If your sources are elsewhere, update `BASELINE_SOURCE_ROOT` in your scratch checkout to the directory resolved above. The M4 environment variable applies to the M4 script.

```powershell
python -m pip install matplotlib
python .\validate_frozen_replication.py
```

Check `study/AI-Results/analysis/frozen-replication-validation.csv` and the corresponding PNG. The saved totals are **761 baseline smells**, **859 AI-output smells**, and **0 duplicated blocks** in all eight projects. The four saved AI cases passed compilation and execution. Compare the interpretation with [Event A's result comparison](event-a/ResultComparison.md) and [design implication](event-a/DesignImplication.md).

## 3. M4 — Run the change-spread tool

Use Python 3.10 or later and the JDK from Event A. Leave the baseline environment variable set to the `Scenarios` folder. The script reads the saved Event A runs and the Event B Java inputs under `event-b/modernised-snapshots/` and `event-b/controlled-reproduction/`.

```powershell
python .\M4\compare_change_spread.py
Import-Csv .\M4\change-spread.csv |
    Format-Table scenario,state,files_changed,build_validation
```

Expect six rows with `PASS` in `build_validation`. Booking and Tickets each change one file in Event A. The modernised snapshots change two and one files respectively against their original baselines. In the controlled before/after comparison, each scenario adds one file. Compare the generated `M4/change-spread.csv` with the [saved Event B CSV](event-b/change-spread.csv). See [M4/README.md](M4/README.md) for input paths and baseline layout.

## 4. Event B — Verify the modernised scenarios

1. Review the changes to the isolated high-debt copies in [the Event B report](event-b/EVENT_B_REPORT.md). For the controlled comparison, use the versioned `modernised-before/` and `modernised-after/` inputs and the M4 command above. The [controlled reproduction notes](event-b/CONTROLLED_REPRODUCTION.md) explain the extension-based reuse in each case.
2. Compile and run the saved AI output for Booking and Tickets separately. The [Event B AI run guide](event-b/AI_RUN_GUIDE.md) gives the `javac` and `java` commands for `booking.Main` and `tickets.Main` and identifies the matching prompt and input files. Both saved outputs should compile and execute. For a fresh AI run, copy each `input/` directory into a separate workspace and submit its original `instructions.md` task in Copilot Ask mode. Record the model setting and save the response and resulting sources.
3. Inspect the [saved SonarQube results](event-b/sonarqube-results.csv) and [deltas](event-b/sonarqube-deltas.csv) for smells and duplication. Use the scan and export procedure in the Event B report when collecting fresh measurements. Compare the findings with [Event B's responses](event-b/Responses.md).
