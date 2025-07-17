from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='admin')  # e.g. admin, viewer, operator

class DeviceReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100))
    os = db.Column(db.String(200))
    ip = db.Column(db.String(100))
    status = db.Column(db.String(20))
    cpu = db.Column(db.Float)
    ram = db.Column(db.Float)
    disk = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ExtensionPolicy(db.Model):
    __tablename__ = 'extension_policies'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), nullable=False)
    ext_type = db.Column(db.String(50))       # e.g., vscode, browser, blacklist
    name = db.Column(db.String(200))          # Extension name or ID
    mode = db.Column(db.String(20))           # whitelist or blacklist

class CommandLog(db.Model):
    __tablename__ = 'command_logs'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    device = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
