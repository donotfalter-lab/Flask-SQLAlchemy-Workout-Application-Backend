from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from server.extensions import db
from server.models.workout import Workout
from server.models.exercise import Exercise
from server.models.workout_exercise import WorkoutExercise
from server.schemas.workout_exercise_schema import workout_exercise_schema

workout_exercises_bp = Blueprint("workout_exercises", __name__, url_prefix="/workouts")


@workout_exercises_bp.post("/<int:workout_id>/exercises")
def add_exercise_to_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": f"Workout {workout_id} not found."}), 404

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"error": "Request body must be JSON."}), 400

    try:
        data = workout_exercise_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    exercise = db.session.get(Exercise, data["exercise_id"])
    if exercise is None:
        return jsonify({"error": f"Exercise {data['exercise_id']} not found."}), 404

    try:
        workout_exercise = WorkoutExercise(
            workout_id=workout.id,
            exercise_id=exercise.id,
            sets=data["sets"],
            reps=data.get("reps"),
            duration_seconds=data.get("duration_seconds"),
            order_index=data.get("order_index", 0),
        )
        db.session.add(workout_exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Could not add exercise to workout; check constraints."}), 400

    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201
