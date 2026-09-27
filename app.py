import json
import os

from flask import Flask, jsonify, request, render_template

from ai import extract_resume_text, match_labs, chat, draft_email


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
    return render_template("index.html")

@app.route("/labs")
def labs_page():
    return render_template("index.html")


@app.route("/lab/<lab_id>")
def lab_page(lab_id):
    labs = load_labs()

    for lab in labs:
        if lab.get("id") == lab_id:
            return jsonify(lab)

    return jsonify({
        "error": "Lab not found"
    }), 404


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

    return jsonify({
        "error": "Lab not found"
    }), 404


@app.route("/api/match", methods=["POST"])
def api_match():
    resume_file = request.files.get("resume")
    interests = request.form.get("interests", "").strip()

    resume_bytes = b""
    resume_text = ""

    if resume_file and resume_file.filename:
        if not resume_file.filename.lower().endswith(".pdf"):
            return jsonify({
                "error": "Resume must be a PDF"
            }), 400

        resume_bytes = resume_file.read()

        if len(resume_bytes) > 5 * 1024 * 1024:
            return jsonify({
                "error": "Resume must be smaller than 5 MB"
            }), 400

    if not resume_bytes and not interests:
        return jsonify({
            "error": "Please provide a resume or interests"
        }), 400

    try:
        if resume_bytes:
            resume_text = extract_resume_text(resume_bytes)

        labs = load_labs()

        matches = match_labs(
            labs,
            resume_text,
            interests
        )

        return jsonify({
            "matches": matches,
            "resume_text": resume_text
        })

    except Exception as e:
        print("api_match failed:", e)

        return jsonify({
            "error": "Unable to generate matches"
        }), 500


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({
            "error": "Message is required"
        }), 400

    try:
        labs = load_labs()

        result = chat(
            labs,
            message,
            history
        )

        return jsonify(result)

    except Exception as e:
        print("api_chat failed:", e)

        return jsonify({
            "error": "Unable to generate chat response"
        }), 500


@app.route("/api/email", methods=["POST"])
def api_email():
    data = request.get_json(silent=True) or {}

    lab_id = data.get("lab_id", "").strip()
    resume_text = data.get("resume_text", "").strip()

    if not lab_id:
        return jsonify({
            "error": "Lab ID is required"
        }), 400

    labs = load_labs()

    lab = None

    for current_lab in labs:
        if current_lab.get("id") == lab_id:
            lab = current_lab
            break

    if lab is None:
        return jsonify({
            "error": "Lab not found"
        }), 404

    try:
        draft = draft_email(
            lab,
            resume_text
        )

        return jsonify({
            "draft": draft
        })

    except Exception as e:
        print("api_email failed:", e)

        return jsonify({
            "error": "Unable to generate email draft"
        }), 500


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
