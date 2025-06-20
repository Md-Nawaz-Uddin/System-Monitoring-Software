from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from models import db, User

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SECRET_KEY'] = '4ad0fcf56a5e23464bc68e21c796c789'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Only True if using HTTPS

# Initialize Extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

# CORS: Allow frontend at http://localhost:3000
CORS(app, supports_credentials=True, origins=["http://192.168.32.87:3000"])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({'status': 'logged in'})
    return jsonify({'status': 'fail'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'logged out'})

@app.route('/api/current-user', methods=['GET'])
def current_user_info():
    if current_user.is_authenticated:
        return jsonify({
            'username': current_user.username,
            'role': current_user.role
        })
    return jsonify({'status': 'unauthenticated'}), 401

@app.route('/api/me')
@login_required
def me():
    return jsonify(username=current_user.username, role=current_user.role)

@app.route('/api/devices', methods=['GET'])
@login_required
def get_devices():
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

print("🔧 Flask is loading this app.py")
print(app.url_map)

