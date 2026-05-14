from app.extensions import db

class Word(db.Model):
    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key = True)
    original = db.Column(db.String(80), nullable = False)
    meaning = db.Column(db.String(80), nullable = False)

    difficulty = db.Column(db.Integer, nullable=True)
    topic = db.Column(db.String(80), nullable = True)

    # relacion 1:N con usuario
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # relacion 1:N con language
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id"), nullable=False)