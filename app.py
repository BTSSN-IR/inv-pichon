from flask import Flask, request, url_for, redirect, render_template, flash, send_file, session
import os
import mysql.connector
import sqlite3
import qrcode
import qrcode.constants
import time
from redis import Redis

import hashlib, base64

global loggedin
loggedin = False
global utilisateur_connecte
utilisateur_connecte = 'invité'
app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

app.config['SESSION_TYPE'] = 'redis'  # Backend de session
app.config['SESSION_REDIS'] = Redis(host='localhost', port=5000)  # Configuration de Redis

app.config['UPLOAD_FOLDER'] = 'upload/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

import pyzbar.pyzbar
import PIL.Image

from werkzeug.utils import secure_filename

def generate_hash_key(key):
    hash_object = hashlib.sha256()
    hash_object.update(key.encode('utf-8'))
    hash_key = hash_object.digest()
    return hash_key

SECRET_KEY = 'bts_sn'

def encrypt_password(password, key=SECRET_KEY):
    hash_key = generate_hash_key(key)
    combined = password + hash_key.hex()
    encrypted_password = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
    return encrypted_password

def decrypt_password(encrypted_password, key=SECRET_KEY):
    hash_key = generate_hash_key(key)
    decoded = base64.b64decode(encrypted_password.encode('utf-8')).decode('utf-8')
    password = decoded.replace(hash_key.hex(), '')
    return password

@app.route("/logout")
def logout():
    session.pop('utilisateur_connecte', None)
    loggedin = False
    return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/generate_qrcode")
def generate_qrcode():
    data = request.args.get('table') + ',' + request.args.get('device') 
    qr = qrcode.QRCode(version = 1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size = 10, border = 4)
    qr.add_data(data)
    qr.make(fit = True)

    image = qr.make_image(fill_color = "black", back_color = "white")
    image.save(f"qrcodes/{data}.png")
    return send_file(f"qrcodes/{data}.png")

@app.route("/")
def home():
    if 'loggedin' in session and session['loggedin']:
        try:
            return render_template('home.html', utilisateur_connecte=session['utilisateur_connecte'], logged_in=True)
        except:
            return render_template('home.html', logged_in=False)
    else:
        return render_template('login.html', logged_in=False)

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/show_devices")
def show_devices():
    if 'loggedin' in session and session['loggedin']:
        print('Logged in')
        conn = sqlite3.connect('inv_pichon.db')
        cur = conn.cursor()
        print(cur.execute("SELECT * from Computers").fetchall())
        computers_table = cur.execute("SELECT * from Computers").fetchall()
        screens_table = cur.execute("SELECT * from Screens").fetchall()
        admins_table = cur.execute("SELECT * from Admins").fetchall()
        phones_table = cur.execute("SELECT * from Phones").fetchall()
        employees_table = cur.execute("SELECT * from Users").fetchall()
        return render_template('show_devices.html',computers=computers_table, screens=screens_table, admins=admins_table, phones=phones_table, employees=employees_table)
    else:
        return render_template('login.html')

@app.route("/add_equipment")
def add_equipment():
    if loggedin == True:
        return render_template('add_equipment.html')
    return render_template('login.html')

@app.route("/add_user")
def add_user():
    if loggedin == True:
        return render_template('add_user.html')
    return render_template('login.html')

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
                print("SELECT username FROM Admins WHERE username = '{}'".format(userid))
                cur.execute("SELECT username FROM Admins WHERE username = '{}'".format(userid))
                username_bdd = cur.fetchall()
                pass_encoded = encrypt_password(password, SECRET_KEY) # Cryptage du mot de passe avec une clé secrète
                print(pass_encoded)
                print(decrypt_password(pass_encoded))
                print("SELECT password FROM Admins WHERE password = '{}'".format(pass_encoded))
                cur.execute("SELECT password FROM Admins WHERE password = '{}'".format(pass_encoded))
                mdp_bdd = cur.fetchall()
                if (username_bdd, mdp_bdd) == ([], []):
                    cur.execute("INSERT INTO Admins(username, password) VALUES (\"{}\",\"{}\")".format(userid,pass_encoded))
                    conn.commit()
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

    print(request.json.get('qr_code'))
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    device_data = [request.args.get('table'), request.args.get('device')]
    list_headers = cur.execute(f"PRAGMA table_info({device_data[0]});").fetchall()
    for i in range(len(list_headers)):
        list_headers[i] = list_headers[i][1] # Remplacement des champs par seulement le nom des champs

    try:
        data_list = cur.execute(f"SELECT * FROM {device_data[0]} WHERE {list_headers[0]} == \'{device_data[1]}\'").fetchall()
        data_list = [str(i) for i in list(data_list[0])]
        payload = zip(data_list, list_headers)
    except:
        print('error')
    return render_template('device_information_search.html', payload=payload, device_type=device_data[0])

