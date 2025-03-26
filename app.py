from flask import Flask, render_template, request, redirect, url_for
import database


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main_page.html')


@app.route('/register_as', methods=['GET', 'POST'])
def register_as():
    if request.method == 'POST':
        if request.form['register_as'] == 'applicant':
            return redirect(url_for('registration_applicant'))
        elif request.form['register_as'] == 'lawyer':
            return redirect(url_for('registration_lawyer'))
    return render_template('register_as.html')


@app.route('/registration_applicant', methods=['GET', 'POST'])
def registration_applicant():
    if request.method == 'POST':
        user_data = {
            "name": request.form['name'],
            "surname": request.form['surname'],
            "email": request.form['email'],
            "phone_number": request.form['phone_number']
        }
        database.add_user(user_data)
        return redirect(url_for('home'))
    return render_template('registration_applicant.html')


@app.route('/registration_lawyer', methods=['GET', 'POST'])
def registration_lawyer():
    if request.method == 'POST':
        user_data = {
            "name": request.form['name'],
            "surname": request.form['surname'],
            "email": request.form['email'],
            "phone_number": request.form['phone_number']
        }
        database.add_user(user_data)
        return redirect(url_for('home'))
    return render_template('registration_lawyer.html')


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


@app.route('/password', methods=['GET', 'POST'])
def password():
    return render_template('password.html')

@app.route('/crimes', methods=['GET', 'POST'])
def crimes():
    crimes_list = database.get_crimes()
    return 'crimes.html'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
