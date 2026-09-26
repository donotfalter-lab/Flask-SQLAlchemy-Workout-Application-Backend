from server.extensions import db
from sqlalchemy.orm import validates

ALLOWED_CATEGORIES = {"strength", "cardio", "mobility", "balance", "flexibility"}


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.String, nullable=True)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.CheckConstraint("length(trim(name)) > 0", name="exercise_name_not_blank"),
    )

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name must not be blank.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if value is None or value.lower() not in ALLOWED_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}.")
        return value.lower()

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"
