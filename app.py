from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def dash_board():
    return render_template("index.html")

@app.route("/learn")
def learn():
    return "hello world"

@app.route("/login")
def logeacion():
    return "hello world!"


@app.route("/register")
def registracion():
    return "hello world!"



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
