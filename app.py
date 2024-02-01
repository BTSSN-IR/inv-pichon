from flask import Flask, request, url_for, redirect, render_template, flash
import os
app = Flask(__name__)

from werkzeug.utils import secure_filename

loggedin = False

@app.route("/")
def home():
    if loggedin == True:
        print('Logged in')
    return render_template('home.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/scan")
def scan():
    return render_template('scan.html')

@app.route("/device_information")
def device_information():
    return render_template('device_information.html')


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
        return render_template('scan.html')
    
@app.route('/login_form', methods = ['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
    print(userid, password)
    if (userid, password) == ('Gwendal', 'gt'):
        loggedin = True
        return render_template('home.html')
    print('logged in')
    
    return render_template('login.html')
    
# https://www.refbax.com/cours-en-ligne/comment-lire-un-qr-code-avec-python