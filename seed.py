from datetime import date
from server import create_app
from server.extensions import db
from server.models.exercise import Exercise
from server.models.workout import Workout
from server.models.workout_exercise import WorkoutExercise

app = create_app()

with app.app_context():
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print("Seeding exercises...")
    push_up = Exercise(name="Push-Up", category="strength")
    squat = Exercise(name="Squat", category="strength")
    plank = Exercise(name="Plank", category="mobility")
    running = Exercise(name="Running", category="cardio", equipment_needed="Treadmill")
    db.session.add_all([push_up, squat, plank, running])
    db.session.commit()

    print("Seeding workouts...")
    leg_day = Workout(name="Leg Day", date=date.today(), duration_minutes=45, notes="Focus on form")
    full_body = Workout(name="Full Body Circuit", date=date.today(), duration_minutes=60)
    db.session.add_all([leg_day, full_body])
    db.session.commit()

    print("Linking exercises to workouts...")
    db.session.add_all([
        WorkoutExercise(workout_id=leg_day.id, exercise_id=squat.id, sets=4, reps=12, order_index=0),
        WorkoutExercise(workout_id=leg_day.id, exercise_id=plank.id, sets=3, duration_seconds=60, order_index=1),
        WorkoutExercise(workout_id=full_body.id, exercise_id=push_up.id, sets=3, reps=15, order_index=0),
        WorkoutExercise(workout_id=full_body.id, exercise_id=squat.id, sets=3, reps=10, order_index=1),
        WorkoutExercise(workout_id=full_body.id, exercise_id=running.id, sets=1, duration_seconds=900, order_index=2),
    ])
    db.session.commit()

    print(f"Done: {Exercise.query.count()} exercises, {Workout.query.count()} workouts, "
          f"{WorkoutExercise.query.count()} workout_exercise links.")
