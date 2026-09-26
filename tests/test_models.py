import pytest
from sqlalchemy.exc import IntegrityError
from server.extensions import db
from server.models import Exercise, Workout, WorkoutExercise


def test_exercise_model_validations(app):
    with pytest.raises(ValueError):
        Exercise(name="  ", category="strength")
    with pytest.raises(ValueError):
        Exercise(name="Hop", category="dance")
    assert Exercise(name=" Hop ", category="CARDIO").category == "cardio"


def test_workout_model_validates_duration(app):
    with pytest.raises(ValueError):
        Workout(name="Bad", duration_minutes=0)


def test_workout_exercise_model_validations(app):
    with pytest.raises(ValueError):
        WorkoutExercise(sets=0, reps=5)
    with pytest.raises(ValueError):
        WorkoutExercise(sets=3, reps=5, order_index=-1)


def test_reps_or_duration_check_constraint_enforced_by_database(app):
    exercise = Exercise(name="Squat", category="strength")
    workout = Workout(name="Leg Day", duration_minutes=30)
    db.session.add_all([exercise, workout])
    db.session.commit()

    db.session.add(WorkoutExercise(workout_id=workout.id, exercise_id=exercise.id, sets=3))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_unique_exercise_name_enforced_by_database(app):
    db.session.add(Exercise(name="Squat", category="strength"))
    db.session.commit()
    db.session.add(Exercise(name="Squat", category="strength"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
