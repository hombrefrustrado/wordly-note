from flask import Flask
from app.extensions import db
from app.routes.general import general

def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    db.init_app(app)

    # blueprints
    app.register_blueprint(general)

    return app