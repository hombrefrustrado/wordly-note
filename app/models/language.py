from app.extensions import db

class Language(db.Model):
    __tablename__ = "languages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    words = db.relationship("Word", backref="language", lazy=True)

    users = db.relationship(
        "User",
        secondary="user_language",
        back_populates="languages"
    )