from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, User, DeviceReport, CommandLog
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SECRET_KEY'] = 'your-secret-key'

db.init_app(app)
CORS(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password=hashed, role=data['role'])
    db.session.add(user)
    db.session.commit()
    return {'status': 'user created'}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user)
        return {'status': 'logged in'}
    return {'status': 'fail'}, 401

@app.route('/api/report', methods=['POST'])
def receive_report():
    data = request.get_json()
    report = DeviceReport(**data)
    db.session.add(report)
    db.session.commit()
    return {'status': 'ok'}

@app.route('/api/devices')
@login_required
def get_devices():
    reports = DeviceReport.query.order_by(DeviceReport.timestamp.desc()).limit(100).all()
    return jsonify([r.__dict__ for r in reports])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
