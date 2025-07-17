# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from models import db, User, ExtensionPolicy, CommandLog, DeviceReport
from datetime import datetime, timedelta
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
pending_system_actions = {}
usb_whitelist = {}

# --------------------- CONFIG ---------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/nawaz/System-Monitoring-Software/backend/data.db'  # <-- use persistent DB
app.config['SECRET_KEY'] = '4ad0fcf56a5e23464bc68e21c796c789'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
        admin = User(username="admin", password=hashed_password, role="admin")
        db.session.add(admin)
        db.session.commit()

# --------------------- HELPERS ---------------------
def log_action(user, action, device, details=None):
    try:
        log = CommandLog(user=user, action=action, device=device, details=details)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"❌ Failed to log action: {e}")

# --------------------- AUTH ---------------------
CORS(app, supports_credentials=True, origins=["http://192.168.32.87:3000"])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"status": "logged in", "username": user.username})
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

# --------------------- COMMAND LOGS ---------------------
@app.route('/api/command-log')
def command_log():
    logs = CommandLog.query.order_by(CommandLog.time.desc()).limit(100).all()
    return jsonify([{
        "user": log.user,
        "action": log.action,
        "device": log.device,
        "timestamp": log.time.strftime('%Y-%m-%d %H:%M:%S')
    } for log in logs])

@app.route('/api/audit-logs')
def get_audit_logs():
    device_id = request.args.get("device_id")
    logs = CommandLog.query.filter_by(device=device_id).order_by(CommandLog.time.desc()).all()
    return jsonify([
        {
            "user": log.user,
            "action": log.action,
            "device": log.device,
            "timestamp": log.time.isoformat(),
            "details": log.details or "-"
        } for log in logs
    ])

# --------------------- DEVICE ROUTES ---------------------
@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify(list(device_store.values()))

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

# --------------------- SYSTEM ACTIONS ---------------------
@app.route('/api/devices/<device_id>/action/shutdown', methods=['POST'])
def request_shutdown(device_id):
    pending_system_actions.setdefault(device_id, []).append('shutdown')
    log_action(current_user.username, "Shutdown", device_id)
    return jsonify({"status": "shutdown requested"})
    

@app.route('/api/devices/<device_id>/action/restart', methods=['POST'])
def request_restart(device_id):
    pending_system_actions.setdefault(device_id, []).append('restart')
    log_action(current_user.username, "Restart", device_id)
    return jsonify({"status": "restart requested"})

@app.route('/api/devices/<device_id>/action/lock', methods=['POST'])
def lock_user(device_id):
    pending_service_actions.setdefault(device_id, []).append("lock-user")
    log_action(current_user.username, "Lock User", device_id)
    return jsonify({"status": "lock queued"})

@app.route('/api/devices/<device_id>/action/unlock', methods=['POST'])
def unlock_user(device_id):
    pending_service_actions.setdefault(device_id, []).append("unlock-user")
    log_action(current_user.username, "Unlock User", device_id)
    return jsonify({"status": "unlock queued"})

@app.route('/api/devices/<device_id>/actions/pending', methods=['GET'])
def get_pending_system_actions(device_id):
    return jsonify(pending_system_actions.get(device_id, []))


@app.route('/api/devices/<device_id>/action/enable-usb', methods=['POST'])
def enable_usb_temporarily(device_id):
    data = request.json or {}
    duration_minutes = int(data.get("duration", 15))
    until_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration_minutes)
    usb_whitelist[device_id] = {"until": until_time.isoformat()}
    log_action(current_user.username, f"Enable USB for {duration_minutes} min", device_id)
    return jsonify({"status": "usb enabled", "until": until_time.isoformat()})

@app.route('/api/devices/<device_id>/action/usb-enable-pending', methods=['GET'])
def get_usb_enable_pending(device_id):
    entry = usb_whitelist.get(device_id)
    if not entry:
        return jsonify({"enable_usb": False})

    expiry = datetime.datetime.fromisoformat(entry["until"])
    if expiry > datetime.datetime.utcnow():
        return jsonify({"enable_usb": True})
    
    usb_whitelist.pop(device_id, None)
    return jsonify({"enable_usb": False})


