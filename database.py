import sqlite3 as s
from datetime import datetime
class Database:
    def __init__(self):
        pass

    @staticmethod
    def CreateTableDoctor():
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE Doctor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT,
            first_name TEXT,
            last_name TEXT
            )
        ''')
        connection.commit()
        connection.close()

    @staticmethod
    def insertIntoDoctor(id, username, email, password, first_name, last_name):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO Doctor VALUES (?,?,?,?,?,?)",
                        (id, username, email, password, first_name, last_name))
            connection.commit()
        except:
            connection.rollback()
        connection.close()

    @staticmethod
    def checkInDoctor(email, password):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        Doctors = cursor.execute("SELECT * from Doctor")
        for Doctor in Doctors:
            if (email and password) in Doctor:
                return True
        return False


    @staticmethod
    def CreateTablePatient():
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE Patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT,
            first_name TEXT,
            last_name TEXT
            )
        '''
                       )
        connection.commit()
        connection.close()

    @staticmethod
    def insertIntoPatient(first_name, last_name, username, Useremail, Userpassword):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        cursor.execute("pragma foreign_keys=on")
        cursor.execute("BEGIN TRANSACTION")
        try:
            cursor.execute('''INSERT INTO Patients(username, first_name, last_name, password, email) VALUES (?,?,?,?,?)''', (username, first_name, last_name, Userpassword, Useremail))
            connection.commit()
        except:
            connection.rollback()
        connection.close()


    @staticmethod
    def checkIfPatientAlreadyExistForLogin(Useremail, Userpassword):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        Patients = cursor.execute("SELECT * from Patients")
        for Patient in Patients:
            if (Useremail and Userpassword) in Patient:
                return True
        return False
    
    @staticmethod
    def checkIfPatientAlreadyExistForSignUp(Useremail, username):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        Patients = cursor.execute("SELECT * from Patients")
        for Patient in Patients:
            if (Useremail) in Patient:
                return True
            
            if(username in Patient):
                return True
            
        return False
    

    @staticmethod
    def getLoggedInPatientId(email, password):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM Patients WHERE email = ? AND password = ?", (email, password))
        result = cursor.fetchone()
        connection.close()

        if result:
            return result[0]
        else:
            return None

    

    @staticmethod
    def CreateTableXRayImages():
        connection = s.connect("covid_tracker.db")
        connection.execute("PRAGMA timezone = 'local'")
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE XRayImages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            file_name TEXT,
            uploaded_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES Patients (id) ON DELETE SET NULL
            )
        '''
                       )
        connection.commit()
        connection.close()


    @staticmethod
    def insertIntoXRayImages(patient_id, file_name):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()

        current_time = datetime.now().strftime("%d-%B-%Y %H:%M")
        cursor.execute("INSERT INTO XRayImages (patient_id, file_name, uploaded_date) VALUES (?,?,?)",
                    (patient_id, file_name, current_time))
        connection.commit()
        connection.close()

    
    @staticmethod
    def returnXRayImagesWithXrayId(img_id):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        xray_image = cursor.execute("SELECT * FROM XRayImages WHERE id = ?", (img_id,))
        return xray_image
    

    @staticmethod
    def returnXRayImagesCount():
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        count = cursor.execute("SELECT COUNT(*) FROM XRayImages")
        return count.fetchone()


    @staticmethod
    def CreateTableResults():
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE Results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            xRay_img_id INTEGER,
            result TEXT,
            covid_probability REAL,
            normal_probability REAL,
            forwarded INTEGER DEFAULT 0,
            FOREIGN KEY (patient_id) REFERENCES Patients (id) ON DELETE CASCADE,
            FOREIGN KEY (xRay_img_id) REFERENCES XRayImages (id) ON DELETE SET NULL
            )
        '''
                       )
        connection.commit()
        connection.close()


    @staticmethod
    def insertIntoResults(patient_id, xRay_img_id, result, covid_probability, normal_probability, forwarded):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Results (patient_id, xRay_img_id, result, covid_probability, normal_probability, forwarded) VALUES (?,?,?,?,?,?)",
                    (patient_id, xRay_img_id, result, covid_probability, normal_probability, forwarded))
        connection.commit()
        last_inserted_id = cursor.lastrowid
        connection.close()
        return last_inserted_id
    


    @staticmethod
    def returnResults(patient_id):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        # Fetch all the X-ray images for the patient
        cursor.execute("SELECT * FROM XRayImages WHERE patient_id = ?", (patient_id,))
        xray_images = cursor.fetchall()

        reports = []
        # Fetch the corresponding results for each X-ray image, if available
        for xray_image in xray_images:
            cursor.execute("SELECT * FROM Results WHERE xRay_img_id = ?", (xray_image[0],))
            result = cursor.fetchone()
            if result:
                reports.append({
                    'xray_image': xray_image,
                    'result': result
                })

        connection.close()
        return reports


    @staticmethod
    def checkForwardedResults(patient_id, xRay_img_id):
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        cursor.execute("SELECT forwarded FROM Results WHERE patient_id = ? AND xRay_img_id = ?",
                       (patient_id, xRay_img_id))
        result = cursor.fetchone()
        connection.close()

        if result:
            return True if result[0] == 1 else False
        else:
            return False
        

    @staticmethod
    def returnResultsWithImagesAndPatients():
        connection = s.connect("covid_tracker.db")
        cursor = connection.cursor()
        cursor.execute('''
            SELECT XRayImages.id, XRayImages.file_name, XRayImages.uploaded_date, Patients.first_name, Patients.last_name, Patients.id, Results.result, Results.covid_probability, Results.normal_probability, Results.forwarded
            FROM XRayImages
            LEFT JOIN Patients ON XRayImages.patient_id = Patients.id
            LEFT JOIN RESULTS ON XRayImages.ID = Results.ID
        ''')
        xray_imagesWithResults = cursor.fetchall()
        connection.close()
        return xray_imagesWithResults
    







