
import json
from collections import Counter
from pathlib import Path

folder = Path(__file__).parent
rules_file = folder / ".manual_rules.json"

with open(rules_file, encoding="utf-8-sig") as f:
    rules = json.load(f)

for issues_file in folder.rglob("*_issues.json"):

    with open(issues_file, encoding="utf-8-sig") as f:
        data = json.load(f)

    # Support both a list of issues and SonarQube's API format
    if isinstance(data, list):
        issues = data
    elif isinstance(data, dict) and "issues" in data:
        issues = data["issues"]
    else:
        print(f"\nUnexpected JSON structure: {issues_file}")
        print("Top-level type:", type(data).__name__)
        if isinstance(data, dict):
            print("Available keys:", list(data.keys()))
        continue

    included = []
    excluded = []
    unknown = []

    for issue in issues:
        rule = issue.get("rule")

        if rule not in rules:
            unknown.append(issue)
        elif rules[rule]["ignored"]:
            excluded.append(issue)
        else:
            included.append(issue)

    output_file = issues_file.with_name(
        issues_file.stem.replace("_issues", "_filtered") + ".json"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(included, f, indent=2)

    print(f"\n{issues_file.name}")
    print("Raw issues:", len(issues))
    print("Included:", len(included))
    print("Excluded:", len(excluded))
    print("Unknown:", len(unknown))

    if unknown:
        print("Unknown rules:")
        for rule, count in Counter(
            issue.get("rule", "MISSING_RULE") for issue in unknown
        ).most_common():
            print(f"  {rule}: {count}")
