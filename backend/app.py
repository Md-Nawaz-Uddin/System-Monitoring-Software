from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from models import db, User, ExtensionPolicy
import datetime
import traceback
import psutil

app = Flask(__name__)
device_store = {}
pending_removals = {}
device_software_store = {}
pending_service_actions = {}
device_services_store = {}
pending_process_kills = {}
EXTENSION_BLACKLISTS = {}


# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SECRET_KEY'] = '4ad0fcf56a5e23464bc68e21c796c789'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set True if using HTTPS

# Initialize Extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
        admin = User(username="admin", password=hashed_password)
        db.session.add(admin)
        db.session.commit()

# CORS: Allow frontend at specific IP
CORS(app, supports_credentials=True, origins=["http://192.168.32.87:3000"])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#  Auth Routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"status": "logged in", "username": user.username})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

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

#  Devices Endpoint for UI
@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify(list(device_store.values()))

#  Command Log
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

# ---- ROUTES FOR EXTENSIONS------

@app.route('/api/devices/<device_id>/extension-policy', methods=['GET'])
def get_policy(device_id):
    policies = ExtensionPolicy.query.filter_by(device_id=device_id, mode='whitelist').all()
    result = {}
    for p in policies:
        result.setdefault(p.ext_type, []).append(p.name)
    return jsonify(result)

@app.route('/api/devices/<device_id>/extension-policy', methods=['POST'])
def update_policy(device_id):
    data = request.json  # Expected: {"vscode": ["ext1", "ext2"], "browser": [...]}

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid payload"}), 400

    try:
        # Delete existing whitelist entries
        ExtensionPolicy.query.filter_by(device_id=device_id, mode='whitelist').delete()
        db.session.commit()

        # Add new whitelist entries
        for ext_type, names in data.items():
            for name in names:
                db.session.add(ExtensionPolicy(
                    device_id=device_id,
                    ext_type=ext_type,
                    name=name,
                    mode='whitelist'
                ))
        db.session.commit()
        return jsonify({"status": "whitelist updated"})

    except Exception as e:
        print(f"❌ Failed to update whitelist: {e}")
        return jsonify({"error": "Server failed to update whitelist"}), 500


@app.route('/api/devices/<device_id>/extensions', methods=['POST'])
def receive_extensions(device_id):
    data = request.json
    print(f"🔧 Incoming extensions for {device_id}: {data}")

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

# ---- BLACKLIST (now in-memory, not DB) ----

@app.route('/api/devices/<device_id>/extension-blacklist', methods=['GET'])
def get_blacklist(device_id):
    return jsonify({'vscode': EXTENSION_BLACKLISTS.get(device_id, [])})

@app.route('/api/devices/<device_id>/extension-blacklist', methods=['POST'])
def update_blacklist(device_id):
    data = request.json  # Expecting { "vscode": ["tabnine", "some.other.id"] }
    EXTENSION_BLACKLISTS[device_id] = data.get("vscode", [])
    print(f"🔒 Updated in-memory blacklist for {device_id}: {EXTENSION_BLACKLISTS[device_id]}")
    return jsonify({"status": "blacklist updated"})


@app.route('/api/devices/<device_id>/software', methods=['POST'])
def receive_software(device_id):
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Invalid format"}), 400

    if device_id not in device_software_store:
        device_software_store[device_id] = []

    # Merge new software/processes with existing
    existing = device_software_store[device_id]
    all_names = {s["name"]: s for s in existing}

    for item in data:
        all_names[item["name"]] = item  # update or add

    device_software_store[device_id] = list(all_names.values())
    return jsonify({"status": "software received"}), 200


@app.route('/api/devices/<device_id>/software', methods=['GET'])
def get_software_info(device_id):
    return jsonify(device_software_store.get(device_id, []))

