import requests
import json
import socket
import platform
import psutil
import subprocess
import datetime
import os
from datetime import datetime

SERVER_URL = "http://192.168.32.87:5000"
DEVICE_ID = socket.gethostname()

def get_static_inventory():
    return {
        "hostname": DEVICE_ID,
        "model": get_dmi_info("product_name"),
        "firmware": get_dmi_info("bios_version"),
        "ip": get_local_ip(),
        "os": get_os_name(),
        "cpu": platform.processor() or "Unknown",
        "gpu": get_gpu_info(),
        "ram": f"{round(psutil.virtual_memory().total / (1024**3))} GB",
        "storage": f"{round(psutil.disk_usage('/').total / (1024**3))} GB",
        "gnome": get_gnome_version(),
        "windowing": os.environ.get("XDG_SESSION_TYPE", "Unknown"),
        "kernel": platform.release(),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_usage_data():
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "cpu_usage": f"{cpu_percent}%",
        "ram_usage": f"{round(mem.used / (1024**3))} GB / {round(mem.total / (1024**3))} GB",
        "disk_usage": f"{round(disk.used / (1024**3))} GB / {round(disk.total / (1024**3))} GB"
    }

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "unknown"

def get_os_name():
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.strip().split("=")[1].strip('"')
    except:
        return platform.system()

def get_dmi_info(field):
    try:
        with open(f"/sys/class/dmi/id/{field}", "r") as f:
            return f.read().strip()
    except:
        return "Unknown"

def get_gpu_info():
    try:
        output = subprocess.check_output("lspci | grep -i vga", shell=True, text=True)
        return output.strip()
    except:
        return "Unknown"

def get_gnome_version():
    try:
        output = subprocess.check_output("gnome-shell --version", shell=True, text=True)
        return output.replace("GNOME Shell", "").strip()
    except:
        return "Unknown"

# ---------------- EXTENSIONS ----------------

def collect_extensions():
    extensions_dir = os.path.expanduser("~/.vscode/extensions")
    try:
        if not os.path.exists(extensions_dir):
            return []

        return [
            {"name": d, "type": "vscode"}
            for d in os.listdir(extensions_dir)
            if os.path.isdir(os.path.join(extensions_dir, d))
        ]
    except:
        return []

def fetch_whitelist():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/extension-policy")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return {}

def fetch_blacklist():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/extension-blacklist")
        if res.status_code == 200:
            return res.json().get("vscode", [])
    except:
        pass
    return []

def enforce_policy(installed, whitelist):
    allowed = [name.lower() for name in whitelist.get("vscode", [])]
    for ext in installed:
        if ext.lower() not in allowed:
            subprocess.run([
                'code',
                '--no-sandbox',
                '--user-data-dir=/home/nawazuddinm/.vscode-user-data',
                '--uninstall-extension',
                ext
            ])

def enforce_blacklist(installed, blacklist):
    for ext in installed:
        if ext.lower() in [b.lower() for b in blacklist]:
            ext_path = os.path.expanduser(f"~/.vscode/extensions/{ext}")
            if os.path.isdir(ext_path):
                subprocess.run(['rm', '-rf', ext_path])

def push_extensions(installed):
    extensions = [{"name": ext, "type": "vscode"} for ext in installed]
    try:
        requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/extensions", json=extensions)
    except:
        pass

def handle_extensions():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/extensions/pending-removal")
        if res.status_code == 200:
            extensions = res.json()
            for ext in extensions:
                ext_path = os.path.expanduser(f"~/.vscode/extensions/{ext}")
                if os.path.isdir(ext_path):
                    subprocess.run(['rm', '-rf', ext_path])
    except:
        pass

# ---------------- SOFTWARE ----------------

