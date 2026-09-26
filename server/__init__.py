from flask import Flask
from server.config import Config
from server.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.sort_keys = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Register every model on db.metadata so Alembic autogenerate can see them.
    from server import models  # noqa: F401

    from server.routes.workouts import workouts_bp
    from server.routes.exercises import exercises_bp
    from server.routes.workout_exercises import workout_exercises_bp

    app.register_blueprint(workouts_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(workout_exercises_bp)

    from server.errors import register_error_handlers
    register_error_handlers(app)

    return app
