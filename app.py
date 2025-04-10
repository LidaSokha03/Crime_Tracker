import csv
import logging
import base64
from bson.binary import Binary
import certifi
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from bson import ObjectId
import database
from classes import user
from classes import crime
import send_email
#проблема з send_email


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = 'super secret key'

uri = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true"
client = MongoClient(uri, tlsCAFile=certifi.where(), server_api=ServerApi('1'))
db = client["crime_tracker_db"]
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


#✅
@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    This is the main page of the application.
    It serves as the entry point for users to navigate to different sections of the application.
    The page is rendered using the 'main_page.html' template.
    '''
    return render_template('main_page.html')


#✅
@app.route('/register_as', methods=['GET', 'POST'])
def register_as():
    '''
    This function handles the registration process for users.
    It allows users to choose their role (applicant or lawyer) and redirects them to the appropriate registration page.
    '''
    return render_template('register_as.html')


#проблема з регексом
@app.route('/registration_applicant', methods=['GET', 'POST'])
def registration_applicant():
    '''
    This function handles the registration process for applicants.
    It collects user data from the form and creates an Applicant object.
    The user data is stored in the session for later use.
    If the request method is POST, it redirects to the password page.
    '''
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if 'send_code' in request.form:
            if database.find_user_by_email(email):
                flash('Ця пошта вже використовується!', 'danger')
                return render_template('registration_applicant.html', form_data=request.form)
            code = send_email.send_email_to_confirm(email)
            session['confirmation_code'] = code
            session['email'] = email
            flash('Код надіслано на вашу пошту.', 'info')
            return render_template('registration_applicant.html', form_data=request.form)
        elif 'register' in request.form:
            code_from_page = request.form.get('code', '').strip()
            code_in_session = session.get('confirmation_code')
            if code_from_page != str(code_in_session):
                flash('Невірний код підтвердження.', 'danger')
                return render_template('registration_applicant.html', form_data=request.form)
            user_data = {
            "surname": request.form['surname'],
            "name": request.form['name'],
            "email": request.form['email'],
            "phone_number": request.form['phone'],
            "location": request.form['location'],
            "submitter_type": request.form['submitter_type'],
            "workplace": request.form['workplace']
        }
            try:
                user_ = user.Applicant(user_data['surname'], user_data['name'], user_data['email'], user_data['location'], user_data['phone_number'], user_data['submitter_type'], user_data['workplace'])
            except Exception as e:
                flash(f'Помилка при створенні користувача: {e}', 'danger')
                return render_template('registration_applicant.html', form_data=request.form)
            session['user_data'] = user_.to_dict()
            return redirect(url_for('password'))
    return render_template('registration_applicant.html', form_data={})


#проблема з регексом
@app.route('/registration_lawyer', methods=['GET', 'POST'])
def registration_lawyer():
    '''
    This function handles the registration process for lawyers.
    It collects user data from the form and creates a Lawyer object.
    Sends a confirmation code to the provided email, and if confirmed, redirects to password page.
    '''
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if 'send_code' in request.form:
            if database.find_user_by_email(email):
                flash('Ця пошта вже використовується!', 'danger')
                return render_template('registration_lawyer.html', form_data=request.form)
            code = send_email.send_email_to_confirm(email)
            session['confirmation_code'] = code
            session['email'] = email
            flash('Код надіслано на вашу пошту.', 'info')
            return render_template('registration_lawyer.html', form_data=request.form)
        elif 'register' in request.form:
            code_from_page = request.form.get('code', '').strip()
            code_in_session = session.get('confirmation_code')
            if code_from_page != str(code_in_session):
                flash('Невірний код підтвердження.', 'danger')
                return render_template('registration_lawyer.html', form_data=request.form)
            user_data = {
                "surname": request.form['surname'],
                "name": request.form['name'],
                "email": email,
                "phone_number": request.form['phone'],
                "specialization": request.form['specialization'],
                "location": request.form['location'],
                "experience_years": request.form['experience_years'],
                "position": request.form['position'],
                "submitter_type": 'secret'
            }
            try:
                user_ = user.Lawyer(
                    user_data['surname'], user_data['name'], user_data['email'], user_data['phone_number'],
                    user_data['specialization'], user_data['location'], user_data['experience_years'],
                    user_data['position'], '', user_data['submitter_type']
                )
            except Exception as e:
                flash(f'Помилка при створенні користувача: {e}', 'danger')
                return render_template('registration_lawyer.html', form_data=request.form)
            session['user_data'] = user_.to_dict()
            return redirect(url_for('password'))
    return render_template('registration_lawyer.html', form_data={})


#✅
@app.route('/password', methods=['GET', 'POST'])
def password():
    '''
    This function handles the password creation process for users.
    It collects the password from the form and updates the user data in the session.
    If the request method is POST, it adds the user to the database based on their role (lawyer or applicant).
    If the user is successfully added, it redirects to the home page.
    '''
    if request.method == 'POST':
        user_data = session.get('user_data', None)
        if user_data:
            password = request.form['password']
            confirm_pass = request.form['confirm_password']
            if len(password) < 8:
                flash('Пароль повинен містити щонайменше 8 символів.', 'error')
                return render_template('confirm_password.html')
            if password != confirm_pass:
                flash('Паролі не співпадають.', 'error')
                return render_template('confirm_password.html')
            user_data['password'] = request.form['confirm_password']
            submitter_type = user_data['submitter_type']
            if submitter_type == 'secret':
                userid = database.add_lawyer(user_data)
            elif submitter_type == 'default_user':
                userid = database.add_default_user(user_data)
            else:
                userid = database.add_applicant(user_data)
            if userid:
                session.pop('user_data', None)
                return redirect(url_for('home'))
            else:
                return 'User not added'
        else:
            return redirect(url_for('register_as'))
    return render_template('password.html')


#✅
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    '''
    This function handles the user profile page.
    It retrieves the user data from the session and renders the 'profile.html' template.
    If the user data is not found in the session, it redirects to the registration page.
    '''
    user_data = session.get('user_data', None)
    if user_data:
        return render_template('profile.html', user_data=user_data)
    else:
        return redirect(url_for('register_as'))

#зробити фільтраціюююю
#все полетіло
@app.route('/crimes', methods=['GET', 'POST'])
def crimes():
    '''
    This function handles the crime report page.
    It retrieves the list of crimes from the database and renders the 'crimes.html' template.
    '''
    docs = list(database.valid_crimes_collection.find())
    crimes = []

    for doc in docs:
        images = []

        if 'files' in doc and isinstance(doc['files'], list):
            for file in doc['files']:
                try:
                    file_data = file.get('data')
                    content_type = file.get('content_type')
                    if not file_data or not content_type:
                        continue
                    if isinstance(file_data, Binary):
                        file_data = bytes(file_data)
                    elif isinstance(file_data, str):
                        file_data = file_data.encode('latin1')
                    if not isinstance(file_data, bytes):
                        continue
                    encoded = base64.b64encode(file_data).decode('utf-8')
                    image_url = f"data:{content_type};base64,{encoded}"
                    images.append(image_url)
                except Exception as e:
                    print(f"{e}")
                    continue
        crime_data = {
            '_id': str(doc['_id']),
            'applicant': doc.get('applicant', ''),
            'applicant_number': doc.get('applicant_number', ''),
            'location': doc.get('location', ''),
            'date': doc.get('date', ''),
            'weapon_type': doc.get('weapon_type', ''),
            'victims': doc.get('victims', ''),
            'vict_info': doc.get('vict_info', ''),
            'description': doc.get('description', ''),
            'image_url': images[0] if images else None
        }
        crimes.append(crime_data)
    return render_template('crimes.html', crimes=crimes)


#✅
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    This function handles the login process for users.
    It collects the email and password from the form and checks if the user exists in the database.
    If the user is found, it stores the user data in the session and redirects to the appropriate page based on their role.
    If the user is not found, it displays an error message.
    '''
    if request.method == 'POST':
        email = request.form['email']
        if not database.find_user_by_email(email):
            flash('email_not_found', 'email_error')
            return render_template('login.html')
        password = request.form['password']
        user = database.find_user_by_email(email)
        if user:
            if isinstance(user['password'], str) and not user['password'].startswith("$2"):
                user['password'] = database.hash_password(password)
            if database.check_password(user['password'], password):
                session['user_data'] = user
                if user['submitter_type'] == 'secret':
                    return redirect(url_for('analyst_page'))
                return redirect(url_for('home_page'))
            else:
                flash('password_error', 'password_error')
                return render_template('login.html')
    return render_template('login.html')


