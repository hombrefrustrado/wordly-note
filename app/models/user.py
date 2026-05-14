from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    xp = db.Column(db.BigInteger, nullable=False, default=0)

    # relacion 1:N
    words = db.relationship("Word", backref="user", lazy=True)

    languages = db.relationship(
        "Language",
        secondary="user_language",
        back_populates="users"
    )

