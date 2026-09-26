from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from server.extensions import db
from server.models.workout import Workout
from server.schemas.workout_schema import workout_schema, workouts_schema

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")


@workouts_bp.get("")
def get_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@workouts_bp.get("/<int:id>")
def get_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return jsonify({"error": f"Workout {id} not found."}), 404
    return jsonify(workout_schema.dump(workout)), 200


@workouts_bp.post("")
def create_workout():
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"error": "Request body must be JSON."}), 400
    try:
        data = workout_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Could not create workout; check constraints."}), 400

    return jsonify(workout_schema.dump(workout)), 201


@workouts_bp.delete("/<int:id>")
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return jsonify({"error": f"Workout {id} not found."}), 404
    db.session.delete(workout)  # cascades to its WorkoutExercise rows
    db.session.commit()
    return "", 204
