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