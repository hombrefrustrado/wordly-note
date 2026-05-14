from flask import Flask
from app.extensions import db
from app.routes.general import general
import os
from dotenv import load_dotenv


def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
        )
    


    load_dotenv()
    app.secret_key = os.getenv("secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        from app.models.language import Language
        default_languages = ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Korean", "Chinese"]
        for lang_name in default_languages:
            if not Language.query.filter_by(name=lang_name).first():
                db.session.add(Language(name=lang_name))
        db.session.commit()
    # blueprints
    app.register_blueprint(general)

    return app