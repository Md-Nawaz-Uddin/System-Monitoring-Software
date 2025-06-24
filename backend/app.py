from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from models import db, User, ExtensionPolicy

app = Flask(__name__)
device_store = {}
pending_removals = {}

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SECRET_KEY'] = '4ad0fcf56a5e23464bc68e21c796c789'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set True if using HTTPS

# Initialize Extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

# CORS: Allow frontend at specific IP
CORS(app, supports_credentials=True, origins=["http://192.168.32.87:3000"])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🔐 Auth Routes
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

# ✅ Devices Endpoint for UI
@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify(list(device_store.values()))

# 🧾 Command Log
@app.route('/api/command-log')
def command_log():
    logs = [
        {
            "user": "admin",
            "action": "Uninstalled VS Code",
            "timestamp": "2025-06-20 13:50"
        },
        {
            "user": "nawaz",
            "action": "Shutdown system",
            "timestamp": "2025-06-20 12:40"
        }
    ]
    return jsonify(logs)

@app.route('/api/devices/<hostname>/inventory', methods=['POST'])
def receive_inventory(hostname):
    data = request.json
    device_store.setdefault(hostname, {})['inventory'] = data
    device_store[hostname]['hostname'] = hostname
    device_store[hostname]['id'] = hostname
    device_store[hostname]['ip'] = data.get('ip', 'unknown')
    device_store[hostname]['os'] = data.get('os', 'unknown')
    device_store[hostname]['status'] = 'online'
    return jsonify({'status': 'inventory saved'})

@app.route('/api/devices/<hostname>/inventory', methods=['GET'])
def get_inventory(hostname):
    device = device_store.get(hostname)    
    if not device or 'inventory' not in device:
        return jsonify({'error': 'Inventory not found'}), 404
    return jsonify(device['inventory'])

@app.route('/api/devices/<device_id>/extension-policy', methods=['GET'])
def get_policy(device_id):
    policies = ExtensionPolicy.query.filter_by(device_id=device_id).all()
    result = {}
    for p in policies:
        result.setdefault(p.ext_type, []).append(p.name)
    return jsonify(result)

@app.route('/api/devices/<device_id>/extension-policy', methods=['POST'])
def update_policy(device_id):
    data = request.json  # should be like {"vscode": ["Prettier"], "browser": ["uBlock"]}
    ExtensionPolicy.query.filter_by(device_id=device_id).delete()
    for ext_type, names in data.items():
        for name in names:
            db.session.add(ExtensionPolicy(device_id=device_id, ext_type=ext_type, name=name))
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/devices/<device_id>/extensions', methods=['POST'])
def receive_extensions(device_id):
    data = request.json

    print(f"🔧 Incoming extensions for {device_id}: {data}")  # 🐞 Log raw input

    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of extensions"}), 400

    if device_id not in device_store:
        device_store[device_id] = {
            "id": device_id,
            "hostname": device_id,
            "status": "online",
            "ip": "unknown",
            "os": "unknown"
        }

    # Save the extensions
    device_store[device_id]["extensions"] = data
    print(f"✅ Stored extensions for {device_id}: {device_store[device_id]['extensions']}")
    return jsonify({"status": "extensions received"})


@app.route('/api/devices/<device_id>/extensions', methods=['GET'])
def get_device_extensions(device_id):
    device = device_store.get(device_id)
    if device:
        return jsonify(device.get("extensions", []))
    else:
        return jsonify([])

@app.route('/api/devices/<device_id>/extensions/<ext_name>', methods=['DELETE'])
def request_extension_removal(device_id, ext_name):
    if device_id not in pending_removals:
        pending_removals[device_id] = []
    pending_removals[device_id].append(ext_name)
    print(f"🗑️ Marked for removal: {ext_name} from {device_id}")
    return jsonify({"status": "marked for removal"})

@app.route('/api/devices/<device_id>/extensions/pending-removal', methods=['GET'])
def get_pending_removals(device_id):
    return jsonify(pending_removals.get(device_id, []))

@app.route('/api/devices/<device_id>/extension-blacklist', methods=['GET'])
def get_blacklist(device_id):
    # Reuse ExtensionPolicy table with a special type 'blacklist'
    entries = ExtensionPolicy.query.filter_by(device_id=device_id, ext_type='blacklist').all()
    blacklist = [e.name for e in entries]
    return jsonify({'vscode': blacklist})  # Match structure with frontend expectations

@app.route('/api/devices/<device_id>/extension-blacklist', methods=['POST'])
def update_blacklist(device_id):
    data = request.json  # Expecting { "vscode": ["tabnine.xyz", ...] }
    # Clear existing blacklist for this device
    ExtensionPolicy.query.filter_by(device_id=device_id, ext_type='blacklist').delete()
    # Insert new entries
    for name in data.get("vscode", []):
        db.session.add(ExtensionPolicy(device_id=device_id, ext_type="blacklist", name=name))
    db.session.commit()
    return jsonify({"status": "blacklist updated"})


# Run App
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

print("🔧 Flask is loading this app.py")
print(app.url_map)
