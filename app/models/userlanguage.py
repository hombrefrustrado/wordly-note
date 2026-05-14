from app.extensions import db

class UserLanguage(db.Model):
    __tablename__ = "user_language"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id"), primary_key=True)

    level = db.Column(db.Integer, default=1)
    progress = db.Column(db.Integer, default=0)