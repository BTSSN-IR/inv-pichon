from flask import Flask, request, url_for, redirect, render_template, flash, send_file
import os
import mysql.connector
import sqlite3
import qrcode
import qrcode.constants

global loggedin
loggedin = False
global utilisateur_connecte
utilisateur_connecte = 'invité'
app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

import pyzbar.pyzbar
import PIL.Image

from werkzeug.utils import secure_filename

def generate_qrcode():
    data = request.form.get('serialnumber-input')
    qr = qrcode.QRCode(version = 1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size = 10, border = 4)
    qr.add_data(data)
    qr.make(fit = True)

    image = qr.make_image(fill_color = "black", back_color = "white")
    # uploaded_file = request.files[image]
    # uploaded_file_path = os.path.join('upload', uploaded_file.filename)
    # uploaded_file.save(uploaded_file_path)
    image.save("test.png")
    return send_file("test.png", as_attachment=True)

@app.route("/")
def home():
    if loggedin == True:
        print('Logged in')
    return render_template('home.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/show_devices")
def show_devices():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    computers_table = cur.execute("SELECT * from Computers").fetchall()
    screens_table = cur.execute("SELECT * from Screens").fetchall()
    admins_table = cur.execute("SELECT * from Admins").fetchall()
    phones_table = cur.execute("SELECT * from Phones").fetchall()
    employees_table = cur.execute("SELECT * from Users").fetchall()
    return render_template('show_devices.html',computers=computers_table, screens=screens_table, admins=admins_table, phones=phones_table, employees=employees_table)

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
                escaped_username = userid.replace("'", "''") #evite injection sql
                cur.execute("SELECT username FROM Admins WHERE username = '{}'".format(escaped_username))
                username_bdd = cur.fetchall()
                escaped_mdp = password.replace("'", "''") #evite injection sql
                cur.execute("SELECT password FROM Admins WHERE password = '{}'".format(escaped_mdp))
                mdp_bdd = cur.fetchall()
                if (username_bdd, mdp_bdd) == ([], []):
                    # print("INSERT INTO Admins(username, password) VALUES (\"{}\",\"{}\"").format(escaped_username,escaped_mdp)
                    cur.execute("INSERT INTO Admins(username, password) VALUES (\"{}\",\"{}\")".format(escaped_username,escaped_mdp))
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
    return render_template('device_information_search.html')

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
        generate_qrcode()
    return render_template('equipment_types/computer.html')
    
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
    return render_template('equipment_types/screen.html')

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
    return render_template('equipment_types/phone.html')

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
    return render_template('equipment_types/employee.html')

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
    return render_template('equipment_types/mouse.html')

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
    return render_template('equipment_types/keyboard.html')

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
    return render_template('equipment_types/printer.html')

@app.route("/equipment_types/software", methods=['GET','POST'])
def add_software():
    return render_template('equipment_types/software.html')

@app.route("/add_equipment_form_software_appliquer", methods = ['GET','POST'])
def add_equipment_software_form():
    conn = sqlite3.connect('inv_pichon.db')
    cur = conn.cursor()
    if request.method == 'POST':
        hostname = request.form.get('hostname-input')
        serialnumber = request.form.get('serialnumber')
        assigneduser = request.form.get('assigned-user')
        cur.execute("INSERT INTO Computers(hostname, serialnumber, mainuser) VALUES (\"{}\",\"{}\",\"{}\")".format(hostname,serialnumber, assigneduser))
    return render_template('equipment_types/softare.html')


app.config['UPLOAD_FOLDER'] = 'upload/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        if (userid, password) == (username_bdd[0][0], mdp_bdd[0][0]):
            loggedin = True
            conn.close()
            print('logged in')
            return render_template('home.html', utilisateur_connecte = username_bdd[0][0])

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
    app.run(host='0.0.0.0', port=5000, debug=True)