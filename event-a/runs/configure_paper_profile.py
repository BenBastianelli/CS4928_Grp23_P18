
import json
import os
import requests
import difflib
from pathlib import Path
from requests.auth import HTTPBasicAuth

# =====================================================
# CONFIGURATION
# =====================================================

BASE_URL = "http://localhost:9000"
PROFILE_NAME = "Paper_Manual_Rules"
LANGUAGE = "java"

PROJECTS = [
    # Baselines
    "run-baseline-ticket-htd",
    "run-baseline-booking-ltd",
    "run-baseline-booking-htd",
    "run-baseline-ticket-ltd",

    # Copilot results
    "run1-GPT5.6Luna-booking-htd",
    "run2-GPT5.6Luna-booking-ltd",
    "run3-GPT5.6Luna-tickets-htd",
    "run4-GPT5.6Luna-tickets-ltd",
]

FOLDER = Path(__file__).parent
RULES_FILE = FOLDER / ".manual_rules.json"

# =====================================================
# AUTHENTICATION
# =====================================================

token = os.environ.get("SONAR_TOKEN")

if not token:
    raise SystemExit("SONAR_TOKEN is not set.")

session = requests.Session()
session.auth = HTTPBasicAuth(token, "")
session.headers.update({"Accept": "application/json"})


def api(method, endpoint, **kwargs):
    response = session.request(
        method,
        f"{BASE_URL}/api/{endpoint}",
        timeout=60,
        **kwargs
    )

    if not response.ok:
        raise RuntimeError(
            f"API error {response.status_code} at {endpoint}: "
            f"{response.text}"
        )

    if response.text.strip():
        return response.json()

    return {}


# =====================================================
# LOAD PAPER RULE CONFIGURATION
# =====================================================

with open(RULES_FILE, encoding="utf-8-sig") as f:
    rules = json.load(f)

selected_rules = {
    rule_id: config
    for rule_id, config in rules.items()
    if config.get("ignored") is False
}

ignored_rules = {
    rule_id
    for rule_id, config in rules.items()
    if config.get("ignored") is True
}

print("=" * 60)
print("PAPER RULE CONFIGURATION")
print("=" * 60)
print("Total rules:", len(rules))
print("Selected:", len(selected_rules))
print("Ignored:", len(ignored_rules))


# =====================================================
# DISCOVER ALL AVAILABLE SONAR RULES
# =====================================================

print("\nSearching installed SonarQube rule repositories...")

available_rules = {}
page = 1

while True:
    result = api(
        "GET",
        "rules/search",
        params={
            "ps": 500,
            "p": page,
        }
    )

    for rule in result.get("rules", []):
        available_rules[rule["key"]] = rule

    total = result.get("total", 0)

    if page * 500 >= total:
        break

    page += 1
print("\nAVAILABLE CHECKSTYLE RULES")

for rule_id, info in sorted(available_rules.items()):
    if rule_id.startswith("checkstyle:"):
        print(rule_id, "-", info.get("name", ""))
print("Rules discovered:", len(available_rules))

# Match exact IDs and check language.

available_selected = []
missing_rules = []
wrong_language = []

for rule_id in selected_rules:

    rule_info = available_rules.get(rule_id)

    if rule_info is None:
        missing_rules.append(rule_id)

    elif rule_info.get("lang") != LANGUAGE:
        wrong_language.append(
            (rule_id, rule_info.get("lang"))
        )

    else:
        available_selected.append(rule_id)


print("\nRULE AVAILABILITY")
print("-" * 40)
print("Selected in paper:", len(selected_rules))
print("Available for Java:", len(available_selected))
print("Missing:", len(missing_rules))
print("Wrong language:", len(wrong_language))


if missing_rules:
    print("\nMissing exact rule IDs:")

    for rule_id in missing_rules:

        print("\n ", rule_id)

        suffix = rule_id.split(":", 1)[-1]

        alternatives = [
            key for key in available_rules
            if key.endswith(":" + suffix)
        ]

        if alternatives:
            print("  Possible alternatives:", alternatives)