#✅
@app.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    '''
    This function handles the forgotten password process.
    It collects the email from the form and checks if the user exists in the database.
    If the user is found, it sends a confirmation code to the email and stores the user data in the session.
    If the user enters the correct confirmation code, it redirects to the password confirmation page.
    '''
    if request.method == 'POST':
        if 'send_code' in request.form:
            email = request.form['email']
            user = database.find_user_by_email(email)
            if user:
                session['user_data'] = user
                code = send_email.send_email_to_confirm(email)
                session['confirmation_code'] = code
                return render_template('forgotten_password.html', form_data=request.form)
            else:
                return render_template('forgotten_password.html', message = 'Неправильна пошта', form_data = request.form)
        elif 'confirm_code' in request.form:
            code_from_page = request.form['code']
            code_in_session = session.get('confirmation_code')
            if code_from_page == str(code_in_session):
                return redirect(url_for('confirm_password'))
            else:
                return render_template('forgotten_password.html', form_data=request.form)
    return render_template('forgotten_password.html', form_data={})


#додати вспливашку про успішно змінений пароль
@app.route('/confirm_password', methods=['GET', 'POST'])
def confirm_password():
    '''
    This function handles the password confirmation process.
    It collects the new password and confirmation password from the form.
    If the passwords match, it updates the user's password in the database and redirects to the profile page.   
    '''
    if request.method == 'POST':
        user = session.get('user_data', None)
        if user:
            new_password = request.form['new_password']
            confirm_pass = request.form['confirm_password']
            if len(new_password) < 8:
                flash('Пароль повинен містити щонайменше 8 символів.', 'error')
                return render_template('confirm_password.html')
            if new_password != confirm_pass:
                flash('Паролі не співпадають.', 'error')
                return render_template('confirm_password.html')

            if new_password == confirm_pass:
                email = user['email']
                database.update_users_password(email, new_password)
                return redirect(url_for('profile'))
    return render_template('confirm_password.html')

