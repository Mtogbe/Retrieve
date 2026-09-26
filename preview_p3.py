# Temporary preview server for Person 3. NOT the real app.py. Do not commit.
import json
import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Used only if data/fake_labs.json is missing
SAMPLE_LABS = [
    {
        "id": "sample-001",
        "name": "Sample Lab A",
        "pi_name": "Dr. Sample",
        "department": "Computer Science",
        "research_areas": ["machine learning", "climate"],
        "description": "Placeholder lab for testing the page layout.",
        "accepting_students": "yes",
        "source_url": "https://example.com",
    },
    {
        "id": "sample-002",
        "name": "Sample Lab B",
        "department": "Public Health",
        "research_areas": ["epidemiology", "health data"],
        "source_url": "https://example.com",
    },
]


def load_labs():
    path = os.path.join(BASE_DIR, "data", "labs.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Using built-in sample labs because:", e)
        return SAMPLE_LABS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/labs")
def api_labs():
    q = request.args.get("q", "").strip().lower()
    dept = request.args.get("department", "").strip().lower()
    area = request.args.get("area", "").strip().lower()

    results = []
    for lab in load_labs():
        areas = lab.get("research_areas") or []
        text = " ".join([
            lab.get("name") or "",
            lab.get("pi_name") or "",
            lab.get("description") or "",
            " ".join(areas),
        ]).lower()
        if q and q not in text:
            continue
        if dept and (lab.get("department") or "").lower() != dept:
            continue
        if area and not any(area in a.lower() for a in areas):
            continue
        results.append(lab)
    return jsonify(results)


@app.route("/api/labs/<lab_id>")
def api_lab(lab_id):
    for lab in load_labs():
        if lab.get("id") == lab_id:
            return jsonify(lab)
    return jsonify({"error": "Lab not found"}), 404

@app.route("/")
def labs_page():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
