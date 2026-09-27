"""Checks data/labs.json for problems. Run this before every push.
Usage: python scraper/validate_labs.py
"""
import json
import os
import re

LABS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "labs.json")
TAGS_PATH = os.path.join(os.path.dirname(__file__), "tags.txt")

# Fields required on every entry, regardless of which section it's in.
# NOTE: research_areas is intentionally NOT in here - a lab/person/program with
# no verifiable tags yet is expected to carry research_areas: ["not found"],
# which is a valid placeholder, not an error.
REQUIRED_FIELDS = ["id", "department", "source_url"]
VALID_ACCEPTING = {"yes", "no", "unknown", "not found"}
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
NOT_FOUND = "not found"

# Sections we expect in data/labs.json. Each maps to the fields that section
# must have filled in (beyond REQUIRED_FIELDS) to count as "complete" for
# that record type - missing ones are reported as warnings, not hard errors,
# since "not found" / blank is an intentional placeholder in this dataset.
SECTIONS = {
    "labs": ["name", "pi_name"],
    "individual_research": ["pi_name"],
    "research_programs": ["name"],
}

# When data/labs.json is a flat list, each entry may carry a "record_type"
# field ("lab" / "individual_research" / "research_program") saying which of
# the above rule sets applies to it. Falls back to "labs" rules if absent
# (e.g. your original flat schema, before record_type existed).
RECORD_TYPE_TO_SECTION = {
    "lab": "labs",
    "individual_research": "individual_research",
    "research_program": "research_programs",
}


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
    if value.strip().lower() == NOT_FOUND:
        return False
    if "PASTE_ACTUAL_URL_HERE" in value or "example.com" in value:
        return False
    return bool(URL_PATTERN.match(value.strip()))


def validate_entry(entry, label, section_fields, valid_tags, seen_ids):
    problems = []

    # required fields present and non-empty (blank/"not found" counts as present,
    # since this dataset uses that as an intentional placeholder)
    for field in REQUIRED_FIELDS:
        value = entry.get(field)
        if value is None or value == "" or value == []:
            problems.append(f"{label}: missing required field '{field}'")

    # section-specific fields: warn (not error) if left as "not found"/blank
    for field in section_fields:
        value = entry.get(field)
        if value is None or value == "" or (isinstance(value, str) and value.strip().lower() == NOT_FOUND):
            problems.append(f"{label}: '{field}' is blank/not found (ok if unverified, otherwise fill in)")

    # unique id across the whole file
    entry_id = entry.get("id")
    if entry_id:
        if entry_id in seen_ids:
            problems.append(f"{label}: duplicate id '{entry_id}' (ids must be unique across labs/individual_research/research_programs)")
        seen_ids.add(entry_id)

    # research_areas: warn (not error) if left as the "not found" placeholder,
    # and otherwise check each tag against the controlled vocabulary
    tags = entry.get("research_areas", [])
    if not tags:
        problems.append(f"{label}: 'research_areas' is empty (use [\"not found\"] as the placeholder instead of [])")
    elif tags == [NOT_FOUND]:
        problems.append(f"{label}: 'research_areas' is 'not found' (ok if unverified, otherwise fill in)")
    elif valid_tags is not None:
        for tag in tags:
            if tag.lower() != NOT_FOUND and tag.lower() not in valid_tags:
                problems.append(f"{label}: tag '{tag}' not in tags.txt")

    # valid source_url (required, but "not found" is allowed as a placeholder)
    source_url = entry.get("source_url")
    if source_url and source_url.strip().lower() != NOT_FOUND and not check_url(source_url) and not source_url.startswith("web_scraping_document"):
        problems.append(f"{label}: source_url looks invalid: '{source_url}'")

    # valid website (optional field, only check if present and not a placeholder)
    website = entry.get("website")
    if website and website.strip().lower() != NOT_FOUND and not check_url(website):
        problems.append(f"{label}: website looks invalid: '{website}'")

    # valid program_website (optional field, same rule as website)
    program_website = entry.get("program_website")
    if program_website and program_website.strip().lower() != NOT_FOUND and not check_url(program_website):
        problems.append(f"{label}: program_website looks invalid: '{program_website}'")

    # accepting_students must be yes/no/unknown/not found if present
    accepting = entry.get("accepting_students")
    if accepting is not None and accepting not in VALID_ACCEPTING:
        problems.append(
            f"{label}: accepting_students '{accepting}' must be yes, no, unknown, or not found"
        )

    return problems


def validate(data, valid_tags):
    problems = []
    seen_ids = set()
    counts = {}

    if isinstance(data, list):
        # a flat list: each entry's own "record_type" (if present) decides
        # which rule set applies to it; entries with no record_type fall
        # back to the old flat "labs" schema rules.
        for i, entry in enumerate(data):
            label = entry.get("id", f"[entry {i}, no id]") if isinstance(entry, dict) else f"[entry {i} is not an object]"
            if not isinstance(entry, dict):
                problems.append(f"{label}: expected an object, got {type(entry).__name__}")
                counts["labs"] = counts.get("labs", 0) + 1
                continue
            record_type = entry.get("record_type")
            section = RECORD_TYPE_TO_SECTION.get(record_type, "labs")
            counts[section] = counts.get(section, 0) + 1
            problems.extend(validate_entry(entry, label, SECTIONS[section], valid_tags, seen_ids))
        return problems, counts

    if not isinstance(data, dict):
        problems.append(f"Top-level JSON must be an object with 'labs'/'individual_research'/'research_programs' keys or a list; got {type(data).__name__}")
        return problems, counts

    known_sections = set(SECTIONS)
    unknown_sections = set(data) - known_sections
    for section in unknown_sections:
        problems.append(f"Unrecognized top-level key '{section}' (expected one of {sorted(known_sections)})")

    for section, section_fields in SECTIONS.items():
        entries = data.get(section, [])
        if not isinstance(entries, list):
            problems.append(f"'{section}' should be a list, got {type(entries).__name__}")
            continue
        counts[section] = len(entries)
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                problems.append(f"{section}[{i}]: expected an object, got {type(entry).__name__}")
                continue
            label = f"{section}/{entry.get('id', f'[entry {i}, no id]')}"
            problems.extend(validate_entry(entry, label, section_fields, valid_tags, seen_ids))

    return problems, counts


def main():
    data = load_json(LABS_PATH)
    valid_tags = load_tags(TAGS_PATH)

    problems, counts = validate(data, valid_tags)

    total = sum(counts.values())
    breakdown = ", ".join(f"{n} {section}" for section, n in counts.items())
    print(f"Checking {total} entries in {LABS_PATH} ({breakdown})")

    if not problems:
        print("All good. No problems found.")
    else:
        print(f"\nFound {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  - {p}")


if __name__ == "__main__":
    main()