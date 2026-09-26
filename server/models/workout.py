from datetime import date as date_cls
from server.extensions import db
from sqlalchemy.orm import validates


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date_cls.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String, nullable=True)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order_index",
    )

    __table_args__ = (
        db.CheckConstraint("duration_minutes > 0", name="workout_duration_positive"),
    )

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Workout name must not be blank.")
        return value.strip()

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if value is None or value <= 0:
            raise ValueError("duration_minutes must be a positive integer.")
        return value

    def __repr__(self):
        return f"<Workout {self.id}: {self.name}>"
