from app import app


passed = 0
failed = 0


def check(name, condition):
    global passed
    global failed

    if condition:
        print("[PASS]", name)
        passed += 1
    else:
        print("[FAIL]", name)
        failed += 1


def run_tests():
    client = app.test_client()

    # home page
    response = client.get("/")
    check("GET /", response.status_code == 200)

    # get all labs
    response = client.get("/api/labs")
    labs = response.get_json()

    check(
        "GET /api/labs",
        response.status_code == 200 and isinstance(labs, list)
    )

    if not labs:
        print("[FAIL] No labs available for remaining tests")
        return

    first_lab = labs[0]
    lab_id = first_lab.get("id")
    lab_name = first_lab.get("name", "")
    department = first_lab.get("department", "")
    research_areas = first_lab.get("research_areas", [])

    # get one lab
    response = client.get("/api/labs/" + lab_id)
    data = response.get_json()

    check(
        "GET /api/labs/<id>",
        response.status_code == 200
        and data.get("id") == lab_id
    )

    # invalid lab id
    response = client.get("/api/labs/not-a-real-lab")

    check(
        "GET invalid lab returns 404",
        response.status_code == 404
    )

    # lab page
    response = client.get("/lab/" + lab_id)

    check(
        "GET /lab/<id>",
        response.status_code == 200
    )

    # match page
    response = client.get("/match")

    check(
        "GET /match",
        response.status_code == 200
    )

    # search by name
    search_word = lab_name.split()[0]

    response = client.get(
        "/api/labs?q=" + search_word
    )

    results = response.get_json()

    check(
        "Search labs with q",
        response.status_code == 200
        and len(results) > 0
    )

    # filter by department
    response = client.get(
        "/api/labs",
        query_string={
            "department": department
        }
    )

    results = response.get_json()

    check(
        "Filter labs by department",
        response.status_code == 200
        and len(results) > 0
    )

    # filter by research area
    if research_areas:
        area = research_areas[0]

        response = client.get(
            "/api/labs",
            query_string={
                "area": area
            }
        )

        results = response.get_json()

        check(
            "Filter labs by area",
            response.status_code == 200
            and len(results) > 0
        )

    # match with nothing should fail
    response = client.post(
        "/api/match",
        data={}
    )

    check(
        "POST /api/match empty request",
        response.status_code == 400
    )

    # match using interests
    if research_areas:
        interests = research_areas[0]
    else:
        interests = "computer science"

    response = client.post(
        "/api/match",
        data={
            "interests": interests
        }
    )

    data = response.get_json()

    check(
        "POST /api/match",
        response.status_code == 200
        and "matches" in data
        and "resume_text" in data
    )

    # chat with no message should fail
    response = client.post(
        "/api/chat",
        json={}
    )

    check(
        "POST /api/chat empty message",
        response.status_code == 400
    )

    # chat normally
    response = client.post(
        "/api/chat",
        json={
            "message": "What research labs are available?",
            "history": []
        }
    )

    data = response.get_json()

    check(
        "POST /api/chat",
        response.status_code == 200
        and "reply" in data
        and "lab_ids" in data
    )

    # email with no lab id should fail
    response = client.post(
        "/api/email",
        json={}
    )

    check(
        "POST /api/email missing lab id",
        response.status_code == 400
    )

    # email with invalid lab id
    response = client.post(
        "/api/email",
        json={
            "lab_id": "not-a-real-lab",
            "resume_text": ""
        }
    )

    check(
        "POST /api/email invalid lab",
        response.status_code == 404
    )

    # email normally
    response = client.post(
        "/api/email",
        json={
            "lab_id": lab_id,
            "resume_text": "Student interested in research."
        }
    )

    data = response.get_json()

    check(
        "POST /api/email",
        response.status_code == 200
        and "draft" in data
    )

    print()
    print("Tests passed:", passed)
    print("Tests failed:", failed)

    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")


if __name__ == "__main__":
    run_tests()