import time, requests, os
from datetime import datetime, timedelta
import logging
from threading import Thread
from flask_cors import CORS
import schedule
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://an:12345@mysql_sla/sla'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
PROMETHEUS = "http://prometheus:9090/"

db = SQLAlchemy(app)
class Metrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(50), nullable=False)
    desired_value = db.Column(db.Float, nullable=False)
    job_name = db.Column(db.String(50), nullable=False)

    #violations = relationship('Violation', back_populates='sla')


# Definizione del modello delle violazioni
class Violations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sla_id = db.Column(db.Integer, db.ForeignKey('sla.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    #sla = relationship('SLA_table', back_populates='violations')

@app.post("/api/add", methods=['POST'])
def add():
    try:
        if request.method == 'POST':
            metric_n = request.form['metric_name']
            desired_v = request.form['desired_value']
            job_n = request.form['job_name']

            #istance = Metrics.query.filter_by(metric_name=metric_n, job_name=job_n).first()
            new_metric=Metrics(metric_name=metric_n, desired_value=desired_v, job_name=job_n)
            db.session.add(new_metric)
            db.session.commit()

            return jsonify({"success": True, "message": "Metrica aggiunta"})
    except Exception as e:
        return jsonify({"success": False, "message": "Si è verificato un errore durante la registrazione. Riprova più tardi."})



with app.app_context():
    db.create_all()













if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5001)
    app.run()