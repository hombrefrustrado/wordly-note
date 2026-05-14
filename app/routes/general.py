from flask import Blueprint, render_template, request
general = Blueprint("general", __name__)

@general.route("/", methods=['GET','POST'])
def dash_board():
    return render_template("index.html")

@general.route("/learn")
def learn():
    return "hello world"

@general.route("/login",methods=["GET", "POST"])
def logeacion():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        print(username)
        print(password)

        return "Login received"

@general.route("/register", methods=["GET","POST"])
def registracion():
    if request.method == 'GET':
        return render_template("register.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        accepted_terms = request.form.get("terms")

        if not accepted_terms:
            return "You must accept the terms and conditions", 400

        return "User registered"
    

