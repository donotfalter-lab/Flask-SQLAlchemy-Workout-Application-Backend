from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from server.schemas.exercise_schema import ExerciseSchema


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(required=True)
    sets = fields.Int(required=True, validate=validate.Range(min=1))
    reps = fields.Int(required=False, allow_none=True, validate=validate.Range(min=0))
    duration_seconds = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    order_index = fields.Int(required=False, load_default=0, validate=validate.Range(min=0))

    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates_schema
    def validate_reps_or_duration(self, data, **kwargs):
        if data.get("reps") is None and data.get("duration_seconds") is None:
            raise ValidationError(
                "Provide either reps or duration_seconds.", field_name="_schema"
            )


workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)
