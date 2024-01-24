import time, requests, os
from datetime import datetime, timedelta
import logging
from threading import Thread
from flask_cors import CORS
import schedule
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_background_scheduler import BackgroundScheduler

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://an:12345@mysql_sla/sla'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

scheduler = BackgroundScheduler()
scheduler.init_app(app)
scheduler.start()


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


with app.app_context():
    db.create_all()













if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5001)
    app.run()