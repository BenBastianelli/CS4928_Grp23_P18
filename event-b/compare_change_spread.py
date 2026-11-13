import csv
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_ROOT = Path(r"D:\Projects\CS4928\Event_A_repo\Scenarios")
OUTPUT = ROOT / "event-b" / "change-spread.csv"

COMPARISONS = (
    {
        "scenario": "Booking high-debt",
        "baseline": BASELINE_ROOT / "booking" / "high_debt" / "booking",
        "additional_baseline": BASELINE_ROOT / "booking" / "ComputerClassRoom.java",
        "event_a": ROOT / "event-a" / "runs" / "run1_booking_high_29-10-2026_1800",
        "event_b": ROOT / "event-b" / "modernised-snapshots" / "booking",
        "main_class": "booking.Main",
    },
    {
        "scenario": "Tickets high-debt",
        "baseline": BASELINE_ROOT / "tickets" / "high_debt" / "tickets",
        "additional_baseline": BASELINE_ROOT / "tickets" / "TicketTypeSeasonalRestricted.java",
        "event_a": ROOT / "event-a" / "runs" / "run3_tickets_high_29-10-2026_1915",
        "event_b": ROOT / "event-b" / "modernised-snapshots" / "tickets",
        "main_class": "tickets.Main",
    },
)

CONTROLLED_COMPARISONS = (
    {
        "scenario": "Booking modernised controlled reproduction",
        "baseline": ROOT
        / "event-b"
        / "controlled-reproduction"
        / "modernised-before"
        / "booking",
        "candidate": ROOT
        / "event-b"
        / "controlled-reproduction"
        / "modernised-after"
        / "booking",
        "main_class": "booking.Main",
    },
    {
        "scenario": "Tickets modernised controlled reproduction",
        "baseline": ROOT
        / "event-b"
        / "controlled-reproduction"
        / "modernised-before"
        / "tickets",
        "candidate": ROOT
        / "event-b"
        / "controlled-reproduction"
        / "modernised-after"
        / "tickets",
        "main_class": "tickets.Main",
    },
)


def source_files(directory: Path, additional_file: Path | None = None) -> dict[str, Path]:
    files = {path.name: path for path in directory.glob("*.java")}
    if additional_file is not None:
        files[additional_file.name] = additional_file
    return files


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_sources(
    baseline_directory: Path,
    candidate_directory: Path,
    additional_baseline: Path,
) -> dict[str, object]:
    baseline = source_files(baseline_directory, additional_baseline)
    candidate = source_files(candidate_directory)
    names = sorted(set(baseline) | set(candidate))
    added = sorted(name for name in names if name not in baseline)
    removed = sorted(name for name in names if name not in candidate)
    modified = sorted(
        name
        for name in names
        if name in baseline
        and name in candidate
        and digest(baseline[name]) != digest(candidate[name])
    )
    return {
        "baseline_file_count": len(baseline),
        "candidate_file_count": len(candidate),
        "files_changed": len(added) + len(removed) + len(modified),
        "files_added": len(added),
        "files_removed": len(removed),
        "files_modified": len(modified),
        "changed_files": "; ".join(added + removed + modified),
    }


def validation_status(
    directory: Path,
    main_class: str,
    additional_baseline: Path | None,
) -> str:
    java_home = os.environ.get("JAVA_HOME")
    javac = (
        str(Path(java_home) / "bin" / "javac.exe")
        if java_home and (Path(java_home) / "bin" / "javac.exe").exists()
        else shutil.which("javac")
    )
    java = (
        str(Path(java_home) / "bin" / "java.exe")
        if java_home and (Path(java_home) / "bin" / "java.exe").exists()
        else shutil.which("java")
    )
    if javac is None or java is None:
        return "NOT_RUN_JDK_UNAVAILABLE"

    with tempfile.TemporaryDirectory(prefix="event-b-validation-") as output:
        output_directory = Path(output)
        sources = [str(path) for path in directory.glob("*.java")]
        if additional_baseline is not None and additional_baseline.name not in {
            path.name for path in directory.glob("*.java")
        }:
            sources.append(str(additional_baseline))
        compile_result = subprocess.run(
            [javac, "-d", str(output_directory), *sources],
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            return "COMPILE_FAIL"
        run_result = subprocess.run(
            [java, "-cp", str(output_directory), main_class],
            capture_output=True,
            text=True,
        )
        return "PASS" if run_result.returncode == 0 else "RUNTIME_FAIL"


def build_rows() -> list[dict[str, object]]:
    rows = []
    for comparison in COMPARISONS:
        for state, directory in (
            ("Event A AI-generated", comparison["event_a"]),
            ("Event B modernised", comparison["event_b"]),
        ):
            change = compare_sources(
                comparison["baseline"],
                directory,
                comparison["additional_baseline"],
            )
            rows.append(
                {
                    "scenario": comparison["scenario"],
                    "state": state,
                    **change,
                    "build_validation": validation_status(
                        directory,
                        comparison["main_class"],
                        comparison["additional_baseline"],
                    ),
                }
            )
    for comparison in CONTROLLED_COMPARISONS:
        change = compare_sources(
            comparison["baseline"],
            comparison["candidate"],
            None,
        )
        rows.append(
            {
                "scenario": comparison["scenario"],
                "state": "Event B controlled reproduction",
                **change,
                "build_validation": validation_status(
                    comparison["candidate"],
                    comparison["main_class"],
                    None,
                ),
            }
        )
    return rows


def main() -> None:
    rows = build_rows()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Change-spread comparison: {OUTPUT}")


if __name__ == "__main__":
    main()
