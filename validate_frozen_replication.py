import csv
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
BASELINE_SOURCE_ROOT = Path(r"D:\Projects\CS4928\Event_A_repo\Scenarios")
STUDY = ROOT / "study"
BASELINE_METRICS = STUDY / "Baseline" / "metrics-summary.csv"
AI_METRICS = STUDY / "AI-Results" / "metrics-summary.csv"
OUTPUT = STUDY / "AI-Results" / "analysis"

SCENARIOS = [
    ("Booking High TD", "PROJECT-BOOKING-HTD-BASE", "run1-GPT5.6Luna-booking-htd", "booking.Main"),
    ("Booking Low TD", "PROJECT-BOOKING-LTD-BASE", "run2-GPT5.6Luna-booking-ltd", "booking.Main"),
    ("Tickets High TD", "PROJECT-TICKET-HTD-BASE", "run3-GPT5.6Luna-tickets-htd", "tickets.Main"),
    ("Tickets Low TD", "PROJECT-TICKET-LTD-BASE", "run4-GPT5.6Luna-tickets-ltd", "tickets.Main"),
]

AI_RUNS = {
    ai_project: ROOT / "event-a" / "runs" / run_directory
    for ai_project, run_directory in {
        "run1-GPT5.6Luna-booking-htd": "run1_booking_high_29-10-2026_1800",
        "run2-GPT5.6Luna-booking-ltd": "run2_booking_low_29-10-2026_1900",
        "run3-GPT5.6Luna-tickets-htd": "run3_tickets_high_29-10-2026_1915",
        "run4-GPT5.6Luna-tickets-ltd": "run4_tickets_low_29-10-2026_1950",
    }.items()
}

BASELINE_RUNS = {
    "PROJECT-BOOKING-HTD-BASE": (
        BASELINE_SOURCE_ROOT / "booking" / "high_debt" / "booking",
        BASELINE_SOURCE_ROOT / "booking" / "ComputerClassRoom.java",
        "booking.Main",
    ),
    "PROJECT-BOOKING-LTD-BASE": (
        BASELINE_SOURCE_ROOT / "booking" / "low_debt" / "booking",
        BASELINE_SOURCE_ROOT / "booking" / "ComputerClassRoom.java",
        "booking.Main",
    ),
    "PROJECT-TICKET-HTD-BASE": (
        BASELINE_SOURCE_ROOT / "tickets" / "high_debt" / "tickets",
        BASELINE_SOURCE_ROOT / "tickets" / "TicketTypeSeasonalRestricted.java",
        "tickets.Main",
    ),
    "PROJECT-TICKET-LTD-BASE": (
        BASELINE_SOURCE_ROOT / "tickets" / "low_debt" / "tickets",
        BASELINE_SOURCE_ROOT / "tickets" / "TicketTypeSeasonalRestricted.java",
        "tickets.Main",
    ),
}


