from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'homepage'

@app.route('/registration')
def user_registration():
    return 'registration'

if __name__ == '__main__':
    app.run()
