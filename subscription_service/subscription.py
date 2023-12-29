from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
#import os

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


@app.route('/subscription', methods=['GET','POST'])
def subscription():
    if request.method == 'POST':
        # Ottieni i valori inseriti dall'utente
        #username = request.form.get('username')
        #username = json_data['username']
        city_from = request.form['city_from']
        city_to = request.form['city_to']
        date_from = request.form['date_from']
        date_to = request.form['date_to']
        return_from = request.form['return_from']
        return_to = request.form['return_to']
        price_from = request.form['price_from']
        price_to = request.form['price_to']

        # Salva i valori nel database
        user_preferences = UserPreferences(user_id='antonioinv1@hotmail.it', city_from=city_from,city_to=city_to, date_from=date_from, date_to=date_to,
                                           return_from=return_from,
                                           return_to=return_to,
                                           price_from=price_from,
                                           price_to=price_to)
        db.session.add(user_preferences)
        db.session.commit()

        return redirect(url_for('subscription'))
        #return f"{username}"

    # Ottieni tutte le preferenze utente dal database
    # preferences = UserPreferences.query.all()

    return render_template('subscription.html')  # , preferences=preferences)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
