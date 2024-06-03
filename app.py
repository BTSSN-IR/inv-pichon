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
    session.pop('loggedin')
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
        printers_table = cur.execute("SELECT * from Printers").fetchall()
        screens_table = cur.execute("SELECT * from Screens").fetchall()
        admins_table = cur.execute("SELECT * from Admins").fetchall()
        phones_table = cur.execute("SELECT * from Phones").fetchall()
        employees_table = cur.execute("SELECT * from Users").fetchall()
        externaldrives_table = cur.execute("SELECT * from ExternalDrives").fetchall()
        return render_template('show_devices.html',computers=computers_table, printers=printers_table, screens=screens_table, admins=admins_table, phones=phones_table,externaldrives=externaldrives_table, employees=employees_table)
    else:
        return render_template('login.html')

@app.route("/add_equipment")
def add_equipment():
    if 'loggedin' in session and session['loggedin']:
        return render_template('add_equipment.html')
    return render_template('login.html')

@app.route("/add_user")
def add_user():
    if 'loggedin' in session and session['loggedin']:
        return render_template('add_user.html')
    return render_template('login.html')

@app.route("/add_user_form", methods = ['GET', 'POST'])
def add_user_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if 'loggedin' in session and session['loggedin']:
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
    if 'loggedin' in session and session['loggedin']:
        return render_template('scan.html')
    return render_template('login.html')

