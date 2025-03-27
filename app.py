from flask import Flask, render_template, request, redirect, url_for, session
import logging
import database
from classes import user

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = 'super secret key'


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
            "region": request.form['region'],
            "experience_years": request.form['experience_years'],
            "position": request.form['position'],
            "qualification_document": request.form['qualification_document'],
            "submitter_type": 'secret'
        }
        user_ = user.Lawyer(user_data['full_name'], user_data['email'], user_data['phone_number'], user_data['specialization'], user_data['region'], user_data['experience_years'], user_data['position'], user_data['qualification_document'])
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
    return render_template('profile.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = database.get_user(email, password)
        if user:
            return redirect(url_for('profile'))
        else:
            return 'User not found'
    return render_template('login.html')


@app.route('/crimes', methods=['GET', 'POST'])
def crimes():
    crimes_list = database.get_crimes()
    return 'crimes.html'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
