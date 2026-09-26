from marshmallow import Schema, fields, validate

ALLOWED_CATEGORIES = ["strength", "cardio", "mobility", "balance", "flexibility"]


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.OneOf(ALLOWED_CATEGORIES))
    equipment_needed = fields.Str(required=False, allow_none=True)


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