if wrong_language:
    print("\nRules found under another language:")

    for rule_id, language in wrong_language:
        print(f"  {rule_id}: {language}")


# =====================================================
# CREATE OR REUSE QUALITY PROFILE
# =====================================================

print("\nChecking Quality Profiles...")

profiles = api(
    "GET",
    "qualityprofiles/search",
    params={"language": LANGUAGE}
)

existing = next(
    (
        profile
        for profile in profiles.get("profiles", [])
        if profile["name"] == PROFILE_NAME
    ),
    None
)

if existing:

    profile_key = existing["key"]

    print("Using existing profile:", PROFILE_NAME)

else:

    created = api(
        "POST",
        "qualityprofiles/create",
        data={
            "name": PROFILE_NAME,
            "language": LANGUAGE,
        }
    )

    profile_key = created["profile"]["key"]

    print("Created profile:", PROFILE_NAME)


# =====================================================
# ACTIVATE AVAILABLE SELECTED RULES
# =====================================================

print("\nActivating selected rules...")

activated = []
activation_errors = []

for rule_id in available_selected:

    config = selected_rules[rule_id]

    severity = config.get(
        "severity", "MAJOR"
    ).upper()

    if severity not in {
        "INFO", "MINOR", "MAJOR", "CRITICAL", "BLOCKER"
    }:
        severity = "MAJOR"

    try:

        api(
            "POST",
            "qualityprofiles/activate_rule",
            data={
                "key": profile_key,
                "rule": rule_id,
                "severity": severity,
            }
        )

        activated.append(rule_id)

        print(f"Activated: {rule_id} ({severity})")

    except RuntimeError as error:

        activation_errors.append(rule_id)

        print(f"FAILED: {rule_id}")
        print(error)


# =====================================================
# DISCOVER SONARQUBE PROJECTS
# =====================================================

print("\nDiscovering SonarQube projects...")

sonar_projects = {}
page = 1

while True:

    result = api(
        "GET",
        "projects/search",
        params={
            "ps": 500,
            "p": page,
        }
    )

    for project in result.get("components", []):
        sonar_projects[project["key"]] = project

    total = result.get("paging", {}).get("total", 0)

    if page * 500 >= total:
        break

    page += 1

print("Projects visible to token:", len(sonar_projects))


# =====================================================
# ASSIGN PROFILE TO ALL EIGHT PROJECTS
# =====================================================

print("\nAssigning Quality Profile...")

assigned = []
not_found = []
assignment_errors = []

for project in PROJECTS:

    if project not in sonar_projects:

        not_found.append(project)

        print(f"\nPROJECT NOT FOUND: {project}")

        suggestions = difflib.get_close_matches(
            project,
            list(sonar_projects.keys()),
            n=3,
            cutoff=0.3
        )

        if suggestions:
            print("Possible project keys:")

            for suggestion in suggestions:
                print(" ", suggestion)

        continue

    try:

        api(
            "POST",
            "qualityprofiles/add_project",
            data={
                "language": LANGUAGE,
                "qualityProfile": PROFILE_NAME,
                "project": project,
            }
        )

        assigned.append(project)

        print("Assigned:", project)

    except RuntimeError as error:

        assignment_errors.append(project)

        print(f"ASSIGNMENT FAILED: {project}")
        print(error)


# =====================================================
# FINAL SUMMARY
# =====================================================

print("\n")
print("=" * 60)
print("CONFIGURATION SUMMARY")
print("=" * 60)

print("Profile:", PROFILE_NAME)
print("Profile key:", profile_key)

print("\nRules:")
print("Selected by paper:", len(selected_rules))
print("Available for Java:", len(available_selected))
print("Activated successfully:", len(activated))
print("Missing:", len(missing_rules))
print("Activation failures:", len(activation_errors))

print("\nProjects:")
print("Expected:", len(PROJECTS))
print("Assigned:", len(assigned))
print("Not found:", len(not_found))
print("Assignment failures:", len(assignment_errors))

print("\nConfiguration process finished.")
