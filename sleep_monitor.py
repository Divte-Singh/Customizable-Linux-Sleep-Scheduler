import os
import time
import platform
import psutil
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import threading
from pynput import mouse, keyboard
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

CONFIG_FILE = "sleep_config.json"
settings_window = None

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {"idle_time": 300, "whitelist": []}

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

config = load_config()
last_active = time.time()

CPU_THRESHOLD = 50  
RAM_THRESHOLD = 70  

def reset_timer():
    global last_active
    last_active = time.time()

def on_mouse_move(x, y):
    reset_timer()

def on_key_press(key):
    reset_timer()

def is_system_idle():
    return time.time() - last_active > config["idle_time"]

def is_whitelisted_app_running():
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() in config["whitelist"]:
            return True
    return False

def warn_user():
    time.sleep(10)

def put_system_to_sleep():
    os_name = platform.system()
    if os_name == "Windows":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif os_name == "Linux":
        os.system("systemctl suspend")
    elif os_name == "Darwin":
        os.system("pmset sleepnow")

def monitor_activity():
    while True:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram_usage = psutil.virtual_memory().percent

        if is_system_idle() and not is_whitelisted_app_running():
            if cpu_usage < CPU_THRESHOLD and ram_usage < RAM_THRESHOLD:
                warn_user()
                if is_system_idle():
                    put_system_to_sleep()
        time.sleep(1)

def update_gui():
    remaining_time = max(0, config["idle_time"] - (time.time() - last_active))
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram_usage = psutil.virtual_memory().percent

    info_label.config(
        text=f"Time Left: {int(remaining_time)}s\n"
             f"CPU Usage: {cpu_usage}%\n"
             f"RAM Usage: {ram_usage}%"
    )
    remaining_time_label.config(text=f"Remaining Time: {int(remaining_time)}s")
    root.after(1000, update_gui)

def open_settings():
    global settings_window
    if settings_window and settings_window.winfo_exists():
        return
    
    def update_settings():
        config["idle_time"] = int(idle_time_entry.get())
        save_config(config)
        messagebox.showinfo("Settings", "Settings saved successfully!")
    
    def add_to_whitelist():
        app_path = filedialog.askopenfilename(title="Select an Application")
        if app_path:
            app_name = os.path.basename(app_path).lower()
            if app_name not in config["whitelist"]:
                config["whitelist"].append(app_name)
                whitelist_listbox.insert(tk.END, app_name)
                save_config(config)
    
    def remove_from_whitelist():
        selected = whitelist_listbox.curselection()
        for index in reversed(selected):
            app_name = whitelist_listbox.get(index)
            config["whitelist"].remove(app_name)
            whitelist_listbox.delete(index)
        save_config(config)
    
    settings_window = tk.Toplevel(root)
    settings_window.title("Sleep Mode Settings")
    
    tk.Label(settings_window, text="Idle Time (seconds):").pack()
    idle_time_entry = tk.Entry(settings_window)
    idle_time_entry.insert(0, str(config["idle_time"]))
    idle_time_entry.pack()
    
    tk.Button(settings_window, text="Save Settings", command=update_settings).pack()
    
    tk.Label(settings_window, text="Whitelist Apps:").pack()
    whitelist_listbox = tk.Listbox(settings_window, height=10, width=40)
    for app in config["whitelist"]:
        whitelist_listbox.insert(tk.END, app)
    whitelist_listbox.pack()
    
    tk.Button(settings_window, text="Add App", command=add_to_whitelist).pack()
    tk.Button(settings_window, text="Remove App", command=remove_from_whitelist).pack()

cpu_usage_list = deque(maxlen=50)
ram_usage_list = deque(maxlen=50)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6))

def update_graph(i):
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram_usage = psutil.virtual_memory().percent

    cpu_usage_list.append(cpu_usage)
    ram_usage_list.append(ram_usage)

    ax1.clear()
    ax2.clear()

    ax1.plot(cpu_usage_list, label="CPU Usage (%)", linestyle='dashed', marker='o')
    ax2.plot(ram_usage_list, label="RAM Usage (%)", linestyle='dashed', marker='o')

    ax1.axhline(CPU_THRESHOLD, linestyle='dashed', label="CPU Threshold")
    ax2.axhline(RAM_THRESHOLD, linestyle='dashed', label="RAM Threshold")

    ax1.set_ylabel("CPU Usage (%)")
    ax2.set_ylabel("RAM Usage (%)")
    ax2.set_xlabel("Samples")

    ax1.set_ylim(0, 100)
    ax2.set_ylim(0, 100)

    ax1.legend()
    ax2.legend()

root = tk.Tk()
root.title("Sleep Monitor")

info_label = tk.Label(root, text="Initializing...", font=("Arial", 14))
info_label.pack()

remaining_time_label = tk.Label(root, text="Remaining Time: --s", font=("Arial", 14))
remaining_time_label.pack()

root.after(1000, update_gui)

tk.Button(root, text="Open Settings", command=open_settings).pack()
tk.Button(root, text="Show CPU/RAM Graph", command=lambda: plt.show()).pack()

mouse_listener = mouse.Listener(on_move=on_mouse_move)
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener.start()
keyboard_listener.start()

monitor_thread = threading.Thread(target=monitor_activity, daemon=True)
monitor_thread.start()

ani = FuncAnimation(fig, update_graph, interval=1000)
plt.show(block=False)

root.mainloop()
