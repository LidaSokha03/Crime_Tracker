'''
This is a Flask application for a crime tracking system.
It allows users to register as applicants or lawyers, report crimes, and manage their profiles.
The application uses MongoDB for data storage
'''
import csv
import logging
import base64
from bson import ObjectId
from bson.binary import Binary
import certifi
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, session
import database
from classes import user
from classes import crime
import send_email
from locations import cities_from_files
from datetime import datetime
from functools import wraps


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


##########################################
###### helper functions ##################
##########################################
@app.route('/select_crime/<crime_id>', methods=['POST'])
def select_crime(crime_id):
    '''
    This function handles the selection of a crime for confirmation.
    '''
    session['crime_id'] = crime_id
    return redirect(url_for('confirmation_of_crimes'))

@app.route('/image/<crime_id>')
def get_image(crime_id):
    '''
    This function retrieves the first image of a crime from the database.
    '''
    crime = database.unvalid_crimes_collection.find_one({'_id': ObjectId(crime_id)})
    if crime and 'images' in crime and len(crime['images']) > 0:
        return Response(crime['images'][0], mimetype='image/jpeg')
    return 'Зображення не знайдено', 404

def required_login(f):
    @wraps(f)
    def function(*args, **kwargs):
        if 'user_data' not in session:
            flash('Увійдіть в свій профіль, щоб мати доступ до сторінки', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return function

def required_lawyer(f):
    @wraps(f)
    def function(*args, **kwargs):
        if 'user_data' not in session:
            flash('Увійдіть в свій профіль, щоб мати доступ до сторінки', 'danger')
            return redirect(url_for('login'))
        else:
            user_ = session['user_data']
            if user_.get('submitter_type') != 'secret':
                flash('Ваш профіль не є призначеним для виконання цих операцій', 'danger')
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return function
##########################################


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


#✅
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
            code = send_email.send_email_to_confirm(email, request.form['name'], request.form['surname'])
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


#✅
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
            company_code = request.form.get('company_code')
            if company_code != 'secret_company_code':
                flash('Невірний код компанії.', 'danger')
                return render_template('registration_lawyer.html', form_data=request.form)
            code = send_email.send_email_to_confirm(email, request.form['name'], request.form['surname'])
            session['confirmation_code'] = code
            session['email'] = email
            flash('Код надіслано на вашу пошту.', 'success')
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
                "submitter_type": 'secret',
                "company_code": request.form['company_code']
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
            user_data['password'] = database.hash_password(request.form['confirm_password'])
            submitter_type = user_data['submitter_type']
            if submitter_type == 'secret':
                userid = database.add_lawyer(user_data)
            elif submitter_type == 'default_user':
                userid = database.add_default_user(user_data)
            else:
                userid = database.add_applicant(user_data)
            if userid:
                session.pop('user_data', None)
                flash('Ви зареєстровані! Увійдіть в свій акаунт', 'success')
                return redirect(url_for('home'))
            else:
                return 'User not added'
        else:
            return redirect(url_for('register_as'))
    return render_template('password.html')


#✅
@app.route('/profile', methods=['GET', 'POST'])
@required_login
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


#додати флеші
@app.route('/crimes', methods=['GET', 'POST'])
def crimes():
    '''
    This function handles the crime report page.
    It retrieves the list of crimes from the database and renders the 'crimes.html' template.
    '''

    cities = []
    crimes = []
    show_filters = request.method == 'POST' and request.form.get('apply_filters') != 'true'

    if request.form.get('city') and not request.form.get('region'):
        flash('Оберіть область', 'danger')
        return render_template('crimes.html', crimes=crimes, cities=cities, show_filters=show_filters)
    

    if request.form.get('region'):
        if request.form.get('city'):
            cities = cities_from_files.search_cities(request.form.get('region'), request.form.get('city'))
        else:
            cities = cities_from_files.region_to_cities(request.form.get('region'))

    filters = {'date_from': None,
                'date_to': None,
                'region': None,
                'location': None, 
                'weapon_type': None}
    
    if request.form.get('date_from'):
        filters['date_from'] = datetime.strptime(request.form.get('date_from'), "%Y-%m-%d")
    if request.form.get('date_to'):
        filters['date_to'] = datetime.strptime(request.form.get('date_to'), "%Y-%m-%d")
    filters['region'] = request.form.get('region')
    if request.form.get('location'):
        filters['location'] = request.form.get('location').strip(request.form.get('location').split()[0]).strip()
    filters['weapon_type'] = request.form.get('weapon_type')
    
    
    if request.method == 'POST' and request.form.get('apply_filters') == 'true':
        print('reached here')
        filters_for_bd = {key: value for key, value in filters.items() if value is not None and value != '' and 'date' not in key}
        date_filter = {}
        if filters['date_from']:
            date_filter["$gte"] = filters['date_from']
        if filters['date_to']:
            date_filter["$lte"] = filters['date_to']
        if date_filter:
            filters_for_bd["date"] = date_filter

        print(filters_for_bd)
        docs = list(database.valid_crimes_collection.find(filters_for_bd))
    else:
        docs = list(database.valid_crimes_collection.find())
    
    if not docs:
        if request.form.get('apply_filters') == 'true':
            flash('Злочини з такими фільтрами не знайдені', 'danger')
        else:
            flash('Злочини не знайдені', 'danger')
        return render_template('crimes.html', crimes=crimes, cities=cities, filters=filters, show_filters=show_filters)


    for doc in docs:
        print(type(doc['date']))
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
            'region': doc.get('region', ''),
            'location': doc.get('location', ''),
            'date': doc.get('date', ''),
            'weapon_type': doc.get('weapon_type', ''),
            'victims': doc.get('victims', ''),
            'vict_info': doc.get('vict_info', ''),
            'description': doc.get('description', ''),
            'image_url': images[0] if images else None
        }
        crimes.append(crime_data)
    return render_template('crimes.html', crimes=crimes, cities=cities, filters=filters, show_filters=show_filters)


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
                code = send_email.send_email_to_confirm(email, user['name'], user['surname'])
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


