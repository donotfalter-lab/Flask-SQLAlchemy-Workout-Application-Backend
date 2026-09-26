def _setup(client, exercise_name="Plank", category="mobility"):
    exercise = client.post("/exercises", json={"name": exercise_name, "category": category}).get_json()
    workout = client.post("/workouts", json={"name": "Core Day", "duration_minutes": 20}).get_json()
    return exercise, workout


def test_add_exercise_to_workout(client):
    exercise, workout = _setup(client)

    resp = client.post(f"/workouts/{workout['id']}/exercises",
                       json={"exercise_id": exercise["id"], "sets": 3, "duration_seconds": 45})
    assert resp.status_code == 201
    assert resp.get_json()["exercise"]["name"] == "Plank"


def test_workout_nests_exercises_in_order(client):
    exercise, workout = _setup(client)
    squat = client.post("/exercises", json={"name": "Squat", "category": "strength"}).get_json()
    client.post(f"/workouts/{workout['id']}/exercises",
                json={"exercise_id": squat["id"], "sets": 3, "reps": 10, "order_index": 1})
    client.post(f"/workouts/{workout['id']}/exercises",
                json={"exercise_id": exercise["id"], "sets": 3, "duration_seconds": 30, "order_index": 0})

    nested = client.get(f"/workouts/{workout['id']}").get_json()["workout_exercises"]
    assert [we["exercise"]["name"] for we in nested] == ["Plank", "Squat"]


def test_add_exercise_requires_reps_or_duration(client):
    exercise, workout = _setup(client, "Row", "strength")

    resp = client.post(f"/workouts/{workout['id']}/exercises",
                       json={"exercise_id": exercise["id"], "sets": 3})
    assert resp.status_code == 400
    assert "_schema" in resp.get_json()["errors"]


def test_add_exercise_rejects_non_positive_sets(client):
    exercise, workout = _setup(client, "Row", "strength")

    resp = client.post(f"/workouts/{workout['id']}/exercises",
                       json={"exercise_id": exercise["id"], "sets": 0, "reps": 10})
    assert resp.status_code == 400


def test_add_exercise_to_missing_workout_returns_404(client):
    exercise = client.post("/exercises", json={"name": "Row", "category": "strength"}).get_json()
    resp = client.post("/workouts/9999/exercises", json={"exercise_id": exercise["id"], "sets": 3, "reps": 10})
    assert resp.status_code == 404


def test_add_missing_exercise_to_workout_returns_404(client):
    _, workout = _setup(client)
    resp = client.post(f"/workouts/{workout['id']}/exercises", json={"exercise_id": 9999, "sets": 3, "reps": 10})
    assert resp.status_code == 404


def test_delete_exercise_cascades_but_keeps_workout(client):
    exercise, workout = _setup(client)
    client.post(f"/workouts/{workout['id']}/exercises",
                json={"exercise_id": exercise["id"], "sets": 3, "duration_seconds": 45})

    assert client.delete(f"/exercises/{exercise['id']}").status_code == 204
    resp = client.get(f"/workouts/{workout['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["workout_exercises"] == []
