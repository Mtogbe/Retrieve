import glob
import json
import re
import sys
import time
import ai

start = time.time()

# pick the data file, real labs by default
path = sys.argv[1] if len(sys.argv) > 1 else "data/labs.json"
with open(path, encoding="utf-8") as f:
    labs = json.load(f)
by_id = {str(lab.get("id")): lab for lab in labs}
print("loaded", len(labs), "records from", path)
print("match and email model:", ai.MODEL, "effort", ai.EFFORT)
print("chat model:", ai.CHAT_MODEL)

# tools never appear in lab data, so in a reason they must come from the resume
TOOLS = ["pytorch", "tensorflow", "xgboost", "scikit-learn", "sql", "duckdb",
         "tableau", "matplotlib", "pandas", "numpy", "java", "slurm"]

# placeholder values that mean the field is really missing
MISSING = {"", "not found", "n/a", "none", "not applicable"}


def real(value):
    # field text, or "" if missing or a placeholder
    text = str(value or "").strip()
    return "" if text.lower() in MISSING else text


def person(name):
    # name without titles and punctuation, for spotting the same person twice
    name = re.sub(r"\bdr\.?\s*", "", real(name).lower())
    if "," in name:
        last, first = name.split(",", 1)
        name = first + " " + last
    return " ".join(name.replace(".", " ").split())


def name_of(lab_id):
    # record name, or a loud warning if the id is fake
    lab = by_id.get(lab_id)
    return lab.get("name") if lab else "??? UNKNOWN ID " + lab_id


def check_tools(text, resume):
    # warn about tools that are not on this resume
    for tool in TOOLS:
        if tool in text.lower() and tool not in resume.lower():
            print("   WARNING", tool, "is not on this resume")


def check_email(email, lab):
    # warn about contact info, background claims, lacking claims, and wrong greeting
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", email) or re.search(r"\d{3}[\s.-]?\d{3}[\s.-]?\d{4}", email):
        print("WARNING contact info found in email")
    if re.search(r"\b(align\w*|fits?|match\w*) with (my|areas|what i)", email.lower()):
        print("WARNING email claims something about the student's background")
    if re.search(r"\b(do not|don't|have not|haven't) (yet )?(have|had)|\bno (formal |prior )?experience", email.lower()):
        print("WARNING email claims the student lacks something")
    expected = ai._greeting(lab)
    if expected not in email:
        print("WARNING greeting should be", expected)


# ===== data check =====
print("\n===== data check =====")
problems = 0
required = ["id", "name", "department", "research_areas", "source_url"]
seen_ids = {}
seen_sites = {}
seen_people = {}
for lab in labs:
    lab_id = str(lab.get("id"))
    kind = real(lab.get("record_type")) or "lab"
    for field in required:
        value = lab.get(field)
        if not value or (isinstance(value, str) and not real(value)):
            print("missing", field, "in", lab_id)
            problems += 1
    if not isinstance(lab.get("research_areas"), list):
        print("research_areas is not a list in", lab_id)
        problems += 1
    status = real(lab.get("accepting_students"))
    if status and status not in ("yes", "no", "unknown"):
        print("bad accepting_students in", lab_id, status)
        problems += 1
    email = real(lab.get("contact_email"))
    if email and "@" not in email:
        print("bad contact_email in", lab_id, email)
        problems += 1
    if lab_id in seen_ids:
        print("duplicate id", lab_id)
        problems += 1
    seen_ids[lab_id] = True
    # programs share department pages on purpose, so only check other records
    site = real(lab.get("website"))
    if site and kind != "research_program":
        if site in seen_sites:
            print("same website for", seen_sites[site], "and", lab_id, site)
            problems += 1
        else:
            seen_sites[site] = lab_id
    # the same person as independent research and as a lab lead is a duplicate
    who = person(lab.get("pi_name"))
    if who and kind != "research_program":
        if who in seen_people:
            other_id, other_kind = seen_people[who]
            if "individual_research" in (kind, other_kind):
                print("same person listed twice:", other_id, "and", lab_id, "-", who)
                problems += 1
            else:
                print("note:", who, "leads both", other_id, "and", lab_id)
        else:
            seen_people[who] = (lab_id, kind)
print(problems, "problems found")

# ===== resumes =====
print("\n===== extract_resume_text =====")
resumes = []
for pdf in sorted(glob.glob("test_resumes/*.pdf")):
    with open(pdf, "rb") as f:
        text = ai.extract_resume_text(f.read())
    print(pdf, len(text), "chars")
    resumes.append((pdf, text))
if not resumes:
    print("no pdf in test_resumes")

# ===== filter =====
print("\n===== filter_by_interests =====")
for q in ["machine learning", "robotics", "security", "quantum", "cooking", ""]:
    result = ai.filter_by_interests(labs, q)
    print(repr(q), "->", len(result), "records:", [lab.get("name") for lab in result[:5]])

# ===== match =====
print("\n===== match_labs =====")
first_matches = {}
for pdf, text in resumes:
    print("\n-- resume + interests:", pdf)
    matches = ai.match_labs(labs, text, "machine learning and data")
    for m in matches:
        print("-", name_of(m["lab_id"]))
        print("  ", m["reason"])
        check_tools(m["reason"], text)
    if not matches:
        print("(no matches)")
    else:
        print(len(matches), "matches")
        first_matches[pdf] = matches[0]["lab_id"]

print("\n-- interests only: brain computer interfaces")
for m in ai.match_labs(labs, "", "brain computer interfaces"):
    print("-", name_of(m["lab_id"]))
    print("  ", m["reason"])

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
    print("links:", [name_of(i) for i in result["lab_ids"]])

# ===== email =====
print("\n===== draft_email =====")
for pdf, text in resumes:
    lab_id = first_matches.get(pdf, str(labs[0].get("id")))
    print("\n-- with resume", pdf, "for", name_of(lab_id))
    email = ai.draft_email(by_id[lab_id], text)
    print(email)
    print("-- words:", len(email.split()))
    check_email(email, by_id[lab_id])
    check_tools(email, text)

lab_id = str(labs[0].get("id"))
print("\n-- no resume for", name_of(lab_id))
email = ai.draft_email(by_id[lab_id], "")
print(email)
print("-- words:", len(email.split()))
check_email(email, by_id[lab_id])

print("\ntotal time:", round(time.time() - start, 1), "seconds")