#кнопки зі злочинами (шось придумати)
#виведення інфромації про злочини негарне (зробити таке ж як і в crimes)
#пістон з фотками
@app.route('/analyst_page')
def analyst_page():
    docs = list(database.unvalid_crimes_collection.find())
    crimes = []
    for doc in docs:
        images = []

        if 'files' in doc and isinstance(doc['files'], list):
            for file in doc['files']:
                try:
                    file_data = file.get('data')
                    content_type = file.get('content_type')
                    if not file_data or not content_type:
                        continue
                    if isinstance(file_data, Binary):
                        file_data = bytes(file_data)
                    elif isinstance(file_data, str):
                        file_data = file_data.encode('latin1')
                    if not isinstance(file_data, bytes):
                        continue
                    encoded = base64.b64encode(file_data).decode('utf-8')
                    image_url = f"data:{content_type};base64,{encoded}"
                    images.append(image_url)
                except Exception as e:
                    print(f"[WARN] Skip file: {e}")
                    continue
        crime_data = {
            '_id': str(doc['_id']),
            'applicant': doc.get('applicant', ''),
            'applicant_number': doc.get('applicant_number', ''),
            'location': doc.get('location', ''),
            'date': doc.get('date', ''),
            'weapon_type': doc.get('weapon_type', ''),
            'victims': doc.get('victims', ''),
            'vict_info': doc.get('vict_info', ''),
            'description': doc.get('description', ''),
            'image_url': images[0] if images else None
        }
        crimes.append(crime_data)
    return render_template('analyst_page.html', crimes=crimes)

