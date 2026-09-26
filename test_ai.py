import glob
import json
import re
import sys
import ai

# pick the data file, real labs by default
path = sys.argv[1] if len(sys.argv) > 1 else "data/labs.json"
with open(path, encoding="utf-8") as f:
    labs = json.load(f)
by_id = {str(lab.get("id")): lab for lab in labs}
print("loaded", len(labs), "labs from", path)


def name_of(lab_id):
    # lab name, or a loud warning if the id is fake
    lab = by_id.get(lab_id)
    return lab.get("name") if lab else "??? UNKNOWN ID " + lab_id


# ===== data check =====
print("\n===== data check =====")
problems = 0
required = ["id", "name", "department", "research_areas", "source_url"]
seen_ids = {}
seen_sites = {}
for lab in labs:
    lab_id = str(lab.get("id"))
    for field in required:
        if not lab.get(field):
            print("missing", field, "in", lab_id)
            problems += 1
    if not isinstance(lab.get("research_areas"), list):
        print("research_areas is not a list in", lab_id)
        problems += 1
    if lab.get("accepting_students") not in (None, "yes", "no", "unknown"):
        print("bad accepting_students in", lab_id, lab.get("accepting_students"))
        problems += 1
    email = lab.get("contact_email")
    if email and "@" not in str(email):
        print("bad contact_email in", lab_id, email)
        problems += 1
    if lab_id in seen_ids:
        print("duplicate id", lab_id)
        problems += 1
    seen_ids[lab_id] = True
    site = lab.get("website")
    if site and site in seen_sites:
        print("same website for", seen_sites[site], "and", lab_id, site)
        problems += 1
    elif site:
        seen_sites[site] = lab_id
print(problems, "problems found")

# ===== resume =====
print("\n===== extract_resume_text =====")
pdfs = sorted(glob.glob("test_resumes/*.pdf"))
resume = ""
if pdfs:
    with open(pdfs[0], "rb") as f:
        resume = ai.extract_resume_text(f.read())
    print(pdfs[0], len(resume), "chars")
else:
    print("no pdf in test_resumes, using empty resume")

# ===== filter =====
print("\n===== filter_by_interests =====")
for q in ["machine learning", "robotics", "security", "quantum", "cooking", ""]:
    result = ai.filter_by_interests(labs, q)
    print(repr(q), "->", len(result), "labs:", [lab.get("name") for lab in result[:5]])

# ===== match =====
print("\n===== match_labs =====")
first_match = None
for title, res, interests in [
    ("resume + interests", resume, "machine learning and data"),
    ("interests only", "", "brain computer interfaces"),
]:
    print("\n--", title)
    matches = ai.match_labs(labs, res, interests)
    for m in matches:
        print("-", name_of(m["lab_id"]))
        print("  ", m["reason"])
    if not matches:
        print("(no matches)")
    if matches and first_match is None:
        first_match = matches[0]["lab_id"]

# ===== chat =====
print("\n===== chat =====")
for q in [
    "Which labs work on robotics?",
    "Who runs DAMS and what is their email?",
    "Are any labs working on quantum computing?",
    "Is the CORAL lab accepting students?",
]:
    result = ai.chat(labs, q, [])
    print("\nQ:", q)
    print("A:", result["reply"])
    print("labs:", [name_of(i) for i in result["lab_ids"]])

# ===== email =====
print("\n===== draft_email =====")
lab_id = first_match or str(labs[0].get("id"))
for title, res in [("with resume", resume), ("no resume", "")]:
    print("\n--", title, "for", name_of(lab_id))
    email = ai.draft_email(by_id[lab_id], res)
    print(email)
    print("-- words:", len(email.split()))
    # contact info should never make it into the email
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", email) or re.search(r"\d{3}[\s.-]?\d{3}[\s.-]?\d{4}", email):
        print("WARNING contact info found in email")