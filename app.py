from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, request, redirect, url_for, session
import logging
import database
from classes import user
import send_email

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = 'super secret key'

uri = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["crime_tracker_db"]
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main_page.html')


@app.route('/register_as', methods=['GET', 'POST'])
def register_as():
    return render_template('register_as.html')


@app.route('/registration_applicant', methods=['GET', 'POST'])
def registration_applicant():
    if request.method == 'POST':
        user_data = {
            "full_name": request.form['full_name'],
            "email": request.form['email'],
            "phone_number": request.form['phone'],
            "location": request.form['location'],
            "submitter_type": request.form['submitter_type'],
            "workplace": request.form['workplace']
        }
        user_ = user.Applicant(user_data['full_name'], user_data['email'], user_data['location'], user_data['phone_number'], user_data['submitter_type'], user_data['workplace'])
        session['user_data'] = user_.to_dict()
        return redirect(url_for('password'))
    return render_template('registration_applicant.html')


@app.route('/registration_lawyer', methods=['GET', 'POST'])
def registration_lawyer():
    if request.method == 'POST':
        user_data = {
            "full_name": request.form['full_name'],
            "email": request.form['email'],
            "phone_number": request.form['phone'],
            "specialization": request.form['specialization'],
            "location": request.form['location'],
            "experience_years": request.form['experience_years'],
            "position": request.form['position'],
            "qualification_document": request.form['qualification_document'],
            "submitter_type": 'secret'
        }
        user_ = user.Lawyer(user_data['full_name'], user_data['email'], user_data['phone_number'], user_data['specialization'], user_data['location'], user_data['experience_years'], user_data['position'], user_data['qualification_document'], user_data['submitter_type'])
        session['user_data'] = user_.to_dict()
        return redirect(url_for('password'))
    return render_template('registration_lawyer.html')


@app.route('/password', methods=['GET', 'POST'])
def password():
    if request.method == 'POST':
        user_data = session.get('user_data', None)
        if user_data:
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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_data = session.get('user_data', None)
    if user_data:
        return render_template('profile.html', user_data=user_data)
    else:
        return redirect(url_for('register_as'))

@app.route('/crimes', methods=['GET', 'POST'])
def crimes():
    return render_template('crimes.html', crimes=crimes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = database.get_user(email, password)
        if user:
            session['user_data'] = user
            if user['submitter_type'] == 'secret':
                return redirect(url_for('analyst_page'))
            return redirect(url_for('home_page'))
        else:
            return 'User not found'
    return render_template('login.html')

@app.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    if request.method == 'POST':
        if 'email' in request.form:
            email = request.form['email']
            user = database.find_user_by_email(email)
            if user:
                session['user_data'] = user
                code = send_email.send_email_to_confirm(email)
                session['confirmation_code'] = code
            else:
                return render_template('forgotten_password.html', message = 'Неправильна пошта')
        elif 'code' in request.form:
            code_from_page = request.form['code']
            code_in_session = session.get('confirmation_code')
            if code_from_page == str(code_in_session):
                return redirect(url_for('confirm_password'))
            else:
                return render_template('forgotten_password.html')
    return render_template('forgotten_password.html')

@app.route('/confirm_password', methods=['GET', 'POST'])
def confirm_password():
    if request.method == 'POST':
        user = session.get('user_data', None)
        if user:
            new_password = request.form['new_password']
            confirm_pass = request.form['confirm_password']
            if new_password == confirm_pass:
                email = user['email']
                database.update_users_password(email, new_password)
                return redirect(url_for('profile'))
    return render_template('confirm_password.html')

@app.route('/analyst_page')
def analyst_page():
    return render_template('analyst_page.html')

@app.route('/crime_report', methods=['GET', 'POST'])
def crime_report():
    if request.method == 'POST':
        crime_info = {
            'applicant': request.form['applicant'],
            'applicant_number': request.form['phone'],
            'location': request.form['location'],
            'date': request.form['date'],
            'description': request.form['description'],
            'files': None,
            'weapon_type': request.form['weapon'],
            'victims': request.form['victims'],
            'vict_info': request.form['vict_info']
        }
        crime = crime.Crime(crime_info['applicant'], crime_info['applicant_number'], crime_info['location'], crime_info['date'], crime_info['description'], None, crime_info['weapon_type'], crime_info['victims'], crime_info['vict_info'])
        crime_ = dict(crime)
        crimeid = database.crime_report(crime_)
        return redirect(url_for(crime_report))
    return render_template('crime_report.html')

@app.route('/home_page')
def home_page():
    return render_template('home_page.html')

if __name__ == '__main__':
    app.run(debug=True)