#✅
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
                flash('Пароль успішно змінено!', 'success')
                return redirect(url_for('profile'))
    return render_template('confirm_password.html')


#✅
@app.route('/analyst_page')
@required_lawyer
def analyst_page():
    '''
    This function handles the analyst page.
    It retrieves the list of unvalidated crimes from the database and renders the 'analyst_page.html' template.
    '''
    docs = list(database.unvalid_crimes_collection.find())
    crimes = []
    for doc in docs:
        images = []
        if 'files' in doc and isinstance(doc['files'], list):
            for file in doc['files']:
                try:
                    file_data = file.get('data')
                    content_type = file.get('content_type', 'image/jpeg')
                    if not file_data or not content_type:
                        continue
                    if isinstance(file_data, Binary):
                        file_data = bytes(file_data)

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


#додати флеші
@app.route('/crime_report', methods=['GET', 'POST'])
@required_login
def crime_report():
    '''
    This function handles the crime report page.
    It collects crime information from the form and creates a Crime object.
    The crime data is stored in the database.
    '''
    crime_info = {
            'applicant': None,
            'applicant_number': None,
            'region': None,
            'city': None,
            'date': None,
            'description': None,
            'files': None,
            'weapon_type': None,
            'victims': None,
            'vict_info': None}
    cities = []
    is_required = request.method == 'POST' and request.form.get('location')

    if request.method == 'POST' and request.form.get('report_crime') != 'true':
        if request.form.get('region'):
            if request.form.get('city'):
                cities = cities_from_files.search_cities(request.form.get('region'), request.form.get('city'))
            else:
                cities = cities_from_files.region_to_cities(request.form.get('region'))
        crime_info = {
            'applicant': request.form.get('applicant'),
            'applicant_number': request.form.get('phone'),
            'region': request.form.get('region'),
            'city': request.form.get('city'),
            'date': request.form.get('date'),
            'description': request.form.get('description'),
            'files': [{'filename': f.filename,
                        'content_type': f.content_type,
                        'data': Binary(f.read())}
                    for f in request.files.getlist('files') if f.filename],
            'weapon_type': request.form.get('weapon'),
            'victims': request.form.get('victims'),
            'vict_info': request.form.get('vict_info')}
        return render_template('crime_report.html', crime_info=crime_info, cities=cities, is_required = is_required)

    if request.method == 'POST' and request.form.get('report_crime') == 'true':
        crime_info = {
            'applicant': request.form['applicant'],
            'applicant_number': request.form['phone'],
            'region': request.form['region'],
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
            crime_info['region'],
            crime_info['location'],
            crime_info['date'],
            crime_info['description'],
            crime_info['files'],
            crime_info['weapon_type'],
            crime_info['victims'],
            crime_info['vict_info'])
        crime_ = crime_.to_dict()
        act = database.crime_report(crime_)
        if act:
            flash('Звіт про злочин успішно подано!', 'success')
            return redirect(url_for('home_page'))
    return render_template('crime_report.html', crime_info=crime_info, is_required = is_required)


#✅
@app.route('/home_page')
@required_login
def home_page():
    '''
    This function handles the home page for applicants.
    '''
    return render_template('home_page.html')


#✅
@app.route('/confirmation_of_crimes', methods=['GET', 'POST'])
@required_lawyer
def confirmation_of_crimes():
    '''
    This function handles the confirmation of crimes.
    It retrieves the crime data from the session and renders the 'confirmation_of_crimes.html' template.
    '''
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
    images = []
    for file in crime.get('files', []):
        data = file.get('data')
        content_type = file.get('content_type', 'image/jpeg')
        if data:
            if isinstance(data, Binary):
                data = bytes(data)
            encoded = base64.b64encode(data).decode('utf-8')
            image_url = f"data:{content_type};base64,{encoded}"
            images.append(image_url)
    crime['image_urls'] = images
    return render_template('confirmation_of_crimes.html', crime=crime)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
