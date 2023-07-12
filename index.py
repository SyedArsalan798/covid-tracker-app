from flask import Flask, render_template, redirect, request, url_for, session, abort
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
from tensorflow.keras import models
from database import Database
import os


def checkAppropriateFile(file):
    ALLOWED_EXTENSIONS = ['png']
    for f in ALLOWED_EXTENSIONS:
        if file.endswith(f):
            return True
    return False

# Database.CreateTableDoctor()
# Database.insertIntoDoctor(1, 'doctor12', 'b.r.courtney@gmail.com', 'aRh$#78KL', 'Billie', 'Courtney')
# Database.CreateTablePatient()
# Database.CreateTableXRayImages()
# Database.CreateTableResults()

model = models.load_model('CNN_Covid19_Xray_V1.h5')

app = Flask(__name__)
app.secret_key = '7457hhhyuft26442'
app.config['UPLOAD_FOLDER'] = 'static/images/xrays'


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if "Useremail" and "Userpassword" not in session:
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            username = request.form['username']
            Useremail = request.form['Useremail']
            Userpassword = request.form['Userpassword']

            session['first_name'] = first_name
            session['last_name'] = last_name
            session['username'] = username
            session['Useremail'] = Useremail
            session['Userpassword'] = Userpassword

            check = Database.checkIfPatientAlreadyExistForSignUp(Useremail, username)
            if not check:
                Database.insertIntoPatient(
                    first_name, last_name, username, Useremail, Userpassword)
                return redirect(url_for('dashboard'))
            else:
                session.pop('Useremail', None)
                session.pop('Userpassword', None)
                return render_template('signup.html', flag=True)
        else:
            return render_template('signup.html')
    return redirect(url_for('dashboard'))



@app.route('/login', methods=['POST', 'GET'])
def login():
    if "Useremail" and "Userpassword" not in session:
        if request.method == 'POST':
            Useremail = request.form['Useremail']
            Userpassword = request.form['Userpassword']
            session["Useremail"] = Useremail
            session["Userpassword"] = Userpassword
            check = Database.checkIfPatientAlreadyExistForLogin(Useremail, Userpassword)
            if (check == True):
                return redirect(url_for('dashboard'))
            else:
                session.pop("Useremail", None)
                session.pop("Userpassword", None)
                return render_template("login.html", flag=True)
        else:
            return render_template("login.html")
    else:
        return redirect(url_for('dashboard'))





@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if "Useremail" and "Userpassword" in session:
        if request.method == 'POST':
            file = request.files['image']
            if file.filename == '':
                return "No file selected"
            if file and checkAppropriateFile(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = app.config['UPLOAD_FOLDER']

                file.save(os.path.join(upload_folder, filename))

                email = session['Useremail']
                password = session['Userpassword']

                patient_id = Database.getLoggedInPatientId(email, password)

                Database.insertIntoXRayImages(patient_id, filename)
                return redirect('/view_report')
            else:
                return "Invalid file format"
        else:
            return render_template("dashboard.html")
    return redirect(url_for('login'))

@app.route('/view_report')
def view_report():
    if "Useremail" and "Userpassword" in session:
        email = session['Useremail']
        password = session['Userpassword']

        patient_id = Database.getLoggedInPatientId(email, password)
        reports = Database.returnResults(patient_id)
        if reports:
            message = "Please Note that once you submit a request to doctor, it will take some time to respond. Please be patient."
            return render_template('view_report.html', reports=reports, message=message)
        else:
            message = "Please Note that once you submit a request to doctor, it will take some time to respond. Please be patient."
            return render_template('view_report.html', message=message)
    return redirect(url_for('login'))
        
    


@app.route('/doctor/login', methods=['POST', 'GET'])
def dlogin():
    if "email" and "password" not in session:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            session["email"] = email
            session["password"] = password

            check = Database.checkInDoctor(email, password)
            if (check == True):
                return redirect(url_for('doctor_dashboard'))
            else:
                session.pop("email", None)
                session.pop("password", None)
                return render_template("dlogin.html", flag=True)
        else:
            return render_template("dlogin.html")
    return redirect(url_for('doctor_dashboard'))


@app.route('/doctor/dashboard')
def doctor_dashboard(flag=None, img_id=None):
    if "email" and "password" in session:
        xray_imagesWithResults = Database.returnResultsWithImagesAndPatients()
        print(xray_imagesWithResults)

        return render_template('doctor_dashboard.html',xray_imagesWithResults=xray_imagesWithResults, flag=flag, img_id=img_id)
    return redirect(url_for('dlogin'))



@app.route('/doctor/dashboard/<int:flag>/<int:img_id>/<int:p_id>')
def doctor_dashboard_(flag, img_id, p_id):
    if "email" and "password" in session:
        count = Database.returnXRayImagesCount()
        if img_id <= count[0]:
            xray_image = Database.returnXRayImagesWithXrayId(img_id).fetchone()
            
            forwarded = Database.checkForwardedResults(p_id, img_id)
            if not forwarded:
                image_path = f"static/images/xrays/{xray_image[2]}"
                image = Image.open(image_path)
                image = image.resize((150, 150))
                image = np.array(image) / 255.0
                if image.shape[-1] != 3:
                    image = np.stack((image,) * 3, axis=-1)        
                image = np.expand_dims(image, axis=0)

                predictions = model.predict(image)

                predicted_class = np.argmax(predictions)

                class_names = ['COVID-19', 'Normal']

                predicted_label = class_names[predicted_class]
                print(predicted_label)

                prediction_probability = predictions.squeeze()
                print(prediction_probability[0])
                print(prediction_probability[1])

                result = predicted_label
                covid_probability = round(float(prediction_probability[0]), 5)
                normal_probability = round(float(prediction_probability[1]), 5)
                forwarded = 1
                Database.insertIntoResults(p_id, img_id, result, covid_probability, normal_probability, forwarded)

            xray_imagesWithResults = Database.returnResultsWithImagesAndPatients()

            return render_template('doctor_dashboard.html',xray_imagesWithResults=xray_imagesWithResults, flag=flag, img_id=img_id)
        else:
            abort(404)
    return redirect(url_for('dlogin'))


@app.route('/logout')
def Logout():
    if "Useremail" and "Userpassword" in session:
        session.pop('Useremail', None)
        session.pop('Userpassword', None)
        return redirect(url_for('login'))
    return redirect(url_for("login"))

@app.route('/doctor/logout')
def doctorLogout():
    if "email" and "password" in session:
        session.pop('email', None)
        session.pop('password', None)
        return redirect(url_for('dlogin'))
    return redirect(url_for("dlogin"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)