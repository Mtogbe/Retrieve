import json
import os
from ai import filter_by_interests

labs = [
    {"id": "t-001", "name": "Climate AI Lab", "department": "Computer Science",
     "research_areas": ["machine learning", "climate"],
     "description": "We use machine learning to forecast air quality.",
     "source_url": "https://example.com"},
    {"id": "t-002", "name": "Robotics Lab", "department": "Mechanical Engineering",
     "research_areas": ["robotics", "computer vision"],
     "source_url": "https://example.com"},
    {"id": "t-003", "name": "Marine Biology Lab", "department": "Biology",
     "research_areas": ["marine ecology"], "description": None,
     "source_url": "https://example.com"},
    {"id": "t-004", "name": "Mystery Lab", "department": "Physics",
     "source_url": "https://example.com"},
]

tests = [
    "machine learning and climate",
    "robot vision",
    "AI",
    "I'm interested in marine research",
    "cooking",
    "",
]

for q in tests:
    result = filter_by_interests(labs, q)
    print(repr(q), "->", [lab["name"] for lab in result])

# also run on fake labs if person 2 has added them
path = os.path.join("data", "fake_labs.json")
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        fake = json.load(f)
    result = filter_by_interests(fake, "machine learning")
    print("fake_labs 'machine learning' ->", [lab.get("name") for lab in result])
else:
    print("no data/fake_labs.json yet, skipped")
    