import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)
def load_labs():
    real_data = os.path.join("data", "labs.json")
    fake_data = os.path.join("data", "fake_labs.json")

    if os.path.exists(real_data):
        file_path = real_data
    else:
        file_path = fake_data

    with open(file_path, "r", encoding="utf-8") as file:
        labs = json.load(file)

    return labs

@app.route("/")
def home():
    return "Retrieve backend is running!"


@app.route("/lab/<lab_id>")
def lab_page(lab_id):
    labs = load_labs()

    for lab in labs:
        if lab.get("id") == lab_id:
            return jsonify(lab)

    return jsonify({"error": "Lab not found"}), 404


@app.route("/match")
def match_page():
    return "Retrieve match page"


@app.route("/api/labs")
def get_labs():
    labs = load_labs()

    q = request.args.get("q", "").lower()
    department = request.args.get("department", "").lower()
    area = request.args.get("area", "").lower()

    results = []

    for lab in labs:
        name = lab.get("name", "").lower()
        pi_name = lab.get("pi_name", "").lower()
        description = lab.get("description", "").lower()
        research_areas = lab.get("research_areas", [])

        research_text = " ".join(research_areas).lower()

        matches_q = (
            not q
            or q in name
            or q in pi_name
            or q in description
            or q in research_text
        )

        matches_department = (
            not department
            or department in lab.get("department", "").lower()
        )

        matches_area = (
            not area
            or area in research_text
        )

        if matches_q and matches_department and matches_area:
            results.append(lab)

    return jsonify(results)


@app.route("/api/labs/<lab_id>")
def get_lab(lab_id):
    labs = load_labs()

    for lab in labs:
        if lab.get("id") == lab_id:
            return jsonify(lab)

    return jsonify({"error": "Lab not found"}), 404


@app.route("/api/match", methods=["POST"])
def api_match():
    return jsonify({
        "matches": [],
        "resume_text": ""
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    return jsonify({
        "reply": "Chat is not connected yet.",
        "lab_ids": []
    })


@app.route("/api/email", methods=["POST"])
def api_email():
    return jsonify({
        "draft": "Email drafting is not connected yet."
    })


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)