@app.route("/device_information", methods=['POST'])
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
        purchase = request.form.get('purchasedate-input')
        licenses = request.form.get('licenses-input')
        cur.execute("INSERT INTO Computers(hostname, serialnumber, mainuser, purchasedate, licenses) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(hostname,serialnumber, assigneduser, purchase, licenses))
        conn.commit()
    return render_template('equipment_types/computer.html',validation_code = "The computer was successfully added")
    
@app.route("/update_equipement_computer", methods = ['GET','POST'])
def update_equipement_computer():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        hostname = request.form.get('hostname-input')
        serialnumber = request.form.get('serialnumber-input')
        assigneduser = request.form.get('assigneduser-input')
        purchase = request.form.get('purchasedate-input')
        licenses = request.form.get('licenses-input')
        cur.execute("SELECT * FROM Computers WHERE serialnumber = ?", (serialnumber,))
        contenue_entree = cur.fetchall()
        if " " in assigneduser :
            utilisateur = assigneduser.split()
            cur.execute("SELECT firstname FROM Users WHERE firstname = '{}'".format(utilisateur[0]))
            Prenom_bdd = cur.fetchall()
            cur.execute("SELECT lastname FROM Users WHERE lastname = '{}'".format(utilisateur[1]))
            Nom_bdd = cur.fetchall()
            if Prenom_bdd == [] or Nom_bdd == []:
                return render_template('Device_information_scan/computer.html', message_erreur = "User is not in the database", contenue_entree = contenue_entree)   
            cur.execute("UPDATE Computers SET serialnumber = '{}', hostname = '{}', mainuser = '{}', purchasedate = '{}', licenses = '{}' WHERE serialnumber = '{}'".format(serialnumber, hostname, assigneduser, purchase, licenses, serialnumber))
            conn.commit()
            return render_template('scan.html',message_erreur = "The equipment has been updated")    
        return render_template('Device_information_scan/computer.html', message_erreur = "space between first name and last name.", contenue_entree = contenue_entree)

@app.route("/delete_equipement_computer", methods = ['GET','POST'])
def delete_equipement_computer():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        serialnumber = request.form.get('serialnumber-input')
        print(serialnumber)
        cur.execute("DELETE FROM Computers WHERE serialnumber = ?", (serialnumber,))
        conn.commit()
    return render_template('scan.html', message_erreur = "The equipment has been removed")

@app.route("/equipment_types/screen", methods=['GET','POST'])
def add_screen():
    return render_template('equipment_types/screen.html')

@app.route("/add_equipment_form_screen_appliquer", methods = ['GET','POST'])
def add_equipment_screen_form():
    conn = sqlite3.connect('inv_pichon.db') # Connexion à la base de données avec le module SQLite3
    cur = conn.cursor()
    if request.method == 'POST':
        make = request.form.get('make-input') # Récupération des champs tapés par l'utilisateur
        model = request.form.get('model-input')
        serialnumber = request.form.get('serialnumber-input')
        purchasedate = request.form.get('purchase-input')
        assigneduser = request.form.get('assigneduser-input')
        # Insertion dans la base de données de l'équipement avec les informations récupérées dans le formulaire
        cur.execute("INSERT INTO Screens(make, model, serialnumber, purchasedate, mainuser) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(make, model, serialnumber, purchasedate, assigneduser))
        # Validation des changements
        conn.commit()
    return render_template('equipment_types/screen.html',validation_code = "The screen was successfully added") # Affichage de la page avec un message de validation ajouté

@app.route("/update_equipement_screen", methods = ['GET','POST'])
def update_equipement_screen():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        make = request.form.get('make-input') # Récupération des champs tapés par l'utilisateur
        model = request.form.get('model-input')
        serialnumber = request.form.get('serialnumber-input')
        purchasedate = request.form.get('purchase-input')
        assigneduser = request.form.get('assigneduser-input')
        cur.execute("SELECT * FROM Screens WHERE serialnumber = ?", (serialnumber,))
        contenue_entree = cur.fetchall()
        if " " in assigneduser :
            utilisateur = assigneduser.split()
            cur.execute("SELECT firstname FROM Users WHERE firstname = '{}'".format(utilisateur[0]))
            Prenom_bdd = cur.fetchall()
            cur.execute("SELECT lastname FROM Users WHERE lastname = '{}'".format(utilisateur[1]))
            Nom_bdd = cur.fetchall()
            if Prenom_bdd == [] or Nom_bdd == []:
                return render_template('Device_information_scan/screen.html', message_erreur = "User is not in the database", contenue_entree = contenue_entree)   
            cur.execute("UPDATE Screens SET serialnumber = '{}', make = '{}', model = '{}', purchasedate = '{}', mainuser = '{}' WHERE serialnumber = '{}'".format(serialnumber, make, model, purchasedate, assigneduser, serialnumber))
            conn.commit()
            return render_template('scan.html',message_erreur = "The equipment has been updated")
        return render_template('Device_information_scan/screen.html', message_erreur = "space between first name and last name.", contenue_entree = contenue_entree)


@app.route("/delete_equipement_screen", methods = ['GET','POST'])
def delete_equipement_screen():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        serialnumber = request.form.get('serialnumber-input')
        print(serialnumber)
        cur.execute("DELETE FROM Screens WHERE serialnumber = ?", (serialnumber,))
        conn.commit()
    return render_template('scan.html', message_erreur = "The equipment has been removed")

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
    return render_template('equipment_types/phone.html',validation_code = "The phone was successfully added")

@app.route("/update_equipement_phone", methods = ['GET','POST'])
def update_equipement_phone():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        model = request.form.get('model-input')
        serialnumber = request.form.get('serialnumber-input')
        phonenumber = request.form.get('phonenumber-input')
        purchase = request.form.get('purchase-input')
        make = request.form.get('make-input')
        assigneduser = request.form.get('assigneduser-input')
        cur.execute("SELECT * FROM Phones WHERE serialnumber = ?", (serialnumber,))
        contenue_entree = cur.fetchall()
        if " " in assigneduser :
            utilisateur = assigneduser.split()
            cur.execute("SELECT firstname FROM Users WHERE firstname = '{}'".format(utilisateur[0]))
            Prenom_bdd = cur.fetchall()
            cur.execute("SELECT lastname FROM Users WHERE lastname = '{}'".format(utilisateur[1]))
            Nom_bdd = cur.fetchall()
            if Prenom_bdd == [] or Nom_bdd == []:
                return render_template('Device_information_scan/phone.html', message_erreur = "User is not in the database", contenue_entree = contenue_entree)   
            cur.execute("UPDATE Phones SET make = '{}', model = '{}', serialnumber = '{}', purchasedate = '{}', phonenumber = '{}', mainuser = '{}' WHERE serialnumber = '{}'".format(make, model, serialnumber, purchase, phonenumber, assigneduser, serialnumber))
            conn.commit()
            return render_template('scan.html',message_erreur = "The equipment has been updated")
        return render_template('Device_information_scan/phone.html', message_erreur = "space between first name and last name.", contenue_entree = contenue_entree)

@app.route("/delete_equipement_phone", methods = ['GET','POST'])
def delete_equipement_phone():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        serialnumber = request.form.get('serialnumber-input')
        print(serialnumber)
        cur.execute("DELETE FROM Phones WHERE serialnumber = ?", (serialnumber,))
        conn.commit()
    return render_template('scan.html', message_erreur = "The equipment has been removed")
    
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
    return render_template('equipment_types/employee.html',validation_code = "The employee was successfully added")

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
    return render_template('equipment_types/mouse.html',validation_code = "The mouse was successfully added")

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
    return render_template('equipment_types/keyboard.html',validation_code = "The keyboard was successfully added")

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
        ip = request.form.get('ip-input')
        cur.execute("INSERT INTO Printers(hostname, make, model, serialnumber, purchasedate, ip) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(hostname,make,model,serialnumber,purchasedate, ip))
        conn.commit()
    return render_template('equipment_types/printer.html',validation_code = "The printer was successfully added")

@app.route("/update_equipement_printer", methods = ['GET','POST'])
def update_equipement_printer():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        hostname = request.form.get('hostname-input')
        make = request.form.get('make-input')
        model = request.form.get('model-input')
        purchasedate = request.form.get('purchasedate-input')
        serialnumber = request.form.get('serialnumber-input')
        ip = request.form.get('ip-input')
        cur.execute("UPDATE Printers SET serialnumber = '{}', make = '{}', model = '{}', hostname = '{}', purchasedate = '{}', ip = '{}' WHERE serialnumber = '{}'".format(serialnumber, make, model, hostname, purchasedate, ip, serialnumber))
        conn.commit()
    return render_template('scan.html',message_erreur = "The equipment has been updated")

@app.route("/delete_equipement_printer", methods = ['GET','POST'])
def delete_equipement_printer():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        serialnumber = request.form.get('serialnumber-input')
        print(serialnumber)
        cur.execute("DELETE FROM Printers WHERE serialnumber = ?", (serialnumber,))
        conn.commit()
    return render_template('scan.html', message_erreur = "The equipment has been removed")

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
    return render_template('equipment_types/software.html',validation_code = "The software was successfully added")

@app.route("/equipment_types/externaldrive", methods=['GET','POST'])
def add_externaldrive():
    return render_template('equipment_types/externaldrive.html')

@app.route("/add_equipment_form_externaldrive_appliquer", methods = ['GET','POST'])
def add_equipment_externaldrive_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        serialnumber = request.form.get('serialnumber-input')
        make = request.form.get('make-input')
        model = request.form.get('model-input')
        type = request.form.get('type-input')
        capacity = request.form.get('capacity-input')
        purchasedate = request.form.get('purchasedate-input')
        cur.execute("INSERT INTO ExternalDrives(serialnumber, make, model, type, capacity, purchasedate) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(serialnumber, make, model, type, capacity, purchasedate))
        conn.commit()
    return render_template('equipment_types/externaldrive.html',validation_code = "The drive was successfully added")

@app.route("/update_equipement_externaldrive", methods = ['GET','POST'])
def update_equipement_externaldrive():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        serialnumber = request.form.get('serialnumber-input')
        make = request.form.get('make-input')
        model = request.form.get('model-input')
        type = request.form.get('type-input')
        capacity = request.form.get('capacity-input')
        purchasedate = request.form.get('purchasedate-input')
        cur.execute("UPDATE ExternalDrives SET serialnumber = '{}', make = '{}', model = '{}', type = '{}', capacity = '{}', purchasedate = '{}' WHERE serialnumber = '{}'".format(serialnumber, make, model, type, capacity, purchasedate, serialnumber))
        conn.commit()
    return render_template('scan.html', message_erreur = "The equipment has been updated")

@app.route("/delete_equipement_externaldrive", methods = ['GET','POST'])
def delete_equipement_externaldrive():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        serialnumber = request.form.get('serialnumber-input')
        print(serialnumber)
        cur.execute("DELETE FROM ExternalDrives WHERE serialnumber = ?", (serialnumber,))
        conn.commit()
    return render_template('scan.html', message_erreur = "The equipment has been removed")

def allowed_file(filename):
    valid_extensions = ('.jpg', '.jpeg', '.png')
    return filename.lower().endswith(valid_extensions)

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
        else :
            return render_template("scan.html", message_erreur = "The file is not an image")
        image = PIL.Image.open(file)
        codes = pyzbar.pyzbar.decode(image)
        print(codes)
        if codes == []:
            return render_template("scan.html", message_erreur = "The image is not a QR Code")
        redirection = codes[0].data.decode()
        conn = sqlite3.connect('inv_pichon.db') # Connexion à la base de données
        cur = conn.cursor()
        if ',' in redirection:
            liste_redirection = redirection.split(",")
            if liste_redirection[0] in ["Computers","ExternalDrives","Phones","Printers","Screens"]:
                    query = "SELECT * FROM \"{}\" WHERE serialnumber = ?".format(liste_redirection[0])
                    cur.execute(query, (liste_redirection[1],))
                    contenue_entree = cur.fetchall()
                    conn.close()
                    if contenue_entree == []:
                        return render_template("scan.html",message_erreur = "The equipment is not referenced in the database")
                    if liste_redirection[0] == "Computers":
                        return render_template("Device_information_scan/computer.html",contenue_entree = contenue_entree)
                    if liste_redirection[0] == "ExternalDrives":
                        return render_template("Device_information_scan/externaldrive.html",contenue_entree = contenue_entree)
                    if liste_redirection[0] == "Phones":
                        return render_template("Device_information_scan/phone.html",contenue_entree = contenue_entree)
                    if liste_redirection[0] == "Printers":
                        return render_template("Device_information_scan/printer.html",contenue_entree = contenue_entree)
                    if liste_redirection[0] == "Screens":
                        return render_template("Device_information_scan/screen.html",contenue_entree = contenue_entree)
            return render_template("scan.html", message_erreur = "The QR Code is not valid")
        return render_template("scan.html", message_erreur = "The QR Code is not valid")
    
@app.route('/redirection_scan_api', methods = ['POST'])
def redirection_scan_api():
    conn = sqlite3.connect('inv_pichon.db') # Connexion à la base de données
    cur = conn.cursor()
    redirection = request.form.get('qr_data')
    print(redirection)
    if ',' in redirection:
        liste_redirection = redirection.split(",")
        if liste_redirection[0] in ["Computers","ExternalDrives","Phones","Printers","Screens"]:
                query = "SELECT * FROM \"{}\" WHERE serialnumber = ?".format(liste_redirection[0])
                cur.execute(query, (liste_redirection[1],))
                contenue_entree = cur.fetchall()
                conn.close()
                if contenue_entree == []:
                    return render_template("scan.html",message_erreur = "The equipment is not referenced in the database")
                if liste_redirection[0] == "Computers":
                    return render_template("Device_information_scan/computer.html",contenue_entree = contenue_entree)
                if liste_redirection[0] == "ExternalDrives":
                    return render_template("Device_information_scan/externaldrive.html",contenue_entree = contenue_entree)
                if liste_redirection[0] == "Phones":
                    return render_template("Device_information_scan/phone.html",contenue_entree = contenue_entree)
                if liste_redirection[0] == "Printers":
                    return render_template("Device_information_scan/printer.html",contenue_entree = contenue_entree)
                if liste_redirection[0] == "Screens":
                    return render_template("Device_information_scan/screen.html",contenue_entree = contenue_entree)
        return render_template("scan.html", message_erreur = "The QR Code is not valid")
    return render_template("scan.html", message_erreur = "The QR Code is not valid")

@app.route('/login_form', methods = ['GET', 'POST'])
def login_form():
    global loggedin
    loggedin = False
    conn = sqlite3.connect('inv_pichon.db') # Connexion à la base de données
    cur = conn.cursor()
    if request.method == 'POST':
        userid = request.form.get('userid') # Récuprération des informations entrées par l'utilisateur
        password = request.form.get('password')
        escaped_username = userid.replace("'", "''") #Evite injection SQL
        cur.execute("SELECT username FROM Admins WHERE username = '{}'".format(escaped_username)) # Récupération de l'utilisateur depuis la base de données
        username_bdd = cur.fetchall()
        escaped_mdp = password.replace("'", "''") #Evite injection SQL
        # escaped_mdp = encrypt_password(password) # test pour la connexion avec des comptes qui ont des mots de passe cryptés
        cur.execute("SELECT password FROM Admins WHERE password = '{}'".format(escaped_mdp)) # Récupération du mot de passe depuis la base de données
        mdp_bdd = cur.fetchall()
        if username_bdd == [] or mdp_bdd == []: # Cas ou l'utilisateur n'existe pas dans la base de données
            loggedin = False
            print("Mauvais MDP")
            conn.close()
            return render_template('login.html',mot_retour_connexion="Utilisateur ou Mot de passe invalide") # Affichage du message d'erreur
        if (userid, password) == (username_bdd[0][0], mdp_bdd[0][0]): # Cas ou le mot de passe et le nom d'utilisateur sont corrects ----------- Décryptage MDP à revoir -----------
            loggedin = True
            conn.close()
            print('logged in')
            session['loggedin'] = True
            session['utilisateur_connecte'] = request.form['userid']
            return render_template('home.html', utilisateur_connecte=session['utilisateur_connecte'], logged_in=loggedin) # Redirection vers l'accueil

@app.route('/details_equipment_user', methods = ['POST'])
def details_equipment_user():
    conn = sqlite3.connect('inv_pichon.db') # Connexion à la base de données
    cur = conn.cursor()
    id_user = request.form.get('userid')
    user_name = cur.execute(f'SELECT firstname, lastname FROM Users WHERE id={id_user}').fetchall()[0]
    user_name = str(user_name[0] + ' ' + user_name[1])
    user_mouse = cur.execute(f'SELECT * FROM Mouse WHERE user={id_user}').fetchall()
    user_computer = cur.execute(f'SELECT * FROM Computers WHERE mainuser={id_user}').fetchall()
    user_screen = cur.execute(f'SELECT * FROM Screens WHERE mainuser=\"{id_user}\"').fetchall()
    user_phone = cur.execute(f'SELECT * FROM Phones WHERE mainuser=\"{id_user}\"').fetchall()
    user_externaldrive = cur.execute(f'SELECT * FROM Phones WHERE mainuser=\"{id_user}\"').fetchall()
    return render_template('user_equipment.html', id_user = id_user, user_name = user_name, user_mouse = user_mouse, user_computer = user_computer, user_screen = user_screen, user_phone = user_phone, user_externaldrive = user_externaldrive)

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
    app.run(host='0.0.0.0', port=5000, debug=True)
