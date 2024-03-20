from flask import Flask, request, url_for, redirect, render_template, flash
import os
import mysql.connector
import sqlite3

global loggedin
loggedin = False
global utilisateur_connecte
utilisateur_connecte = 'invité'
app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

#import pyzbar.pyzbar
#import PIL.Image

from werkzeug.utils import secure_filename

@app.route("/")
def home():
    if loggedin == True:
        print('Logged in')
    return render_template('home.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/add_user")
def add_user():
    return render_template('add_user.html')

@app.route("/add_user_form", methods = ['GET', 'POST'])
def add_user_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if loggedin == True:
        if request.method == 'POST':
            userid = request.form.get('userid')
            password = request.form.get('password')
            confirm_password =  request.form.get('confirm_password')
            print(userid, password, confirm_password)
            if password == confirm_password:
                escaped_username = userid.replace("'", "''") #evite injection sql
                cur.execute("SELECT username FROM Admins WHERE username = '{}'".format(escaped_username))
                username_bdd = cur.fetchall()
                escaped_mdp = password.replace("'", "''") #evite injection sql
                cur.execute("SELECT password FROM Admins WHERE password = '{}'".format(escaped_mdp))
                mdp_bdd = cur.fetchall()
                if (userid, password) != (username_bdd[0][0], mdp_bdd[0][0]):
                    cur.execute("INSERT INTO Admins(username) VALUES (?)",(userid, ))
                    cur.execute("INSERT INTO Admins(password) VALUES (?)",(password, ))
                    return render_template('home.html')
                return render_template('add_user.html',user_error="Le compte existe deja")
            return render_template('add_user.html',user_error="Les mots de passe ne correspondent pas")
        return render_template('add_user.html')
    else :
        return render_template('login.html')

@app.route("/scan")
def scan():
    if loggedin ==True:
        return render_template('scan.html')
    return render_template('login.html')

@app.route("/device_information")
def device_information():
    return render_template('device_information.html')

@app.route("/user_information", methods=['GET','POST'])
def user_information():
    return render_template('user_infomation.html')

app.config['UPLOAD_FOLDER'] = 'upload/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

"""
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = PIL.Image.open(file)
        codes = pyzbar.pyzbar.decode(image)
        redirection = codes[0].data.decode()
        return redirect(redirection)
"""

@app.route('/login_form', methods = ['GET', 'POST'])
def login_form():
    global loggedin
    loggedin = False
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        escaped_username = userid.replace("'", "''") #evite injection sql
        cur.execute("SELECT username FROM Admins WHERE username = '{}'".format(escaped_username))
        #cur.execute("SELECT username FROM Admins WHERE username = ?", (userid, ))
        username_bdd = cur.fetchall()
        escaped_mdp = password.replace("'", "''") #evite injection sql
        cur.execute("SELECT password FROM Admins WHERE password = '{}'".format(escaped_mdp))
        #cur.execute("SELECT password FROM Admins WHERE password = ?", (password, ))
        mdp_bdd = cur.fetchall()
        if username_bdd == [] or mdp_bdd == []:
            loggedin = False
            print("Mauvais MDP")
            conn.close()
            return render_template('login.html',mot_retour_connexion="Utilisateur ou Mot de passe invalide")
        if (userid, password) == (username_bdd[0][0], mdp_bdd[0][0]):
            loggedin = True
            conn.close()
            print('logged in')
            return render_template('home.html', utilisateur_connecte = username_bdd[0][0])