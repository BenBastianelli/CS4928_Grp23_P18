import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
BASELINE_FILE = ROOT / "study" / "Baseline" / "metrics-summary.csv"
AI_FILE = ROOT / "study" / "AI-Results" / "metrics-summary.csv"
OUTPUT_DIRECTORY = ROOT / "study" / "AI-Results" / "analysis"

SCENARIOS = [
    {
        "scenario": "Booking High TD",
        "category": "Booking",
        "debt_level": "High TD",
        "baseline_project": "PROJECT-BOOKING-HTD-BASE",
        "ai_project": "run1-GPT5.6Luna-booking-htd",
    },
    {
        "scenario": "Booking Low TD",
        "category": "Booking",
        "debt_level": "Low TD",
        "baseline_project": "PROJECT-BOOKING-LTD-BASE",
        "ai_project": "run2-GPT5.6Luna-booking-ltd",
    },
    {
        "scenario": "Tickets High TD",
        "category": "Tickets",
        "debt_level": "High TD",
        "baseline_project": "PROJECT-TICKET-HTD-BASE",
        "ai_project": "run3-GPT5.6Luna-tickets-htd",
    },
    {
        "scenario": "Tickets Low TD",
        "category": "Tickets",
        "debt_level": "Low TD",
        "baseline_project": "PROJECT-TICKET-LTD-BASE",
        "ai_project": "run4-GPT5.6Luna-tickets-ltd",
    },
]


def read_metrics(path: Path) -> dict[str, dict[str, int]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return {
            row["project_key"]: {
                "code_smells": int(row["code_smells"]),
            }
            for row in csv.DictReader(file)
        }


def build_comparison(
    baseline_metrics: dict[str, dict[str, int]],
    ai_metrics: dict[str, dict[str, int]],
) -> list[dict[str, object]]:
    comparison = []

    for scenario in SCENARIOS:
        baseline_project = scenario["baseline_project"]
        ai_project = scenario["ai_project"]

        if baseline_project not in baseline_metrics:
            raise KeyError(f"Missing baseline project: {baseline_project}")
        if ai_project not in ai_metrics:
            raise KeyError(f"Missing AI project: {ai_project}")

        baseline_smells = baseline_metrics[baseline_project]["code_smells"]
        ai_smells = ai_metrics[ai_project]["code_smells"]
        net_difference = ai_smells - baseline_smells

        comparison.append(
            {
                **scenario,
                "baseline_code_smells": baseline_smells,
                "ai_code_smells": ai_smells,
                "net_difference": net_difference,
                "percentage_change": (net_difference / baseline_smells) * 100,
            }
        )

    return comparison


def write_comparison_csv(comparison: list[dict[str, object]], path: Path) -> None:
    fieldnames = [
        "scenario",
        "category",
        "debt_level",
        "baseline_project",
        "ai_project",
        "baseline_code_smells",
        "ai_code_smells",
        "net_difference",
        "percentage_change",
    ]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comparison)


def create_graph(comparison: list[dict[str, object]], path: Path) -> None:
    labels = [row["scenario"] for row in comparison]
    baseline = [row["baseline_code_smells"] for row in comparison]
    ai = [row["ai_code_smells"] for row in comparison]
    differences = [row["net_difference"] for row in comparison]

    figure, (counts_axis, difference_axis) = plt.subplots(
        2,
        1,
        figsize=(11, 8),
        gridspec_kw={"height_ratios": [2, 1]},
    )

    positions = range(len(labels))
    width = 0.36

    counts_axis.bar(
        [position - width / 2 for position in positions],
        baseline,
        width,
        label="Baseline",
        color="#6c757d",
    )
    counts_axis.bar(
        [position + width / 2 for position in positions],
        ai,
        width,
        label="AI-generated",
        color="#1976d2",
    )
    counts_axis.set_ylabel("Code smells")
    counts_axis.set_title("Baseline vs AI-generated code smells")
    counts_axis.set_xticks(list(positions), labels)
    counts_axis.legend()
    counts_axis.grid(axis="y", alpha=0.25)

    for position, baseline_value, ai_value in zip(positions, baseline, ai):
        counts_axis.text(position - width / 2, baseline_value + 2, str(baseline_value), ha="center")
        counts_axis.text(position + width / 2, ai_value + 2, str(ai_value), ha="center")

    difference_axis.bar(labels, differences, color="#d95f02")
    difference_axis.axhline(0, color="black", linewidth=0.8)
    difference_axis.set_ylabel("Net difference")
    difference_axis.set_title("Net code smells introduced (AI - baseline)")
    difference_axis.grid(axis="y", alpha=0.25)

    for position, difference in zip(positions, differences):
        difference_axis.text(position, difference + 0.8, f"+{difference}", ha="center")

    figure.tight_layout()
    figure.savefig(path, dpi=200)
    plt.close(figure)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    baseline_metrics = read_metrics(BASELINE_FILE)
    ai_metrics = read_metrics(AI_FILE)
    comparison = build_comparison(baseline_metrics, ai_metrics)

    comparison_csv = OUTPUT_DIRECTORY / "code-smells-comparison.csv"
    graph_path = OUTPUT_DIRECTORY / "code-smells-baseline-vs-ai.png"

    write_comparison_csv(comparison, comparison_csv)
    create_graph(comparison, graph_path)

    total_baseline = sum(row["baseline_code_smells"] for row in comparison)
    total_ai = sum(row["ai_code_smells"] for row in comparison)
    total_difference = total_ai - total_baseline

    print(f"Total baseline code smells: {total_baseline}")
    print(f"Total AI-generated code smells: {total_ai}")
    print(f"Total net difference: +{total_difference}")
    print(f"Comparison saved to: {comparison_csv}")
    print(f"Graph saved to: {graph_path}")


if __name__ == "__main__":
    main()
