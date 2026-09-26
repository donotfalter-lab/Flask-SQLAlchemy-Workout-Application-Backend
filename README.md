# Workout Tracker API

## Description
A Flask + SQLAlchemy + Marshmallow backend API for a workout-tracking application used by
personal trainers. Trainers can create reusable exercises, build workouts, and attach exercises
to a workout with the sets/reps or duration performed. Built for the Module 24 Summative Lab
("Relational Databases – Flask SQLAlchemy Workout Application Backend").

## Tech Stack
- Python 3.12
- Flask 2.2.2 / Flask-Migrate 3.1.0 / Flask-SQLAlchemy 3.0.3 / Werkzeug 2.2.2
- Marshmallow 3.20.1
- SQLite (dev), pytest (tests)

## Project Structure
```
server/
├── __init__.py          application factory (create_app)
├── app.py               entry point used by `flask run`
├── config.py            Config / TestConfig
├── extensions.py        db + migrate singletons, constraint naming convention
├── errors.py            JSON error handlers
├── models/              Workout, Exercise, WorkoutExercise
├── schemas/             Marshmallow schemas
└── routes/              one blueprint per resource
migrations/              Alembic migrations (Flask-Migrate)
tests/                   pytest suite
seed.py                  sample data
```

## Data Model
- **Exercise** — a reusable movement (name, category, optional equipment). Name is unique.
  Category is one of `strength`, `cardio`, `mobility`, `balance`, `flexibility`.
- **Workout** — one training session (name, date, duration in minutes, optional notes).
  `date` defaults to today.
- **WorkoutExercise** — the association object joining a Workout and an Exercise for one
  session, carrying `sets`, `reps` and/or `duration_seconds`, and an `order_index`. Each row
  requires either reps or duration_seconds (enforced at both the schema and database level).

Relationships:
- `Workout` 1 → many `WorkoutExercise` (ordered by `order_index`; deleting a workout deletes its rows)
- `Exercise` 1 → many `WorkoutExercise` (deleting an exercise deletes its rows; workouts are kept)

There is intentionally no direct Workout ↔ Exercise relationship; everything goes through
`WorkoutExercise`. Serialization nests in one direction only
(`WorkoutSchema` → `WorkoutExerciseSchema` → `ExerciseSchema`), so there is no circular
reference and no need for `exclude=` or `lambda:` forward references.

## Installation
```bash
git clone <repo-url>
cd alchemy-workout
pipenv install --dev
pipenv shell
flask db upgrade head
python seed.py
```
`FLASK_APP=server.app` and the port are set in `.flaskenv` (loaded via python-dotenv), so no
`export` is needed.

## Running the App
```bash
flask run
```
The API runs at http://127.0.0.1:5555.

## Running Tests
```bash
pytest -v
```
Tests use an in-memory SQLite database and never touch `app.db`.

## API Endpoints

| Method | Route | Description | Success |
|---|---|---|---|
| GET | /workouts | List all workouts, each with its nested exercises | 200 |
| GET | /workouts/&lt;id&gt; | Get one workout with its nested exercises | 200 |
| POST | /workouts | Create a workout. Body: `{name, duration_minutes, date?, notes?}` | 201 |
| DELETE | /workouts/&lt;id&gt; | Delete a workout (also deletes its workout_exercise rows) | 204 |
| GET | /exercises | List all exercises | 200 |
| GET | /exercises/&lt;id&gt; | Get one exercise | 200 |
| POST | /exercises | Create an exercise. Body: `{name, category, equipment_needed?}` | 201 |
| DELETE | /exercises/&lt;id&gt; | Delete an exercise (also deletes its workout_exercise rows) | 204 |
| POST | /workouts/&lt;workout_id&gt;/exercises | Add an exercise to a workout. Body: `{exercise_id, sets, reps?, duration_seconds?, order_index?}` — one of `reps`/`duration_seconds` is required | 201 |

Errors are always JSON: `400` for invalid input (`{"errors": {...}}` from schema validation, or
`{"error": "..."}` from model validation / database constraints) and `404` for a missing workout
or exercise.

### Example
```bash
curl -X POST http://127.0.0.1:5555/workouts/1/exercises \
  -H "Content-Type: application/json" \
  -d '{"exercise_id": 2, "sets": 4, "reps": 12}'
```
```json
{
  "id": 6,
  "workout_id": 1,
  "exercise_id": 2,
  "sets": 4,
  "reps": 12,
  "duration_seconds": null,
  "order_index": 0,
  "exercise": {"id": 2, "name": "Squat", "category": "strength", "equipment_needed": null}
}
```

## Validation Summary
Validation is layered: **schema → model → database**. Bad requests are rejected with a clean 400
by the schema first; model `@validates` methods protect any code path that bypasses the schema
(e.g. `seed.py`); table constraints are the final safety net.

- **Table constraints:** `NOT NULL` on required columns, unique exercise names, and named
  `CheckConstraint`s for non-blank exercise names, positive workout duration, positive sets,
  and a combined check that every workout_exercise row has reps or a duration.
- **Model validations (`@validates`):** blank-name rejection and category whitelist on
  `Exercise`; blank-name rejection and positive duration on `Workout`; positive sets and
  non-negative order on `WorkoutExercise`.
- **Schema validations (Marshmallow):** required fields, `Length`/`Range` limits, a category
  `OneOf`, and a `@validates_schema` rule requiring reps or duration on the join.
