from server.extensions import db
from sqlalchemy.orm import validates


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    __table_args__ = (
        db.CheckConstraint("sets > 0", name="workout_exercise_sets_positive"),
        db.CheckConstraint(
            "(reps IS NOT NULL AND reps >= 0) OR (duration_seconds IS NOT NULL AND duration_seconds > 0)",
            name="workout_exercise_reps_or_duration_required",
        ),
    )

    @validates("sets")
    def validate_sets(self, key, value):
        if value is None or value <= 0:
            raise ValueError("sets must be a positive integer.")
        return value

    @validates("order_index")
    def validate_order_index(self, key, value):
        if value is not None and value < 0:
            raise ValueError("order_index cannot be negative.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>"
