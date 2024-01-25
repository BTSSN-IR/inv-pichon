from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return "<p>Hello, World!</p>"

@app.route("/login")
def login():
    return render_template('login.html')