import os
import pikepdf
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    password = request.form['password']
    
    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

       
        if 'unlock' in request.form:
            success = unlock_pdf(file_path, password)
            print(success)
            if success:
                return send_file(success, as_attachment=True,mimetype='application/pdf', download_name=success)
            else:
                return "Oops..You entered a wrong password, Try again "
        elif 'lock' in request.form:
            success = lock_pdf(file_path, password)
            if success == 'protected':
                return render_template('protected.html')
            if success:
                return send_file(success, as_attachment=True,mimetype='application/pdf', download_name=success)
            else:
                return "Oops..Something went wrong while locking the PDF"
        else:
            return "Invalid operation selected"
    
    return "Invalid file format"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def unlock_pdf(pdf_path, password):
    try:
        with pikepdf.open(pdf_path, password=password,allow_overwriting_input=True) as pdf:
            unlocked_pdf_path = pdf_path.replace('.pdf', '_unlocked.pdf')
            pdf.save(unlocked_pdf_path)
            return unlocked_pdf_path
    except pikepdf.PasswordError:
        return None

def lock_pdf(pdf_path, password):
    try:
        with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
            pdf.save(pdf_path, encryption=pikepdf.Encryption(owner=password, user=password))
            return pdf_path
    except Exception as e:
        return "protected"

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
