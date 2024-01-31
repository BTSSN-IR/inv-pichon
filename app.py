from flask import Flask, request, url_for, redirect, render_template
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('home'))

    return render_template('login.html')