def get_installed_software():
    try:
        result = subprocess.run(['dpkg-query', '-W', '-f=${Package} ${Version}\n'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        software = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                name, version = parts[0], parts[1]
                software.append({
                    "name": name,
                    "version": version,
                    "state": "installed",
                    "path": f"/usr/bin/{name}",
                    "type": "CLI"
                })
        return software
    except:
        return []

def push_software(software_data):
    try:
        requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/software", json=software_data)
    except:
        pass

def fetch_software_uninstall_list():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/software/pending-removal")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

def uninstall_software(name):
    try:
        subprocess.run(["apt", "remove", "-y", name], capture_output=True, text=True)
    except:
        pass

def enforce_software_uninstall():
    targets = fetch_software_uninstall_list()
    for item in targets:
        if isinstance(item, dict):
            name = item.get("name")
        else:
            name = item
        if name:
            print(f"Uninstalling software: {name}")
            uninstall_software(name)

def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            processes.append({
                "name": proc.info['name'],
                "pid": proc.info['pid'],
                "path": proc.info['exe'] or "",
                "state": "running",
                "type": "process"
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def push_running_processes():
    procs = get_running_processes()
    try:
        requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/software", json=procs)
    except:
        pass


def get_services():
    services = []
    try:
        result = subprocess.run(['systemctl', 'list-units', '--type=service', '--no-pager', '--all', '--no-legend'],
                                capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            name = parts[0]
            status = parts[3] if len(parts) > 3 else "unknown"
            pid = get_service_pid(name)
            cpu, ram = get_resource_usage(pid) if pid else ("0%", "0 MB")
            description = get_service_description(name)
            startup = get_startup_type(name)
            services.append({
                "name": name,
                "description": description,
                "status": status,
                "startup": startup,
                "pid": pid,
                "cpu": cpu,
                "ram": ram
            })
    except Exception as e:
        print(f"Error fetching services: {e}")
    return services

def get_service_description(name):
    try:
        result = subprocess.run(['systemctl', 'show', name, '--property=Description'], capture_output=True, text=True)
        return result.stdout.strip().split('=')[1]
    except:
        return "N/A"

def get_startup_type(name):
    try:
        result = subprocess.run(['systemctl', 'is-enabled', name], capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "unknown"

def get_service_pid(name):
    try:
        result = subprocess.run(['systemctl', 'show', name, '--property=MainPID'], capture_output=True, text=True)
        pid_line = result.stdout.strip()
        if '=' in pid_line:
            pid = int(pid_line.split('=')[1])
            return pid if pid > 0 else None
    except:
        return None

def get_resource_usage(pid):
    try:
        p = psutil.Process(pid)
        cpu = f"{p.cpu_percent(interval=0.1)}%"
        ram = f"{round(p.memory_info().rss / 1024 / 1024)} MB"
        return cpu, ram
    except:
        return "0%", "0 MB"

def push_services():
    services = get_services()
    try:
        requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/services", json=services)
        print(" Services pushed.")
    except Exception as e:
        print(f" Failed to push services: {e}")

def fetch_pending_service_actions():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/services/pending-actions")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

def enforce_service_actions():
    actions = fetch_pending_service_actions()
    for item in actions:
        service = item.get("service")
        action = item.get("action")

        try:
            if action == "start":
                subprocess.run(["systemctl", "start", service], check=True)
            elif action == "stop":
                subprocess.run(["systemctl", "stop", service], check=True)
            elif action == "restart":
                subprocess.run(["systemctl", "restart", service], check=True)
            elif action == "disable":
                subprocess.run(["systemctl", "disable", service], check=True)
            elif action == "delete":
                subprocess.run(["systemctl", "stop", service], check=True)
                subprocess.run(["systemctl", "disable", service], check=True)
                subprocess.run(["systemctl", "mask", service], check=True)
            print(f" {action.capitalize()} executed for {service}")
        except Exception as e:
            print(f" Failed to {action} service '{service}': {e}")
        

# ---------------- MAIN PUSH ----------------

def push_data():
    inventory = {
        **get_static_inventory(),
        **get_usage_data()
    }
    try:
        requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/inventory", json=inventory)
    except:
        pass

    installed = [ext["name"] for ext in collect_extensions()]
    enforce_blacklist(installed, fetch_blacklist())
    enforce_policy(installed, fetch_whitelist())
    push_extensions(installed)
    combined = get_installed_software() + get_running_processes()
    push_software(combined)


def fetch_service_removals():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/services/pending-actions")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

def stop_and_disable_service(name):
    try:
        subprocess.run(['systemctl', 'stop', name], check=True)
        subprocess.run(['systemctl', 'disable', name], check=True)
        subprocess.run(['systemctl', 'disable', '--now', name], check=True)
        subprocess.run(['systemctl', 'mask', name], check=True)  # optional: mask to prevent restart
        print(f" Service '{name}' stopped and disabled.")
    except Exception as e:
        print(f" Failed to stop/disable service '{name}': {e}")

def handle_pending_service_removals():
    targets = fetch_service_removals()
    for service in targets:
        stop_and_disable_service(service)


# ---------------- RUN ----------------

if __name__ == "__main__":
    push_data()
    handle_extensions()
    enforce_software_uninstall()
    push_services()
    handle_pending_service_removals()
    enforce_service_actions()