#вспливаюче вікно про успішну подачу
#додати валідацію на заповненість полів
#пістон з фотками
@app.route('/crime_report', methods=['GET', 'POST'])
def crime_report():
    '''
    This function handles the crime report page.
    It collects crime information from the form and creates a Crime object.
    The crime data is stored in the database.
    '''
    if request.method == 'POST':
        crime_info = {
            'applicant': request.form['applicant'],
            'applicant_number': request.form['phone'],
            'location': request.form['location'],
            'date': request.form['date'],
            'description': request.form['description'],
            'files': [{'filename': f.filename,
                        'content_type': f.content_type,
                        'data': Binary(f.read())}
                    for f in request.files.getlist('files') if f.filename],
            'weapon_type': request.form['weapon'],
            'victims': request.form['victims'],
            'vict_info': request.form['vict_info']}
        crime_ = crime.Crime(
            crime_info['applicant'],
            crime_info['applicant_number'],
            crime_info['location'],
            crime_info['date'],
            crime_info['description'],
            crime_info['files'],
            crime_info['weapon_type'],
            crime_info['victims'],
            crime_info['vict_info'])
        crime_ = crime_.to_dict()
        act = database.crime_report(crime_)
        return redirect(url_for('crime_report'))
    return render_template('crime_report.html')


#✅
@app.route('/home_page')
def home_page():
    '''
    This function handles the home page for applicants.
    '''
    return render_template('home_page.html')

#передавання локації поміняти
#мейбі показувати фотки злочину
@app.route('/confirmation_of_crimes', methods=['GET', 'POST'])
def confirmation_of_crimes():
    crime_id = session.get('crime_id')
    if not crime_id:
        return redirect(url_for('analyst_page'))
    crime = database.unvalid_crimes_collection.find_one({"_id": ObjectId(crime_id)})
    if not crime:
        return "Crime not found", 404
    if request.method == 'POST':
        if 'confirm' in request.form:
            try:
                new_crime = dict(crime)
                del new_crime['_id']
                database.valid_crimes_collection.insert_one(new_crime)
                database.unvalid_crimes_collection.delete_one({"_id": ObjectId(crime_id)})
                session.pop('crime_id', None)
                return redirect(url_for('analyst_page'))
            except Exception as e:
                print(f"[ERROR] {e}")
                return "Error", 500
        elif 'reject' in request.form:
            database.unvalid_crimes_collection.delete_one({"_id": ObjectId(crime_id)})
            session.pop('crime_id', None)
            return redirect(url_for('analyst_page'))

    return render_template('confirmation_of_crimes.html', crime=crime)



##########################################
###### helper functions ##################
##########################################
@app.route('/select_crime/<crime_id>', methods=['POST'])
def select_crime(crime_id):
    session['crime_id'] = crime_id
    return redirect(url_for('confirmation_of_crimes'))


def region_to_cities(region):
    file_name = region + '.csv'
    return [f'{t} {n}' for t, n in csv.reader(file_name, delimiter=',')]


@app.route("/filter-section", methods=["GET", 'POST'])
def search_cities():
    region = request.args.get("region")
    query = request.args.get("query", "").lower()

    cities = region_to_cities(region)
    filtered = [city for city in cities if city.lower().split()[1].startswith(query)]

    return jsonify({"cities": filtered})


if __name__ == '__main__':
    app.run(debug=True)
