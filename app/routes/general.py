from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import db
from app.models import User, Word, UserLanguage
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session

general = Blueprint("general", __name__)

@general.route("/", methods=['GET','POST'])
def dash_board():
    return render_template(
        "index.html",
        username=session.get("username")
    )

@general.route("/learn")
def learn():
    return render_template("learn.html", username= session.get("username"))

@general.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return "Missing credentials", 400
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return "User not found", 404
        if not check_password_hash(user.password, password):
            return "Incorrect password", 401

        session["user_id"] = user.id
        session["username"] = user.username

        return redirect(url_for("general.dash_board"))

@general.route("/register", methods=["GET","POST"])
def registration():
    if request.method == 'GET':
        return render_template("register.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return "Missing credentials", 400
        

        accepted_terms = request.form.get("terms")
        # comprobar si respondio los terminos y condiciones
        if not accepted_terms:
            return "You must accept the terms and conditions", 400
        
        # vamos a ver si alguien existe con ese usuario, en caso afirmativo saltamos status code o algo lol.
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
                return "User already exists", 409
        # hashear contraseña
        hashed_password = generate_password_hash(password)

        # crear usuario
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("general.login"))
    

@general.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("general.dash_board"))

@general.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("general.login"))
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for("general.login"))
        
    if request.method == "POST":
        # Handle account deletion and cascade manually for safety
        Word.query.filter_by(user_id=user.id).delete()
        UserLanguage.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return redirect(url_for("general.dash_board"))
        
    return render_template("profile.html", user=user)