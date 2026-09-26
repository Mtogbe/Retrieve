"""Checks data/labs.json for problems. Run this before every push.
Usage: python scraper/validate_labs.py
"""
import json
import os
import re

LABS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "labs.json")
TAGS_PATH = os.path.join(os.path.dirname(__file__), "tags.txt")

REQUIRED_FIELDS = ["id", "name", "department", "research_areas", "source_url"]
VALID_ACCEPTING = {"yes", "no", "unknown"}
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_tags(path):
    if not os.path.exists(path):
        print(f"WARNING: {path} not found, skipping tag validation")
        return None
    with open(path) as f:
        return set(line.strip().lower() for line in f if line.strip())


def check_url(value):
    # returns True if it looks like a real URL, not empty/placeholder
    if not value or not isinstance(value, str):
        return False
    if "PASTE_ACTUAL_URL_HERE" in value or "example.com" in value:
        return False
    return bool(URL_PATTERN.match(value.strip()))


def validate(labs, valid_tags):
    problems = []
    seen_ids = set()

    for i, lab in enumerate(labs):
        label = lab.get("id", f"[entry {i}, no id]")

        # required fields present and non-empty
        for field in REQUIRED_FIELDS:
            value = lab.get(field)
            if value is None or value == "" or value == []:
                problems.append(f"{label}: missing required field '{field}'")

        # unique id
        lab_id = lab.get("id")
        if lab_id:
            if lab_id in seen_ids:
                problems.append(f"{label}: duplicate id '{lab_id}'")
            seen_ids.add(lab_id)

        # valid tags
        if valid_tags is not None:
            for tag in lab.get("research_areas", []):
                if tag.lower() not in valid_tags:
                    problems.append(f"{label}: tag '{tag}' not in tags.txt")

        # valid source_url (required)
        source_url = lab.get("source_url")
        if source_url and not check_url(source_url):
            problems.append(f"{label}: source_url looks invalid: '{source_url}'")

        # valid website (optional field, only check if present)
        website = lab.get("website")
        if website and not check_url(website):
            problems.append(f"{label}: website looks invalid: '{website}'")

        # accepting_students must be yes/no/unknown if present
        accepting = lab.get("accepting_students")
        if accepting is not None and accepting not in VALID_ACCEPTING:
            problems.append(
                f"{label}: accepting_students '{accepting}' must be yes, no, or unknown"
            )

    return problems


def main():
    labs = load_json(LABS_PATH)
    valid_tags = load_tags(TAGS_PATH)

    print(f"Checking {len(labs)} labs in {LABS_PATH}")
    problems = validate(labs, valid_tags)

    if not problems:
        print("All good. No problems found.")
    else:
        print(f"\nFound {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  - {p}")


if __name__ == "__main__":
    main()