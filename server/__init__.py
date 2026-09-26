from flask import Flask
from server.config import Config
from server.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register every model on db.metadata so Alembic autogenerate can see them.
    from server import models  # noqa: F401

    return app