def read_csv_metrics(path: Path) -> dict[str, dict[str, int]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return {
            row["project_key"]: {
                key: int(float(row[key]))
                for key in ("code_smells", "duplicated_lines", "duplicated_blocks")
            }
            for row in csv.DictReader(file)
        }


def issue_file(project_key: str) -> Path:
    matches = list(STUDY.glob(f"**/{project_key}-issues.json"))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one issue export for {project_key}, found {len(matches)}")
    return matches[0]


def read_issues(project_key: str) -> list[dict[str, object]]:
    with issue_file(project_key).open(encoding="utf-8-sig") as file:
        return json.load(file)["issues"]


def count_explicit_rule_matches(issues: list[dict[str, object]], terms: tuple[str, ...]) -> int:
    return sum(
        any(term in f"{issue.get('rule', '')} {issue.get('message', '')}".lower() for term in terms)
        for issue in issues
    )


def validate_source(
    source_directory: Path,
    main_class: str,
    additional_source: Path | None = None,
) -> tuple[str, str]:
    javac = Path(os.environ.get("JAVA_HOME", "")) / "bin" / "javac.exe"
    java = Path(os.environ.get("JAVA_HOME", "")) / "bin" / "java.exe"

    if not javac.exists() or not java.exists():
        return "NOT_RUN_JDK_UNAVAILABLE", "JAVA_HOME must point to a JDK containing javac.exe and java.exe"

    with tempfile.TemporaryDirectory(prefix="frozen-validation-") as temporary_directory:
        output_directory = Path(temporary_directory)
        sources = [str(path) for path in source_directory.glob("*.java")]
        if additional_source is not None:
            sources.append(str(additional_source))
        compile_result = subprocess.run(
            [str(javac), "-d", str(output_directory), *sources],
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            return "FAIL", compile_result.stderr.strip()

        run_result = subprocess.run(
            [str(java), "-cp", str(output_directory), main_class],
            capture_output=True,
            text=True,
        )
        if run_result.returncode != 0:
            return (
                "COMPILE_PASS_RUNTIME_FAIL",
                run_result.stderr.strip() or run_result.stdout.strip(),
            )

    return "PASS", "javac compilation and package-qualified Main execution returned exit code 0"


def validate_ai_source(project_key: str, main_class: str) -> tuple[str, str]:
    return validate_source(AI_RUNS[project_key], main_class)


def validate_baseline_source(
    project_key: str, main_class: str
) -> tuple[str, str]:
    source_directory, additional_source, _ = BASELINE_RUNS[project_key]
    return validate_source(source_directory, main_class, additional_source)


def build_rows() -> list[dict[str, object]]:
    baseline = read_csv_metrics(BASELINE_METRICS)
    ai = read_csv_metrics(AI_METRICS)
    rows = []

    for scenario, baseline_project, ai_project, main_class in SCENARIOS:
        baseline_issues = read_issues(baseline_project)
        ai_issues = read_issues(ai_project)
        baseline_validation_status, baseline_validation_evidence = (
            validate_baseline_source(baseline_project, main_class)
        )
        validation_status, validation_evidence = validate_ai_source(ai_project, main_class)

        baseline_reuse = baseline[baseline_project]["duplicated_blocks"]
        ai_reuse = ai[ai_project]["duplicated_blocks"]
        baseline_naming = count_explicit_rule_matches(
            baseline_issues, ("naming", "class name", "method name", "variable name")
        )
        ai_naming = count_explicit_rule_matches(
            ai_issues, ("naming", "class name", "method name", "variable name")
        )

        rows.append(
            {
                "scenario": scenario,
                "baseline_project": baseline_project,
                "ai_project": ai_project,
                "baseline_code_smells": baseline[baseline_project]["code_smells"],
                "ai_code_smells": ai[ai_project]["code_smells"],
                "net_code_smell_difference": ai[ai_project]["code_smells"]
                - baseline[baseline_project]["code_smells"],
                "baseline_duplicated_blocks": baseline_reuse,
                "ai_duplicated_blocks": ai_reuse,
                "net_duplicated_blocks_difference": ai_reuse - baseline_reuse,
                "baseline_naming_issues": baseline_naming,
                "ai_naming_issues": ai_naming,
                "net_naming_issue_difference": ai_naming - baseline_naming,
                "ai_static_validation": validation_status,
                "ai_static_validation_evidence": validation_evidence,
                "baseline_static_validation": baseline_validation_status,
                "baseline_static_validation_evidence": baseline_validation_evidence,
            }
        )

    return rows


def write_csv(rows: list[dict[str, object]]) -> Path:
    path = OUTPUT / "frozen-replication-validation.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_graph(rows: list[dict[str, object]]) -> Path:
    labels = [row["scenario"] for row in rows]
    positions = range(len(labels))
    figure, axes = plt.subplots(3, 1, figsize=(11, 12))

    metrics = [
        ("Code smells", "baseline_code_smells", "ai_code_smells"),
        ("Duplicated blocks", "baseline_duplicated_blocks", "ai_duplicated_blocks"),
        ("Naming issues", "baseline_naming_issues", "ai_naming_issues"),
    ]
    width = 0.36

    for axis, (title, baseline_key, ai_key) in zip(axes, metrics):
        baseline = [row[baseline_key] for row in rows]
        ai = [row[ai_key] for row in rows]
        axis.bar([p - width / 2 for p in positions], baseline, width, label="Baseline", color="#6c757d")
        axis.bar([p + width / 2 for p in positions], ai, width, label="AI-generated", color="#1976d2")
        axis.set_title(title)
        axis.set_ylabel("Count")
        axis.set_xticks(list(positions), labels)
        axis.grid(axis="y", alpha=0.25)
        axis.legend()

    figure.suptitle("Frozen replication: baseline versus AI-generated validation measures")
    figure.tight_layout()
    path = OUTPUT / "frozen-replication-validation.png"
    figure.savefig(path, dpi=200)
    plt.close(figure)
    return path


def write_document(rows: list[dict[str, object]]) -> Path:
    path = ROOT / "FROZEN_REPLICATION.md"
    ai_validation_passes = sum(row["ai_static_validation"] == "PASS" for row in rows)
    lines = [
        "# Frozen replication record",
        "",
        "## Scope",
        "",
        "This record freezes the four-scenario comparison of the baseline and AI-generated Java projects.",
        "The source of truth is the saved SonarQube metrics and issue exports under `study/`.",
        "",
        "## Frozen procedure",
        "",
        "1. Match each baseline project to its corresponding AI project by scenario and debt level.",
        "2. Use SonarQube `code_smells` as the code-smell measure.",
        "3. Use SonarQube `duplicated_blocks` as the logic-reuse proxy. A value of zero means no duplicated blocks were reported; it does not prove semantic equivalence.",
        "4. Count naming issues only when the SonarQube rule or issue message explicitly identifies naming, a class name, method name, or variable name.",
        "5. Compile each baseline and AI source snapshot with `javac`, then execute its package-qualified `Main` class.",
        "",
        "## Results",
        "",
        "| Scenario | Baseline smells | AI smells | Net smells | Baseline duplicated blocks | AI duplicated blocks | Baseline naming issues | AI naming issues | Baseline validation | AI validation |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['scenario']} | {row['baseline_code_smells']} | {row['ai_code_smells']} | "
            f"{row['net_code_smell_difference']:+} | {row['baseline_duplicated_blocks']} | "
            f"{row['ai_duplicated_blocks']} | {row['baseline_naming_issues']} | "
            f"{row['ai_naming_issues']} | {row['baseline_static_validation']} | "
            f"{row['ai_static_validation']} |"
        )

    total_baseline = sum(row["baseline_code_smells"] for row in rows)
    total_ai = sum(row["ai_code_smells"] for row in rows)
    lines.extend(
        [
            "",
            f"Total code smells: baseline **{total_baseline}**, AI-generated **{total_ai}**, net **{total_ai - total_baseline:+}**.",
            f"AI static validation: **{ai_validation_passes}/{len(rows)}** scenarios passed compilation and execution.",
            "",
            "## Limitations",
            "",
            "- Baseline source was validated from the external Scenarios repository supplied for this task. Booking runtime validation is affected by the source fixture's hard-coded 2021 dates; the result is recorded separately from compilation.",
            "- The saved baseline and AI SonarQube exports report zero duplicated blocks for every scenario. This supports a zero structural-duplication result under this metric, not a proof that no logic was conceptually reused.",
            "- The naming count is zero where no issue explicitly matches the frozen naming terms. General code smells such as magic numbers are not silently reclassified as naming issues.",
            "- SonarQube project keys, timestamps, quality profile, and metric exports should remain unchanged for this record to be reproducible.",
            "",
            "## Output artifacts",
            "",
            "- `study/AI-Results/analysis/frozen-replication-validation.csv`",
            "- `study/AI-Results/analysis/frozen-replication-validation.png`",
            "- `FROZEN_REPLICATION.md`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    csv_path = write_csv(rows)
    graph_path = write_graph(rows)
    document_path = write_document(rows)
    print(f"Validation CSV: {csv_path}")
    print(f"Validation graph: {graph_path}")
    print(f"Frozen document: {document_path}")


if __name__ == "__main__":
    main()
