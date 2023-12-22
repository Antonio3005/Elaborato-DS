#from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Carica le variabili di ambiente da .env
#load_dotenv()



app = Flask(__name__, template_folder='templates')


# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://an:12345@mysql_users/users"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            return redirect('http://127.0.0.1:5001/subscription')
        else:
            return 'Credenziali non valide. Riprova.'

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return 'Questo username è già stato utilizzato. Scegli un altro.'

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('http://127.0.0.1:5001/subscription')

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
