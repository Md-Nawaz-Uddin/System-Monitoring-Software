import requests
import json
import socket
import platform
import psutil
import subprocess
import datetime
import os
import getpass
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
    
    home_dir = os.path.expanduser("~")
    user_data_dir = os.path.join(home_dir, ".vscode-user-data")

    for ext in installed:
        if ext.lower() not in allowed:
            subprocess.run([
                'code',
                '--no-sandbox',
                f'--user-data-dir={user_data_dir}',
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
                    "type": "App"
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
    cleared = []

    for item in targets:
        if isinstance(item, dict):
            name = item.get("name")
        else:
            name = item

        if name:
            print(f"Uninstalling software: {name}")
            uninstall_software(name)
            cleared.append(name)

    # Remove completed uninstalls from pending_removals
    try:
        if cleared:
            requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/software/remove-completed", json=cleared)
    except:
        pass


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
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/services/pending-actions")
        if res.status_code == 200:
            actions = res.json()
            completed = []

            for item in actions:
                service = item.get("service")
                action = item.get("action")

                if not service or not action:
                    continue

                print(f"⏳ Executing {action} on service {service}...")

                try:
                    if action == "start":
                        subprocess.run(["systemctl", "start", service])
                    elif action == "stop":
                        subprocess.run(["systemctl", "stop", service])
                    elif action == "restart":
                        subprocess.run(["systemctl", "restart", service])
                    elif action == "disable":
                        subprocess.run(["systemctl", "disable", service])
                    elif action == "delete":
                        subprocess.run(["systemctl", "stop", service])
                        subprocess.run(["systemctl", "disable", service])
                        # DO NOT MASK OR DELETE unless absolutely required:
                        # subprocess.run(["rm", f"/etc/systemd/system/{service}"])

                    completed.append(item)

                except Exception as e:
                    print(f"⚠️ Failed to execute {action} on {service}: {e}")

            # ✅ Report completed ones
            if completed:
                try:
                    requests.post(
                        f"{SERVER_URL}/api/devices/{DEVICE_ID}/services/clear-completed",
                        json=completed
                    )
                except Exception as e:
                    print("❌ Failed to report completed service actions:", e)
    except Exception as e:
        print("❌ Failed to enforce service actions:", e)
      

def fetch_pending_process_kills():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/processes/pending-kills")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

def enforce_process_kills():
    targets = fetch_pending_kill_list()  # this gives list of dicts
    for item in targets:
        if isinstance(item, dict):
            name = item.get("name")
            mode = item.get("mode", "once")
        else:
            continue

        if not name:
            continue

        print(f" Attempting to kill process: {name} [mode: {mode}]")
        success = kill_process(name)

        if success and mode == "once":
            clear_process_kill(DEVICE_ID, name)

def clear_process_kill(device_id, name):
    try:
        res = requests.delete(f"{SERVER_URL}/api/devices/{device_id}/processes/pending-kill/{name}")
        if res.status_code == 200:
            print(f" Cleared '{name}' from kill queue (once mode).")
    except Exception as e:
        print(f" Failed to clear kill for {name}: {e}")


def fetch_pending_kill_list():
    try:
        url = f"{SERVER_URL}/api/devices/{DEVICE_ID}/processes/pending-kill"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f" Failed to fetch process kill list: {e}")
        return []


def notify_backend_of_kill(name):
    try:
        requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/processes/{name}/kill/complete")
    except:
        pass

def kill_process(name):
    killed = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == name.lower():
                os.kill(proc.info['pid'], 9)  # SIGKILL
                killed.append(proc.info['pid'])
        except Exception as e:
            print(f" Failed to kill process {proc.info['pid']}: {e}")
    if killed:
        print(f" Killed process '{name}' -> PIDs: {killed}")
        return True
    else:
        print(f" No running process named '{name}' found.")
        return False

#---------------------SYSTEM ACTIONS----------------
def check_and_execute_system_actions():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/actions/pending")
        if res.status_code == 200:
            actions = res.json()
            if not actions:
                return

            for action in actions:
                if action == 'shutdown':
                    subprocess.run(['shutdown', '-h', 'now'])
                elif action == 'restart':
                    subprocess.run(['reboot'])

            # After executing actions, clear them on the server
            try:
                requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/actions/clear")
            except:
                pass

    except Exception as e:
        print(f"Error executing system action: {e}")



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


def apply_patch_update():
    try:
        update = subprocess.run(
            ['sudo', 'apt', 'update', '-y'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=300
        )
        upgrade = subprocess.run(
            ['sudo', 'apt', 'upgrade', '-y'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=600
        )
        combined_output = update.stdout.decode() + "\n" + upgrade.stdout.decode()

        # Report result back
        requests.post(
            f"{SERVER_URL}/api/devices/{DEVICE_ID}/actions/patch-result",
            json={
                "output": combined_output,
                "status": "success"
            }
        )
    except Exception as e:
        requests.post(
            f"{SERVER_URL}/api/devices/{DEVICE_ID}/actions/patch-result",
            json={
                "output": str(e),
                "status": "failed"
            }
        )

def handle_pending_actions():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/actions")
        if res.status_code == 200:
            actions = res.json()

            for action_item in actions:
                if isinstance(action_item, dict) and action_item.get("action") == "patch":
                    apply_patch_update()
    except Exception as e:
        print(f"Error handling patch actions: {e}")

def lock_current_user():
    username = getpass.getuser()
    try:
        print(f"🔒 Locking user: {username}")

        # 1. Kill all user sessions
        subprocess.run(["pkill", "-KILL", "-u", username], check=False)
        print(f"🔫 Logged out all sessions for '{username}'")

        # 2. Lock the account
        subprocess.run(["usermod", "-L", username], check=True)
        print(f"🔐 Account for '{username}' has been locked.")
        
    except Exception as e:
        print(f"❌ Failed to lock user '{username}': {e}")

def unlock_current_user():
    username = getpass.getuser()
    try:
        subprocess.run(["usermod", "-U", username], check=True)
        print(f"✅ User '{username}' unlocked.")
    except Exception as e:
        print(f"❌ Failed to unlock user '{username}':", e)


def enforce_system_actions():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/actions")
        if res.status_code == 200:
            actions = res.json()

            if "lock-user" in actions:
                lock_current_user()

            if "unlock-user" in actions:
                unlock_current_user()

    except Exception as e:
        print("❌ Failed to enforce system actions:", e)

#-------------------USB ACTION---------------


def reload_usb_modules():
    try:
        subprocess.run(['modprobe', '-r', 'usb_storage'], check=True)
        subprocess.run(['modprobe', 'usb_storage'], check=True)
        print("🔁 USB kernel modules reloaded.")
    except Exception as e:
        print(f"❌ Failed to reload USB modules: {e}")

def fetch_pending_usb_action():
    try:
        res = requests.get(f"{SERVER_URL}/api/devices/{DEVICE_ID}/action/usb-enable-pending")
        if res.status_code == 200:
            return res.json().get("enable_usb", False)
    except:
        pass
    return False

def notify_usb_enabled():
    try:
        requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/action/usb-enabled")
    except:
        pass

def enforce_usb_control():
    try:
        if fetch_pending_usb_action():
            print("🔓 Enabling USB (temp)...")
            blacklist_path = "/etc/modprobe.d/blacklist.conf"
            line = "blacklist usb_storage\n"

            # Remove blacklist line if exists
            try:
                with open(blacklist_path, "r") as f:
                    contents = f.readlines()
            except FileNotFoundError:
                contents = []

            if line in contents:
                contents.remove(line)
                with open(blacklist_path, "w") as f:
                    f.writelines(contents)
                reload_usb_modules()
                print("✅ USB access temporarily enabled.")
                notify_usb_enabled()
            else:
                print("ℹ️ USB was already enabled.")
    except Exception as e:
        print(f"❌ USB control error: {e}")

def report_device():
    try:
        report = {
            "hostname": DEVICE_ID,
            "os": get_os_name(),
            "ip": get_local_ip(),
            "status": "online",
            "cpu": psutil.cpu_percent(interval=1),         # Returns a float
            "ram": psutil.virtual_memory().percent,         # Float percentage
            "disk": psutil.disk_usage("/").percent          # Float percentage
        }
        res = requests.post(f"{SERVER_URL}/api/devices/{DEVICE_ID}/report", json=report)
        print("[Agent] Sent device report:", res.status_code, res.text)
    except Exception as e:
        print("[Agent] Error reporting device:", e)


# ---------------- RUN ----------------

if __name__ == "__main__":
    push_data()
    handle_extensions()
    enforce_software_uninstall()
    push_services()
    enforce_service_actions()
    enforce_process_kills()
    check_and_execute_system_actions()
    enforce_service_actions() 
    handle_pending_actions()
    enforce_system_actions()
    enforce_usb_control()
    report_device()