@app.route('/api/devices/<device_id>/software/<software_name>', methods=['DELETE'])
def request_software_uninstall(device_id, software_name):
    if device_id not in pending_removals:
        pending_removals[device_id] = []
    pending_removals[device_id].append(software_name)
    print(f" Software marked for uninstall: {software_name} from {device_id}")
    return jsonify({"status": "marked for uninstall"})

@app.route('/api/devices/<device_id>/software/pending-removal', methods=['GET'])
def get_software_pending_removal(device_id):
    return jsonify(pending_removals.get(device_id, []))

# 1. POST: Receive services from agent
@app.route('/api/devices/<device_id>/services', methods=['POST'])
def receive_services(device_id):
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Invalid format"}), 400
    device_services_store[device_id] = data
    return jsonify({"status": "services received"}), 200

# 2. GET: Fetch current services for frontend
@app.route('/api/devices/<device_id>/services', methods=['GET'])
def get_services(device_id):
    return jsonify(device_services_store.get(device_id, []))

# 3. POST: Queue a service action (start/stop/restart/disable/delete)
@app.route('/api/devices/<device_id>/services/<service_name>/<action>', methods=['POST'])
def queue_service_action(device_id, service_name, action):
    valid_actions = ["start", "stop", "restart", "disable", "delete"]
    if action not in valid_actions:
        return jsonify({"error": "Invalid action"}), 400

    if device_id not in pending_service_actions:
        pending_service_actions[device_id] = []

    pending_service_actions[device_id].append({
        "service": service_name,
        "action": action,
        "timestamp": datetime.datetime.now().isoformat()
    })

    print(f"📦 Queued service action: {action} on {service_name} for {device_id}")
    return jsonify({"status": "queued", "action": action})

# 4. GET: Agent polls this to fetch all pending actions
@app.route('/api/devices/<device_id>/services/pending-actions', methods=['GET'])
def get_pending_service_actions(device_id):
    return jsonify(pending_service_actions.get(device_id, []))

@app.route('/api/devices/<device_id>/processes/<name>/kill', methods=['POST'])
def queue_process_kill(device_id, name):
    data = request.json or {}
    mode = data.get("mode", "once")  # mode can be 'once' or 'forever'

    if device_id not in pending_process_kills:
        pending_process_kills[device_id] = []

    # Avoid duplicates
    exists = any(entry["name"] == name and entry["mode"] == mode for entry in pending_process_kills[device_id])
    if not exists:
        pending_process_kills[device_id].append({
            "name": name,
            "mode": mode,
            "timestamp": datetime.datetime.now().isoformat()
        })
        print(f"📦 Queued process kill: {name} ({mode}) for {device_id}")
    return jsonify({"status": "queued", "process": name, "mode": mode})


@app.route('/api/devices/<device_id>/processes/pending-kill', methods=['GET'])
def get_pending_process_kills(device_id):
    return jsonify(pending_process_kills.get(device_id, []))

@app.route("/api/devices/<device_id>/processes/<name>/kill/complete", methods=["POST"])
def clear_kill_queue(device_id, name):
    if device_id in pending_process_kill:
        pending_process_kill[device_id] = [p for p in pending_process_kill[device_id] if p != name]
    return jsonify({"status": "removed", "target": name})

@app.route('/api/devices/<device_id>/processes/pending-kill/<name>', methods=['DELETE'])
def delete_pending_kill(device_id, name):
    if device_id not in pending_process_kills:
        return jsonify({"message": "Device not found"}), 404

    before = pending_process_kills[device_id]
    print(f"🔍 Before delete: {before}")

    updated = []
    deleted = False

    for item in before:
        # Match exactly name AND mode
        if item.get("name") == name and item.get("mode") == "once":
            deleted = True
            continue  # Skip this item (delete)
        updated.append(item)

    if not deleted:
        return jsonify({"message": "No matching kill entry found"}), 404

    pending_process_kills[device_id] = updated
    print(f"✅ Cleared 'once' mode kill for '{name}' on {device_id}")
    return jsonify({"status": "cleared"}), 200


# Run App
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

print("🔧 Flask is loading this app.py")
print(app.url_map)
