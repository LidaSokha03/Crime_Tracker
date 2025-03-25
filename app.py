
from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return 'homepage'

@app.route('/registration')
def user_registration():
    return 'registration'

@app.route('/admin')
def admin():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()