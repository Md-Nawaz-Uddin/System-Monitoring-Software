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

class ExtensionPolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(200))  # hostname or unique ID
    ext_type = db.Column(db.String(50))    # 'vscode' or 'browser'
    name = db.Column(db.String(200))       # Extension name
    mode = db.Column(db.String, nullable=False, default='whitelist')
    __table_args__ = (
        db.UniqueConstraint('device_id', 'ext_type', 'name', name='uq_device_ext_policy'),)

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "extension_name": self.extension_name,
            "extension_type": self.extension_type
        }
