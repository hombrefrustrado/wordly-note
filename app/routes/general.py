import json
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.extensions import db
from app.models import User, Word, UserLanguage, Language
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session

general = Blueprint("general", __name__)

@general.route("/", methods=['GET'])
def dash_board():
    if not session.get("user_id"):
        return render_template("index.html", user=None)
    
    user = User.query.get(session.get("user_id"))
    if not user:
        session.clear()
        return render_template("index.html", user=None)
        
    all_languages = Language.query.all()
    user_languages = user.languages
    words = Word.query.filter_by(user_id=user.id).all()

    return render_template(
        "index.html",
        user=user,
        all_languages=all_languages,
        user_languages=user_languages,
        words=words
    )

@general.route("/learn")
def learn():
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("general.login"))
    user = User.query.get(user_id)
    
    language_id = request.args.get("language_id")
    topic = request.args.get("topic")
    
    if language_id and topic:
        words = Word.query.filter_by(user_id=user_id, language_id=language_id, topic=topic).all()
        return render_template("flashcards.html", words=words, language_id=language_id, topic=topic)
        
    user_languages = user.languages
    words = Word.query.filter_by(user_id=user_id).all()
    
    topics_by_language = {}
    for w in words:
        if w.topic:
            lang_id = str(w.language_id)
            if lang_id not in topics_by_language:
                topics_by_language[lang_id] = set()
            topics_by_language[lang_id].add(w.topic)
            
    for lang_id in topics_by_language:
        topics_by_language[lang_id] = list(topics_by_language[lang_id])
    
    return render_template("learn.html", user_languages=user_languages, topics_by_language=topics_by_language)

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
        
        if len(password) < 10:
            return "Password must be at least 10 characters long", 400

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

@general.route("/language/add", methods=["POST"])
def add_language():
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("general.login"))
    
    language_id = request.form.get("language_id")
    if language_id:
        existing = UserLanguage.query.filter_by(user_id=user_id, language_id=language_id).first()
        if not existing:
            new_ul = UserLanguage(user_id=user_id, language_id=language_id)
            db.session.add(new_ul)
            db.session.commit()
            
            if request.headers.get("Accept") == "application/json":
                language = Language.query.get(language_id)
                return jsonify({"success": True, "language": {"id": language.id, "name": language.name}})
        else:
            if request.headers.get("Accept") == "application/json":
                return jsonify({"success": False, "error": "Language already added"}), 400
                
    if request.headers.get("Accept") == "application/json":
        return jsonify({"success": False, "error": "Invalid input"}), 400
    return redirect(url_for("general.dash_board"))

@general.route("/language/remove", methods=["POST"])
def remove_language():
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("general.login"))
    
    language_id = request.form.get("language_id")
    if language_id:
        UserLanguage.query.filter_by(user_id=user_id, language_id=language_id).delete()
        Word.query.filter_by(user_id=user_id, language_id=language_id).delete()
        db.session.commit()
        
        if request.headers.get("Accept") == "application/json":
            return jsonify({"success": True})
            
    if request.headers.get("Accept") == "application/json":
        return jsonify({"success": False, "error": "Invalid input"}), 400
    return redirect(url_for("general.dash_board"))

@general.route("/word/add", methods=["POST"])
def add_word():
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("general.login"))
    
    original = request.form.get("original")
    meaning = request.form.get("meaning")
    topic = request.form.get("topic")
    language_id = request.form.get("language_id")
    
    if original and meaning and language_id:
        existing = Word.query.filter_by(
            original=original, 
            meaning=meaning, 
            language_id=language_id, 
            user_id=user_id
        ).first()
        
        if not existing:
            word = Word(original=original, meaning=meaning, topic=topic, language_id=language_id, user_id=user_id, difficulty=1)
            db.session.add(word)
            db.session.commit()
            
            if request.headers.get("Accept") == "application/json":
                return jsonify({
                    "success": True, 
                    "word": {
                        "id": word.id, 
                        "original": word.original, 
                        "meaning": word.meaning, 
                        "topic": word.topic, 
                        "language_name": word.language.name
                    }
                })
        else:
            if request.headers.get("Accept") == "application/json":
                return jsonify({"success": False, "error": "Word already exists"}), 400
                
    if request.headers.get("Accept") == "application/json":
        return jsonify({"success": False, "error": "Invalid input"}), 400
        
    return redirect(url_for("general.dash_board"))

@general.route("/word/delete/<int:word_id>", methods=["POST"])
def delete_word(word_id):
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("general.login"))
    
    Word.query.filter_by(id=word_id, user_id=user_id).delete()
    db.session.commit()
    
    if request.headers.get("Accept") == "application/json":
        return jsonify({"success": True})
        
    return redirect(url_for("general.dash_board"))

@general.route("/word/import", methods=["POST"])
def import_words():
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("general.login"))
    
    language_id = request.form.get("language_id")
    file = request.files.get("json_file")
    
    if not file or not language_id:
        return "Missing file or language", 400
        
    try:
        data = json.load(file)
        if not isinstance(data, list):
            return "JSON must be a list of objects", 400
            
        for item in data:
            original = item.get("original")
            meaning = item.get("meaning")
            topic = item.get("topic", "General")
            if original and meaning:
                existing = Word.query.filter_by(
                    original=original, 
                    meaning=meaning, 
                    language_id=language_id, 
                    user_id=user_id
                ).first()
                
                if not existing:
                    word = Word(original=original, meaning=meaning, topic=topic, language_id=language_id, user_id=user_id, difficulty=1)
                    db.session.add(word)
        db.session.commit()
    except Exception as e:
        return f"Error processing JSON file: {str(e)}", 400
        
    return redirect(url_for("general.dash_board"))

@general.route("/api/swipe", methods=["POST"])
def swipe():
    user_id = session.get("user_id")
    if not user_id: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    action = data.get("action")
    
    user = User.query.get(user_id)
    if action == 'right':
        user.xp += 10
    else:
        user.xp += 2
        
    db.session.commit()
    return jsonify({"success": True, "xp": user.xp})