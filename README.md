# covid-tracker-app
The COVID-19 Tracker is a web application built with Flask that allows doctors and patients to track and manage COVID-19 cases. It provides functionalities for doctors to generate and forward results, and for patients to view their reports.

You can find already Trained Model on Google drive: [CNN_Covid19_Xray_V1.h5](https://drive.google.com/file/d/1GIz1F3G4p2sxWYFR8TYqSTNpl25NnX6Y/view?usp=sharing)


# Features
- **Doctor Dashboard:** Doctors can view a list of X-ray images uploaded by patients, generate results based on a machine learning model, and forward the results to patients.
- **Patient Dashboard:** Patients can view their X-ray images and the corresponding results generated by doctors.
- **Predictive Model:** The app uses a machine learning model to predict whether an X-ray image indicates COVID-19 or is normal.
- **SQLite3 Database:** The app utilizes a SQLite3 database to store X-ray images, patient information, and generated results.

# Technologies Used
- Flask: A Python web framework used for building the application.
- SQLite3: A lightweight database management system used for data storage.
- Bootstrap: A front-end framework used for responsive and attractive UI.
- Machine Learning (ML): A trained ML model is used to predict COVID-19 cases based on X-ray images. You can find dataset [here](https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database).

# Installation and Setup
- Clone the repository: `git clone <repository_url>`
- Create a virtual environment: `python -m venv venv`
- Activate the virtual environment: `source venv/bin/activate` (for Linux/Mac) or `venv\Scripts\activate` (for Windows)
- Install the required dependencies: `pip install -r requirements.txt`
- Run the Flask application: `flask run`

# Usage
- Access the web application at [http://localhost:5000](http://localhost:5000) (or as per Flask's default configuration).
- Doctors can log in, view X-ray images, generate results, and forward them to patients.
- Patients can log in, view their X-ray images, and check the generated results.

# Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your proposed changes.

# License
This project is licensed under the MIT License.