@app.route("/user_information", methods=['GET','POST'])
def user_information():
    return render_template('user_infomation.html')

@app.route("/equipment_types/computer", methods=['GET','POST'])
def add_computer():
    return render_template('equipment_types/computer.html')

@app.route("/add_equipment_form_computer_appliquer", methods = ['GET','POST'])
def add_equipment_computer_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        hostname = request.form.get('hostname-input')
        serialnumber = request.form.get('serialnumber-input')
        assigneduser = request.form.get('assigneduser-input')
        print(f'hostname : {hostname}; serialnumber : {serialnumber}; user : {assigneduser}')
        print(f"INSERT INTO Computers(hostname, serialnumber, mainuser) VALUES (\"{hostname}\",\"{serialnumber}\",\"{assigneduser}\")")
        cur.execute("INSERT INTO Computers(hostname, serialnumber, mainuser) VALUES (\"{}\",\"{}\",\"{}\")".format(hostname,serialnumber, assigneduser))
        conn.commit()
    return render_template('equipment_types/computer.html',validation_code = "L'équipement a bien été ajouté")
    
@app.route("/equipment_types/screen", methods=['GET','POST'])
def add_screen():
    return render_template('equipment_types/screen.html')

@app.route("/add_equipment_form_screen_appliquer", methods = ['GET','POST'])
def add_equipment_screen_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        make = request.form.get('make-input')
        model = request.form.get('model-input')
        serialnumber = request.form.get('serialnumber-input')
        purchasedate = request.form.get('purchase-input')
        assigneduser = request.form.get('assigneduser-input')
        cur.execute("INSERT INTO Screens(make, model, serialnumber, purchasedate, mainuser) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(make, model, serialnumber, purchasedate, assigneduser))
        conn.commit()
    return render_template('equipment_types/screen.html',validation_code = "L'équipement a bien été ajouté")

@app.route("/equipment_types/phone", methods=['GET','POST'])
def add_phone():
    return render_template('equipment_types/phone.html')

@app.route("/add_equipment_form_phone_appliquer", methods = ['GET','POST'])
def add_equipment_phone_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        model = request.form.get('model')
        serialnumber = request.form.get('serialnumber-input')
        phonenumber = request.form.get('phonenumber-input')
        purchase = request.form.get('purchase-input')
        make = request.form.get('make-input')
        assigneduser = request.form.get('assigneduser-input')
        cur.execute("INSERT INTO Phones(make, model, serialnumber, purchasedate, phonenumber, mainuser) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(make,model, serialnumber, purchase, phonenumber, assigneduser))
        conn.commit()
    return render_template('equipment_types/phone.html',validation_code = "L'équipement a bien été ajouté")

@app.route("/equipment_types/employee", methods=['GET','POST'])
def add_employee():
    return render_template('equipment_types/employee.html')

@app.route("/add_equipment_form_employee_appliquer", methods = ['GET','POST'])
def add_equipment_employee_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        firstname = request.form.get('firstname-input')
        lastname = request.form.get('lastname-input')
        department = request.form.get('department-input')
        email = request.form.get('email-input')
        computer = request.form.get('computer-input')
        phone = request.form.get('phone-input')
        mouse = request.form.get('mouse-input')
        print("INSERT INTO Users(firstname, lastname, department, email, computer, phone, mouse) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(firstname, lastname, department, email, computer, phone, mouse))
        cur.execute("INSERT INTO Users(firstname, lastname, department, email, computer, phone, mouse) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(firstname, lastname, department, email, computer, phone, mouse))
        conn.commit()
    return render_template('equipment_types/employee.html',validation_code = "L'utilisateur a bien été ajouté")

@app.route("/equipment_types/mouse", methods=['GET','POST'])
def add_mouse():
    return render_template('equipment_types/mouse.html')

@app.route("/add_equipment_form_mouse_appliquer", methods = ['GET','POST'])
def add_equipment_mouse_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        make = request.form.get('make-input')
        model = request.form.get('model-input')
        mainuser = request.form.get('mainuser-input')
        cur.execute("INSERT INTO Mouse(make, model, user) VALUES (\"{}\",\"{}\",\"{}\")".format(make, model, mainuser))
        conn.commit()
    return render_template('equipment_types/mouse.html',validation_code = "L'équipement a bien été ajouté")

@app.route("/equipment_types/keyboard", methods=['GET','POST'])
def add_keyboard():
    return render_template('equipment_types/keyboard.html')

@app.route("/add_equipment_form_keyboard_appliquer", methods = ['GET','POST'])
def add_equipment_keyboard_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        hostname = request.form.get('hostname-input')
        serialnumber = request.form.get('serialnumber')
        assigneduser = request.form.get('assigned-user')
        cur.execute("INSERT INTO Computers(hostname, serialnumber, mainuser) VALUES (\"{}\",\"{}\",\"{}\")".format(hostname,serialnumber, assigneduser))
    return render_template('equipment_types/keyboard.html',validation_code = "L'équipement a bien été ajouté")

@app.route("/equipment_types/printer", methods=['GET','POST'])
def add_printer():
    return render_template('equipment_types/printer.html')

@app.route("/add_equipment_form_printer_appliquer", methods = ['GET','POST'])
def add_equipment_printer_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        hostname = request.form.get('hostname-input')
        make = request.form.get('make-input')
        model = request.form.get('model-input')
        purchasedate = request.form.get('purchasedate-input')
        serialnumber = request.form.get('serialnumber-input')
        cur.execute("INSERT INTO Printers(hostname, make, model, serialnumber, purchasedate) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(hostname,make,model,serialnumber,purchasedate))
        conn.commit()
    return render_template('equipment_types/printer.html',validation_code = "L'équipement a bien été ajouté")

@app.route("/equipment_types/software", methods=['GET','POST'])
def add_software():
    return render_template('equipment_types/software.html')

@app.route("/add_equipment_form_software_appliquer", methods = ['GET','POST'])
def add_equipment_software_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name-input')
        description = request.form.get('description-input')
        cur.execute("INSERT INTO Software(name, description) VALUES (\"{}\",\"{}\")".format(name,description))
        conn.commit()
    return render_template('equipment_types/software.html',validation_code = "Le logiciel a bien été ajouté")

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
        username_bdd = cur.fetchall()
        escaped_mdp = password.replace("'", "''") #evite injection sql
        cur.execute("SELECT password FROM Admins WHERE password = '{}'".format(escaped_mdp))
        mdp_bdd = cur.fetchall()
        if username_bdd == [] or mdp_bdd == []:
            loggedin = False
            print("Mauvais MDP")
            conn.close()
            return render_template('login.html',mot_retour_connexion="Utilisateur ou Mot de passe invalide")
        if (userid, password) == (username_bdd[0][0], mdp_bdd[0][0]): # Décryptage du mdp a revoir -------------------------------------------------------------
            loggedin = True
            conn.close()
            print('logged in')
            session['loggedin'] = True
            session['utilisateur_connecte'] = request.form['userid']
            return render_template('home.html', utilisateur_connecte=session['utilisateur_connecte'], logged_in=loggedin)

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
    app.run(host='0.0.0.0', port=5000, debug=True)