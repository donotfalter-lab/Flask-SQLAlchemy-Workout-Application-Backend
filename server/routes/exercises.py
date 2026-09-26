from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from server.extensions import db
from server.models.exercise import Exercise
from server.schemas.exercise_schema import exercise_schema, exercises_schema

exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercises_bp.get("")
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@exercises_bp.get("/<int:id>")
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        return jsonify({"error": f"Exercise {id} not found."}), 404
    return jsonify(exercise_schema.dump(exercise)), 200


@exercises_bp.post("")
def create_exercise():
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"error": "Request body must be JSON."}), 400
    try:
        data = exercise_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Could not create exercise; it may already exist."}), 400

    return jsonify(exercise_schema.dump(exercise)), 201


@exercises_bp.delete("/<int:id>")
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        return jsonify({"error": f"Exercise {id} not found."}), 404
    db.session.delete(exercise)  # cascades to its WorkoutExercise rows
    db.session.commit()
    return "", 204