# ---------------- EXTENSIONS ----------------

@app.route('/api/devices/<device_id>/extension-policy', methods=['GET'])
def get_policy(device_id):
    policies = ExtensionPolicy.query.filter_by(device_id=device_id, mode='whitelist').all()
    result = {}
    for p in policies:
        result.setdefault(p.ext_type, []).append(p.name)
    return jsonify(result)

@app.route('/api/devices/<device_id>/extension-policy', methods=['POST'])
def update_policy(device_id):
    data = request.json
    ExtensionPolicy.query.filter_by(device_id=device_id, mode='whitelist').delete()
    for ext_type, names in data.items():
        for name in names:
            db.session.add(ExtensionPolicy(
                device_id=device_id,
                ext_type=ext_type,
                name=name,
                mode='whitelist'
            ))
    db.session.commit()
    log_action(current_user.username, "Update Whitelist Policy", device_id, details=f"Updated: {list(data.keys())}")
    return jsonify({"status": "success"})

@app.route('/api/devices/<device_id>/extension-blacklist', methods=['GET'])
def get_blacklist(device_id):
    entries = ExtensionPolicy.query.filter_by(device_id=device_id, ext_type='blacklist').all()
    return jsonify({'vscode': [e.name for e in entries]})

@app.route('/api/devices/<device_id>/extension-blacklist', methods=['POST'])
def update_blacklist(device_id):
    data = request.json
    ExtensionPolicy.query.filter_by(device_id=device_id, ext_type='blacklist').delete()
    for name in data.get("vscode", []):
        db.session.add(ExtensionPolicy(device_id=device_id, ext_type="blacklist", name=name))
    db.session.commit()
    log_action(current_user.username, "Update Extension Blacklist", device_id, details=f"Blacklisted: {data.get('vscode')}")
    return jsonify({"status": "blacklist updated"})

@app.route('/api/devices/<device_id>/extensions', methods=['POST'])
def receive_extensions(device_id):
    data = request.json
    if device_id not in device_store:
        device_store[device_id] = {"id": device_id}
    device_store[device_id]["extensions"] = data
    return jsonify({"status": "extensions received"})

@app.route('/api/devices/<device_id>/extensions', methods=['GET'])
def get_device_extensions(device_id):
    return jsonify(device_store.get(device_id, {}).get("extensions", []))

@app.route('/api/devices/<device_id>/extensions/<ext_name>', methods=['DELETE'])
def request_extension_removal(device_id, ext_name):
    if device_id not in pending_removals:
        pending_removals[device_id] = []
    pending_removals[device_id].append(ext_name)
    log_action(current_user.username, "Remove Extension", device_id, details=ext_name)
    return jsonify({"status": "marked for removal"})

@app.route('/api/devices/<device_id>/extensions/pending-removal', methods=['GET'])
def get_pending_removals(device_id):
    return jsonify(pending_removals.get(device_id, []))


# ---------------- SOFTWARE ----------------

@app.route('/api/devices/<device_id>/software', methods=['POST'])
def receive_software(device_id):
    data = request.json
    if device_id not in device_software_store:
        device_software_store[device_id] = []
    existing = device_software_store[device_id]
    all_names = {s["name"]: s for s in existing}
    for item in data:
        all_names[item["name"]] = item
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
    log_action(current_user.username, "Uninstall Software", device_id, details=software_name)
    return jsonify({"status": "marked for uninstall"})

@app.route('/api/devices/<device_id>/software/pending-removal', methods=['GET'])
def get_software_pending_removal(device_id):
    return jsonify(pending_removals.get(device_id, []))


# ---------------- SERVICES ----------------

@app.route('/api/devices/<device_id>/services', methods=['POST'])
def receive_services(device_id):
    device_services_store[device_id] = request.json
    return jsonify({"status": "services received"}), 200

@app.route('/api/devices/<device_id>/services', methods=['GET'])
def get_services(device_id):
    return jsonify(device_services_store.get(device_id, []))

