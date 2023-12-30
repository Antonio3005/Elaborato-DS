from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
#import os
from datetime import datetime

app = Flask(__name__)
app.template_folder = 'templates'

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://an:12345@mysql_subscription/subscription"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    city_from = db.Column(db.String(255), nullable=False)
    city_to = db.Column(db.String(255), nullable=False)
    date_from = db.Column(db.String(255), nullable=False)
    date_to = db.Column(db.String(255), nullable=False)
    return_from = db.Column(db.String(255), nullable=False)
    return_to = db.Column(db.String(255), nullable=False)
    price_from = db.Column(db.String(255), nullable=False)
    price_to = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validate_preferences(city_from, city_to, date_from, date_to, return_from, return_to, price_from, price_to):
    # Verifica che price_from e price_to non siano negativi
    if float(price_from) < 1 or float(price_to) < 1:
        raise ValueError("Il prezzo non può essere minore di 1.")

    # Verifica che le date siano nel formato corretto e non antecedenti a oggi
    today = datetime.now().strftime("%d/%m/%Y")
    if not is_valid_date(date_from) or not is_valid_date(date_to) or date_from < today or date_to < today:
        raise ValueError("Formato data non valido o data antecedente a oggi.")

    if not is_valid_date(return_from) or not is_valid_date(return_to) or return_from < today or return_to < today:
        raise ValueError("Formato data di ritorno non valido o data antecedente a oggi.")

    # Verifica che le date di ritorno non siano antecedenti a quelle di andata
    if return_from < date_from or return_to < date_to:
        raise ValueError("Le date di ritorno non possono essere antecedenti a quelle di andata.")

    # Verifica che city_from e city_to siano diverse
    if city_from == city_to:
        raise ValueError("La città di partenza non può essere uguale a quella di destinazione.")

    # Verifica che price_from non sia maggiore di price_to
    if float(price_from) > float(price_to):
        raise ValueError("Il prezzo minimo non può essere maggiore del prezzo massimo.")



@app.route('/subscription/<username>', methods=['GET','POST'])
def subscription(username):
    if request.method == 'POST':
        try:
            city_from = request.form['city_from']
            city_to = request.form['city_to']
            date_from = request.form['date_from']
            date_to = request.form['date_to']
            return_from = request.form['return_from']
            return_to = request.form['return_to']
            price_from = request.form['price_from']
            price_to = request.form['price_to']

            try:
                validate_preferences(city_from, city_to, date_from, date_to, return_from, return_to, price_from, price_to)
            except ValueError as ve:
                return f"Errore durante la registrazione: {ve}"

            # Salva i valori nel database
            user_preferences = UserPreferences(user_id=username, city_from=city_from,city_to=city_to, date_from=date_from, date_to=date_to,
                                               return_from=return_from,
                                               return_to=return_to,
                                               price_from=price_from,
                                               price_to=price_to)
            db.session.add(user_preferences)
            db.session.commit()

            return redirect(url_for('subscription', username=username))
        except ValueError as ve:
            return f"Errore durante la registrazione: {ve}"

    return render_template('subscription.html', username=username)  # , preferences=preferences)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
