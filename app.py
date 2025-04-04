from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, request, redirect, url_for, session
import logging
import database
from classes import user
import email

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
        user_ = user.Lawyer(user_data['full_name'], user_data['email'], user_data['phone_number'], user_data['specialization'], user_data['location'], user_data['experience_years'], user_data['position'], user_data['qualification_document'])
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
            return redirect(url_for('profile'))
        else:
            return 'User not found'
    return render_template('login.html')

@app.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    if request.method == 'POST':
        email = request.form['email']
        user = database.find_user_by_email(email)
        if user:
            session['user_data'] = user
            code = email.send_email_to_confirm(email)
            code_from_page = request.form['code']
            if code == code_from_page:
                redirect(url_for('password'))
    return render_template('forgotten_password.html')
if __name__ == '__main__':
    app.run(debug=True)
