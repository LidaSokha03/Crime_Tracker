from flask import Flask, render_template, request, redirect, url_for
import database


app = Flask(__name__)

@app.route('/')
def home():
    return 'homepage'

@app.route('/registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        user_data = {
            "name": request.form['name'],
            "surname": request.form['surname'],
            "email": request.form['email'],
            "phone_number": request.form['phone_number']
        }
        database.add_user(user_data)
        return redirect(url_for('home'))
    return 'registration.html'

@app.route('/crimes')
def crimes():
    crimes_list = database.get_crimes()
    return 'crimes.html'

@app.route('/admin')
def admin():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
