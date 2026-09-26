def test_create_workout(client):
    resp = client.post("/workouts", json={"name": "Leg Day", "duration_minutes": 45})
    assert resp.status_code == 201
    assert resp.get_json()["duration_minutes"] == 45


def test_list_and_get_workout(client):
    created = client.post("/workouts", json={"name": "Push Day", "duration_minutes": 50}).get_json()
    assert len(client.get("/workouts").get_json()) == 1
    resp = client.get(f"/workouts/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["workout_exercises"] == []


def test_create_workout_rejects_non_positive_duration(client):
    resp = client.post("/workouts", json={"name": "Bad", "duration_minutes": 0})
    assert resp.status_code == 400


def test_create_workout_rejects_missing_name(client):
    resp = client.post("/workouts", json={"duration_minutes": 30})
    assert resp.status_code == 400
    assert "name" in resp.get_json()["errors"]


def test_create_workout_rejects_non_json_body(client):
    resp = client.post("/workouts", data="not json")
    assert resp.status_code == 400


def test_get_missing_workout_returns_404(client):
    assert client.get("/workouts/9999").status_code == 404


def test_delete_workout_cascades_workout_exercises(app, client):
    from server.models.workout_exercise import WorkoutExercise

    exercise = client.post("/exercises", json={"name": "Squat", "category": "strength"}).get_json()
    workout = client.post("/workouts", json={"name": "Leg Day", "duration_minutes": 30}).get_json()
    client.post(f"/workouts/{workout['id']}/exercises",
                json={"exercise_id": exercise["id"], "sets": 3, "reps": 10})
    assert WorkoutExercise.query.count() == 1

    resp = client.delete(f"/workouts/{workout['id']}")
    assert resp.status_code == 204
    assert client.get(f"/workouts/{workout['id']}").status_code == 404
    assert WorkoutExercise.query.count() == 0
    assert client.get(f"/exercises/{exercise['id']}").status_code == 200
