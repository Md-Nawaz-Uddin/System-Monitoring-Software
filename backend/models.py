from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))  # admin, viewer, operator

class DeviceReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100))
    os = db.Column(db.String(200))
    cpu = db.Column(db.Float)
    ram = db.Column(db.Float)
    disk = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CommandLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    action = db.Column(db.String(200))
    device = db.Column(db.String(100))
    time = db.Column(db.DateTime, default=datetime.utcnow)
