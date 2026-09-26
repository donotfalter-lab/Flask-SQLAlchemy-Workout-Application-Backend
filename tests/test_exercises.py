def test_create_exercise(client):
    resp = client.post("/exercises", json={"name": "Deadlift", "category": "strength"})
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Deadlift"


def test_list_and_get_exercise(client):
    created = client.post("/exercises", json={"name": "Lunge", "category": "strength"}).get_json()
    assert len(client.get("/exercises").get_json()) == 1
    resp = client.get(f"/exercises/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Lunge"


def test_create_exercise_rejects_blank_name(client):
    resp = client.post("/exercises", json={"name": "", "category": "strength"})
    assert resp.status_code == 400


def test_create_exercise_rejects_whitespace_name_via_model_validation(client):
    resp = client.post("/exercises", json={"name": "   ", "category": "strength"})
    assert resp.status_code == 400
    assert "blank" in resp.get_json()["error"]


def test_create_exercise_rejects_unknown_category(client):
    resp = client.post("/exercises", json={"name": "Yoga", "category": "dance"})
    assert resp.status_code == 400
    assert "category" in resp.get_json()["errors"]


def test_create_exercise_rejects_duplicate_name(client):
    client.post("/exercises", json={"name": "Deadlift", "category": "strength"})
    resp = client.post("/exercises", json={"name": "Deadlift", "category": "strength"})
    assert resp.status_code == 400


def test_delete_exercise(client):
    created = client.post("/exercises", json={"name": "Row", "category": "strength"}).get_json()
    resp = client.delete(f"/exercises/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/exercises/{created['id']}").status_code == 404


def test_delete_missing_exercise_returns_404(client):
    assert client.delete("/exercises/9999").status_code == 404
