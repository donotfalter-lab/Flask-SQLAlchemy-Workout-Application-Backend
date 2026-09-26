from marshmallow import Schema, fields, validate
from server.schemas.workout_exercise_schema import WorkoutExerciseSchema


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    date = fields.Date(required=False)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(required=False, allow_none=True)

    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)


workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
