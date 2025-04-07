from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import csv
import logging
import database
from classes import user
from classes import crime
import send_email

#from flask import flash, get_flashed_messages
#це приклад того, як має виглядати висвітлення помилок

# @app.route('/crime_report', methods=['GET', 'POST'])
# def crime_report():
#     if request.method == 'POST':
#         if not request.form['applicant']:
#             flash('Поле "Заявник" обов’язкове для заповнення!', 'danger')  # тип danger — червоний alert
#             return render_template('crime_report.html')  # не перенаправляємо, щоб зберегти введені дані

#         # інші перевірки...
#         flash('Звіт про злочин успішно надіслано!', 'success')  # зелений alert
#         return redirect(url_for('crime_report'))

#     return render_template('crime_report.html')


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = 'super secret key'

uri = "mongodb+srv://lidasokha:lidasokha0303@cluster0.20mu9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["crime_tracker_db"]
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


#тут все гуд
@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    This is the main page of the application.
    It serves as the entry point for users to navigate to different sections of the application.
    The page is rendered using the 'main_page.html' template.
    '''
    return render_template('main_page.html')

#тут (для фронтів) треба поміняти кнопку з зарегатись як подавач
#на подавач або звичайний користувач (хз якось гарно сформулювати) і ті сині кнопки тре гарнюнями зробити
@app.route('/register_as', methods=['GET', 'POST'])
def register_as():
    '''
    This function handles the registration process for users.
    It allows users to choose their role (applicant or lawyer) and redirects them to the appropriate registration page.
    '''
    return render_template('register_as.html')

#поміняти ПІБ на Прізвище, Імʼя спочатку на фронті, потім в класі юзера і в кінці в цьому коді
#+додати перевірку полів на то чи правильно заповнені і додати ці вспливаючі повідомлення
#код для перевірки на пошту
#тут в вибірку ХТО ТИ було б добре було б додати типу не тока професії,
# а щей просто мінус якийсь, якщо людина без професії а от дефолт юзер
#перевірка на то, чи існує акаунт на такій пошті
@app.route('/registration_applicant', methods=['GET', 'POST'])
def registration_applicant():
    '''
    This function handles the registration process for applicants.
    It collects user data from the form and creates an Applicant object.
    The user data is stored in the session for later use.
    If the request method is POST, it redirects to the password page.
    '''
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

#поміняти ПІБ на Прізвище, Імʼя спочатку на фронті, потім в класі юзера і в кінці в цьому коді
#+додати перевірку полів на то чи правильно заповнені і додати ці вспливаючі повідомлення
#+розібратись з фотками
#код для перевірки на пошту
@app.route('/registration_lawyer', methods=['GET', 'POST'])
def registration_lawyer():
    '''
    This function handles the registration process for lawyers.
    It collects user data from the form and creates a Lawyer object.
    The user data is stored in the session for later use.
    If the request method is POST, it redirects to the password page.
    '''
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

#перевірка паролю на нормальність (мін 8 символів) + вспливаючі повідомленння
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

#додати кнопку виходу на home_page
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
@app.route('/crimes', methods=['GET', 'POST'])
def crimes():
    '''
    This function handles the crime report page.
    It retrieves the list of crimes from the database and renders the 'crimes.html' template.
    '''
    return render_template('crimes.html', crimes=crimes)

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

#висвітлювати помилки при вході
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

#якось зробити так, щоб сторінка не обновлялась після кнопки надіслати код
@app.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    '''
    This function handles the forgotten password process.
    It collects the email from the form and checks if the user exists in the database.
    If the user is found, it sends a confirmation code to the email and stores the user data in the session.
    If the user enters the correct confirmation code, it redirects to the password confirmation page.
    '''
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

#перевірка нового паролю на нормальність
@app.route('/confirm_password', methods=['GET', 'POST'])
def confirm_password():
    '''
    This function handles the password confirmation process.
    It collects the new password and confirmation password from the form.
    If the passwords match, it updates the user's password in the database and redirects to the profile page.   
    '''
    #перевірка паролю (мін 8 символів)
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

#зробити таку ж фільтрацію як і на головній сторінці
#додати можливість переходити по злочинам
@app.route('/analyst_page')
def analyst_page():
    '''
    This function handles the analyst page.
    It retrieves the list of crimes from the database and renders the 'analyst_page.html' template.
    '''
    #зробити такий же вивід непідтверджених злочинів
    #як і на головній сторінці + можливість переходити по них щоб відкривалась сторінка підтвердження
    return render_template('analyst_page.html')

#додати вспливаюче повідомлення про успішну подачу
#додати валідацію на заповненість полів
#трошки полетів дизайн
#в бд має додаватись воно з змінною valid = False
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
            'files': None,
            'weapon_type': request.form['weapon'],
            'victims': request.form['victims'],
            'vict_info': request.form['vict_info']
        }
        crime_ = crime.Crime(
            crime_info['applicant'],
            crime_info['applicant_number'],
            crime_info['location'],
            crime_info['date'],
            crime_info['description'],
            None,
            crime_info['weapon_type'],
            crime_info['victims'],
            crime_info['vict_info'])

        crime_ = crime_.to_dict()
        crime_['valid'] = False
        act = database.crime_report(crime_)
        return redirect(url_for('crime_report'))
    return render_template('crime_report.html')

#текст злетів
@app.route('/home_page')
def home_page():
    '''
    This function handles the home page for applicants.
    '''
    return render_template('home_page.html')

#тут має бути сторінку для апруву злочинів


if __name__ == '__main__':
    app.run(debug=True)