@app.route('/api/devices/<device_id>/services/<service_name>/<action>', methods=['POST'])
def queue_service_action(device_id, service_name, action):
    if device_id not in pending_service_actions:
        pending_service_actions[device_id] = []
    pending_service_actions[device_id].append({
        "service": service_name,
        "action": action,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    log_action(current_user.username, f"Service {action.capitalize()}", device_id, details=service_name)
    return jsonify({"status": "queued", "action": action})

@app.route('/api/devices/<device_id>/services/pending-actions', methods=['GET'])
def get_pending_service_actions(device_id):
    return jsonify(pending_service_actions.get(device_id, []))

@app.route('/api/devices/<device_id>/services/clear-completed', methods=['POST'])
def clear_completed_service_actions(device_id):
    completed = request.json
    if device_id in pending_service_actions:
        pending_service_actions[device_id] = [
            a for a in pending_service_actions[device_id]
            if a not in completed
        ]
    return jsonify({"status": "cleared"})


# ---------------- PROCESS KILL (RUN ONCE / INDEFINITE) ----------------

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
        log_action(current_user.username, "Kill Process", device_id, details=f"{name} ({mode})")
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

# ---------------- PATCH SYSTEM ----------------

@app.route('/api/devices/<device_id>/actions/patch-system', methods=['POST'])
def trigger_patch_system(device_id):
    if device_id not in pending_service_actions:
        pending_service_actions[device_id] = []
    pending_service_actions[device_id].append("patch-system")
    log_action(current_user.username, "Patch System", device_id)
    return jsonify({"status": "patch queued"})

@app.route('/api/devices/<device_id>/actions', methods=['GET'])
def get_pending_actions(device_id):
    return jsonify(pending_service_actions.get(device_id, []))

@app.route('/api/devices/<device_id>/actions/patch-result', methods=['POST'])
def receive_patch_result(device_id):
    data = request.json
    result = {
        "status": data.get("status", "unknown"),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    if "patch_results" not in device_store:
        device_store["patch_results"] = {}
    device_store["patch_results"][device_id] = result

    if device_id in pending_service_actions:
        pending_service_actions[device_id] = [
            a for a in pending_service_actions[device_id] if a != "patch-system"
        ]
    return jsonify({"status": "result stored"})

@app.route('/api/devices/<device_id>/actions/patch-status', methods=['GET'])
def get_patch_status(device_id):
    result = device_store.get("patch_results", {}).get(device_id)
    if not result:
        return jsonify({"status": "pending"})
    return jsonify(result)

#------------------Dashboard UI---------------

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    # Total distinct devices
    total_devices = db.session.query(DeviceReport.hostname).distinct().count()

    # Get latest report per device
    latest_reports = db.session.query(DeviceReport.hostname, func.max(DeviceReport.timestamp)).group_by(DeviceReport.hostname).all()

    online_devices = 0
    now = datetime.utcnow()

    for hostname, last_seen in latest_reports:
        if now - last_seen < timedelta(minutes=2):  # adjust as per agent interval
            online_devices += 1

    offline_devices = total_devices - online_devices

    # Recent activity (last 10 actions)
    recent_logs = CommandLog.query.order_by(CommandLog.time.desc()).limit(10).all()
    log_data = [{
        "user": log.user,
        "action": log.action,
        "device": log.device,
        "timestamp": log.time.isoformat(),
        "details": log.details
    } for log in recent_logs]

    return jsonify({
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "recent_activity": log_data
    })

@app.route('/api/devices/<device_id>/report', methods=['POST'])
def report_device(device_id):
    data = request.get_json()
    print(f"[DEBUG] Device Report from {device_id}: {data}")
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    report = DeviceReport(
        hostname=data.get('hostname'),
        os=data.get('os'),
        ip=data.get('ip'),
        status=data.get('status'),
        cpu=data.get('cpu'),
        ram=data.get('ram'),
        disk=data.get('disk'),
        timestamp=datetime.utcnow()
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Report saved successfully"}), 201

# --------------------- RUN ---------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

print("🔧 Flask is loading this app.py")
print(app.url_map)
