import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import logging
import pyperclip
import asyncio
import argparse
from datetime import datetime
import random

# Setup logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'abuser.log')),
        logging.StreamHandler()
    ]
)

# Paths
user_home = os.path.expanduser("~")
base_path = os.path.join(user_home, 'Desktop', 'abuser')
os.makedirs(base_path, exist_ok=True)
GALIS_FILE = os.path.join(base_path, 'galis.json')
TEMP_FILE = os.path.join(base_path, 'temp.json')
CONFIG_FILE = os.path.join(base_path, 'config.json')

# Default galis (fallback if galis.json missing)
DEFAULT_GALIS = {
    "0th": "BAAP AAGYA VAPAS !! DADDY'S HOME !!!",
    "1th": "MAAAA CHHOOD DENGE TERI!",
    # ... (add your galis.json content here)
}

# Load/save JSON helpers
def load_json(file_path, default=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {file_path}: {e}")
        return default or {}

def save_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Saved {file_path}")
    except Exception as e:
        logging.error(f"Error saving {file_path}: {e}")

# Load config
def load_config():
    default_config = {
        'devices': ['127.0.0.1:5555'],
        'delay': 1.0,
        'paste_delay': 0.3,  # Default paste delay
        'randomize': False,
        'theme': 'dark',
        'tap_coords': {'x1': 1119, 'y1': 654, 'x2': 1197, 'y2': 670}
    }
    config = load_json(CONFIG_FILE, default_config)
    # Merge defaults to handle missing keys in existing config
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
        elif isinstance(value, dict):
            # Merge nested dicts (e.g., tap_coords)
            for sub_key, sub_value in value.items():
                if sub_key not in config[key]:
                    config[key][sub_key] = sub_value
    save_json(CONFIG_FILE, config)  # Update config file with defaults
    return config

# Save config
def save_config(config):
    save_json(CONFIG_FILE, config)

# ADB helper
async def adb_command(device, command):
    try:
        process = await asyncio.create_subprocess_shell(
            f"adb -s {device} shell {command}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        logging.info(f"ADB command on {device}: {command}")
        return stdout.decode() or stderr.decode()
    except Exception as e:
        logging.error(f"ADB error on {device}: {e}")
        return str(e)

# Get ADB devices
def get_adb_devices():
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = [line.split('\t')[0] for line in result.stdout.splitlines()[1:] if '\tdevice' in line]
        
        # Filter out potential duplicates (e.g., emulator-5554 and 127.0.0.1:5555)
        filtered_devices = []
        emulator_devices = [d for d in devices if d.startswith('emulator-')]
        ip_devices = [d for d in devices if ':' in d]  # IP-based devices like 127.0.0.1:5555
        
        # If both emulator and IP-based devices are present, prefer IP-based
        if ip_devices and emulator_devices:
            filtered_devices.extend(ip_devices)  # Keep IP-based devices
            # Optionally, verify if emulator device is the same as IP-based
            for emulator in emulator_devices:
                # You can add more checks here (e.g., compare serial numbers)
                # For simplicity, skip emulator devices if IP-based exists
                logging.info(f"Skipping emulator device {emulator} as IP-based device exists")
        else:
            filtered_devices.extend(devices)  # No duplicates, keep all devices
        
        # Remove duplicates while preserving order
        seen = set()
        filtered_devices = [d for d in filtered_devices if not (d in seen or seen.add(d))]
        
        return filtered_devices
    except Exception as e:
        logging.error(f"Error getting ADB devices: {e}")
        return []
# Main App
class AbuserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AMD Abuser v5")
        self.root.geometry("600x400")
        self.config = load_config()
        self.stop_thread = False
        self.paused = False
        self.galis = load_json(GALIS_FILE, DEFAULT_GALIS)
        self.names = load_json(TEMP_FILE, {})
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill='both')

        # Names tab
        self.names_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.names_frame, text="Names")
        self.setup_names_tab()

        # Messages tab
        self.messages_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.messages_frame, text="Messages")
        self.setup_messages_tab()

        # Galis tab
        self.galis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.galis_frame, text="Galis")
        self.setup_galis_tab()

        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.setup_settings_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w')
        self.status_label.pack(fill='x')

    def setup_names_tab(self):
        # Number of persons
        ttk.Label(self.names_frame, text="Number of Persons:").grid(row=0, column=0, padx=5, pady=5)
        self.num_persons_var = tk.StringVar(value="1")
        self.num_persons_entry = ttk.Entry(self.names_frame, textvariable=self.num_persons_var, width=5)
        self.num_persons_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.names_frame, text="Update Fields", command=self.update_name_fields).grid(row=0, column=2, padx=5, pady=5)

        # Name entries
        self.name_entries_frame = ttk.Frame(self.names_frame)
        self.name_entries_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        self.name_entries = []

        # Distribution option
        self.dist_option_var = tk.StringVar(value="1")
        ttk.Radiobutton(self.names_frame, text="Even Distribution", variable=self.dist_option_var, value="1").grid(row=2, column=0, padx=5, pady=5)
        ttk.Radiobutton(self.names_frame, text="Alternate Names", variable=self.dist_option_var, value="2").grid(row=2, column=1, padx=5, pady=5)

        # Generate button
        ttk.Button(self.names_frame, text="Generate Names", command=self.generate_names).grid(row=3, column=0, columnspan=3, pady=10)

    def update_name_fields(self):
        try:
            num_persons = int(self.num_persons_var.get())
            if num_persons <= 0:
                raise ValueError("Number must be positive")
            for widget in self.name_entries_frame.winfo_children():
                widget.destroy()
            self.name_entries = []
            for i in range(num_persons):
                ttk.Label(self.name_entries_frame, text=f"Person {i+1}:").grid(row=i, column=0, padx=5, pady=2)
                entry = ttk.Entry(self.name_entries_frame)
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.name_entries.append(entry)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def generate_names(self):
        try:
            num_persons = int(self.num_persons_var.get())
            names = [entry.get() for entry in self.name_entries]
            if not all(names):
                raise ValueError("All names must be filled")
            json_data = {}
            count = 1
            if self.dist_option_var.get() == "1":
                base_names_per_person = 40 // num_persons
                extra_names = 40 % num_persons
                for i, name in enumerate(names):
                    for _ in range(base_names_per_person):
                        json_data[f"name{count}"] = name
                        count += 1
                    if i < extra_names:
                        json_data[f"name{count}"] = name
                        count += 1
            else:
                for i in range(40):
                    json_data[f"name{count}"] = names[i % num_persons]
                    count += 1
            self.names = json_data
            save_json(TEMP_FILE, json_data)
            messagebox.showinfo("Success", f"Names saved to {TEMP_FILE}")
            self.status_var.set("Names generated")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def setup_messages_tab(self):
        # Devices
        ttk.Label(self.messages_frame, text="Devices (comma-separated or auto-detect):").grid(row=0, column=0, padx=5, pady=5)
        self.devices_var = tk.StringVar(value=','.join(self.config['devices']))
        self.devices_entry = ttk.Entry(self.messages_frame, textvariable=self.devices_var)
        self.devices_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.messages_frame, text="Auto-Detect", command=self.auto_detect_devices).grid(row=0, column=2, padx=5, pady=5)

        # Preview
        ttk.Button(self.messages_frame, text="Preview Message", command=self.preview_message).grid(row=1, column=0, columnspan=3, pady=5)
        self.preview_text = tk.Text(self.messages_frame, height=3, width=50)
        self.preview_text.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Start/Stop/Pause
        ttk.Button(self.messages_frame, text="Start Sending", command=self.start_sending).grid(row=3, column=0, padx=5, pady=10)
        ttk.Button(self.messages_frame, text="Pause/Resume", command=self.pause_resume).grid(row=3, column=1, padx=5, pady=10)
        ttk.Button(self.messages_frame, text="Stop Sending", command=self.stop_sending).grid(row=3, column=2, padx=5, pady=10)

    def auto_detect_devices(self):
        devices = get_adb_devices()
        if devices:
            self.devices_var.set(','.join(devices))
            self.status_var.set(f"Detected {len(devices)} device(s)")
        else:
            messagebox.showwarning("Warning", "No ADB devices detected")

    def preview_message(self):
        if not self.names or not self.galis:
            messagebox.showerror("Error", "Generate names and load galis first")
            return
        name = self.names.get("name1", "Unknown")
        galis = random.choice(list(self.galis.values())) if self.config['randomize'] else self.galis.get("0th", "No galis")
        message = f"{'.' * 40}\n{name} {galis}"
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, message)

    def start_sending(self):
        if not self.names or not self.galis:
            messagebox.showerror("Error", "Generate names and load galis first")
            return
        devices = self.devices_var.get().strip().split(',') if self.devices_var.get() else []
        if not devices:
            messagebox.showerror("Error", "No devices specified")
            return
        self.stop_thread = False
        self.paused = False
        threading.Thread(target=self.sending_loop, args=(devices,), daemon=True).start()
        self.status_var.set("Sending messages...")

    def pause_resume(self):
        self.paused = not self.paused
        self.status_var.set("Paused" if self.paused else "Resumed")

    def stop_sending(self):
        self.stop_thread = True
        self.status_var.set("Stopped")

    def sending_loop(self, devices):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            while not self.stop_thread:
                if self.paused:
                    continue
                for idx in range(1, 41):
                    if self.stop_thread or self.paused:
                        break
                    name = self.names.get(f"name{idx}", "Unknown")
                    galis_key = f"{idx-1}th"
                    galis = random.choice(list(self.galis.values())) if self.config['randomize'] else self.galis.get(galis_key, "No galis")
                    dots10 = "\n".join(["."] * 40)
                    # message = f"{'.' * 40}\n{name} {galis}"
                    message = f'{dots10}\n{name} {galis}'
                    pyperclip.copy(message)
                    
                    # Step 1: Tap input field
                    tasks = [
                        adb_command(device, f"input tap {self.config['tap_coords']['x1']} {self.config['tap_coords']['y1']}")
                        for device in devices
                    ]
                    loop.run_until_complete(asyncio.gather(*tasks))
                    logging.info(f"Tapped input field for {devices}")
                    
                    # Step 2: Paste message
                    tasks = [
                        adb_command(device, "input keyevent 279")
                        for device in devices
                    ]
                    loop.run_until_complete(asyncio.gather(*tasks))
                    logging.info(f"Pasted message: {message} to {devices}")
                    
                    # Wait for paste to complete
                    loop.run_until_complete(asyncio.sleep(self.config['paste_delay']))
                    
                    # Step 3: Tap send
                    tasks = [
                        adb_command(device, f"input tap {self.config['tap_coords']['x2']} {self.config['tap_coords']['y2']}")
                        for device in devices
                    ]
                    loop.run_until_complete(asyncio.gather(*tasks))
                    logging.info(f"Sent message: {message} to {devices}")
                    
                    # Wait for configured delay
                    loop.run_until_complete(asyncio.sleep(self.config['delay']))
        finally:
            loop.close()
            self.status_var.set("Sending stopped")

    def setup_galis_tab(self):
        # Galis treeview
        self.galis_tree = ttk.Treeview(self.galis_frame, columns=("Key", "Value"), show='headings')
        self.galis_tree.heading("Key", text="Index")
        self.galis_tree.heading("Value", text="Galis")
        self.galis_tree.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        self.update_galis_tree()

        # Edit controls
        ttk.Label(self.galis_frame, text="Index (e.g., 0th):").grid(row=1, column=0, padx=5, pady=5)
        self.galis_key_var = tk.StringVar()
        ttk.Entry(self.galis_frame, textvariable=self.galis_key_var).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.galis_frame, text="Galis Text:").grid(row=2, column=0, padx=5, pady=5)
        self.galis_value_var = tk.StringVar()
        ttk.Entry(self.galis_frame, textvariable=self.galis_value_var).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.galis_frame, text="Add/Update", command=self.add_update_galis).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.galis_frame, text="Delete", command=self.delete_galis).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(self.galis_frame, text="Save Galis", command=self.save_galis).grid(row=3, column=2, padx=5, pady=5)

    def update_galis_tree(self):
        for item in self.galis_tree.get_children():
            self.galis_tree.delete(item)
        for key, value in self.galis.items():
            self.galis_tree.insert('', 'end', values=(key, value))

    def add_update_galis(self):
        key = self.galis_key_var.get().strip()
        value = self.galis_value_var.get().strip()
        if not key or not value:
            messagebox.showerror("Error", "Index and galis text required")
            return
        self.galis[key] = value
        self.update_galis_tree()
        self.status_var.set(f"Added/Updated galis: {key}")

    def delete_galis(self):
        selected = self.galis_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a galis to delete")
            return
        key = self.galis_tree.item(selected[0])['values'][0]
        del self.galis[key]
        self.update_galis_tree()
        self.status_var.set(f"Deleted galis: {key}")

    def save_galis(self):
        save_json(GALIS_FILE, self.galis)
        self.status_var.set("Galis saved")

    def setup_settings_tab(self):
        # Delay
        ttk.Label(self.settings_frame, text="Delay between messages (seconds):").grid(row=0, column=0, padx=5, pady=5)
        self.delay_var = tk.DoubleVar(value=self.config['delay'])
        ttk.Entry(self.settings_frame, textvariable=self.delay_var).grid(row=0, column=1, padx=5, pady=5)

        # Paste delay
        ttk.Label(self.settings_frame, text="Paste delay (seconds):").grid(row=1, column=0, padx=5, pady=5)
        self.paste_delay_var = tk.DoubleVar(value=self.config['paste_delay'])
        ttk.Entry(self.settings_frame, textvariable=self.paste_delay_var).grid(row=1, column=1, padx=5, pady=5)

        # Randomize
        self.randomize_var = tk.BooleanVar(value=self.config['randomize'])
        ttk.Checkbutton(self.settings_frame, text="Randomize galis", variable=self.randomize_var).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Tap coordinates
        ttk.Label(self.settings_frame, text="Tap 1 (x, y):").grid(row=3, column=0, padx=5, pady=5)
        self.x1_var = tk.IntVar(value=self.config['tap_coords']['x1'])
        self.y1_var = tk.IntVar(value=self.config['tap_coords']['y1'])
        ttk.Entry(self.settings_frame, textvariable=self.x1_var, width=5).grid(row=3, column=1, padx=2, pady=5)
        ttk.Entry(self.settings_frame, textvariable=self.y1_var, width=5).grid(row=3, column=2, padx=2, pady=5)
        ttk.Label(self.settings_frame, text="Tap 2 (x, y):").grid(row=4, column=0, padx=5, pady=5)
        self.x2_var = tk.IntVar(value=self.config['tap_coords']['x2'])
        self.y2_var = tk.IntVar(value=self.config['tap_coords']['y2'])
        ttk.Entry(self.settings_frame, textvariable=self.x2_var, width=5).grid(row=4, column=1, padx=2, pady=5)
        ttk.Entry(self.settings_frame, textvariable=self.y2_var, width=5).grid(row=4, column=2, padx=2, pady=5)

        # Save settings
        ttk.Button(self.settings_frame, text="Save Settings", command=self.save_settings).grid(row=5, column=0, columnspan=3, pady=10)

    def save_settings(self):
        self.config['delay'] = self.delay_var.get()
        self.config['paste_delay'] = self.paste_delay_var.get()
        self.config['randomize'] = self.randomize_var.get()
        self.config['tap_coords'] = {
            'x1': self.x1_var.get(),
            'y1': self.y1_var.get(),
            'x2': self.x2_var.get(),
            'y2': self.y2_var.get()
        }
        self.config['devices'] = self.devices_var.get().strip().split(',') if self.devices_var.get() else []
        save_config(self.config)
        self.status_var.set("Settings saved")

    def on_closing(self):
        self.stop_sending()
        self.root.destroy()

def run_cli(args):
    config = load_config()
    galis = load_json(GALIS_FILE, DEFAULT_GALIS)
    names = {}
    if args.names:
        names_list = args.names.split(',')
        count = 1
        for i in range(40):
            names[f"name{count}"] = names_list[i % len(names_list)]
            count += 1
        save_json(TEMP_FILE, names)
    else:
        names = load_json(TEMP_FILE, {})
    devices = args.devices.split(',')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        for idx in range(1, 41):
            name = names.get(f"name{idx}", "Unknown")
            galis_key = f"{idx-1}th"
            galis = random.choice(list(galis.values())) if config['randomize'] else galis.get(galis_key, "No galis")
            message = f"{'.' * 40}\n{name} {galis}"
            logging.info(f"Message to copy: {repr(message)}")  # Debug: Log the exact message
            pyperclip.copy(message)
            
            # Step 1: Tap input field
            tasks = [
                adb_command(device, f"input tap {config['tap_coords']['x1']} {config['tap_coords']['y1']}")
                for device in devices
            ]
            loop.run_until_complete(asyncio.gather(*tasks))
            
            # Step 2: Paste message
            tasks = [
                adb_command(device, "input keyevent 279")
                for device in devices
            ]
            loop.run_until_complete(asyncio.gather(*tasks))
            
            # Wait for paste to complete
            loop.run_until_complete(asyncio.sleep(config['paste_delay']))
            
            # Step 3: Tap send
            tasks = [
                adb_command(device, f"input tap {config['tap_coords']['x2']} {config['tap_coords']['y2']}")
                for device in devices
            ]
            loop.run_until_complete(asyncio.gather(*tasks))
            logging.info(f"Sent message: {message} to {devices}")
            
            # Wait for configured delay
            loop.run_until_complete(asyncio.sleep(config['delay']))
    finally:
        loop.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Abuser v5")
    parser.add_argument("--devices", default="127.0.0.1:5555", help="Comma-separated device IDs")
    parser.add_argument("--names", help="Comma-separated names for temp.json")
    args = parser.parse_args()
    if args.names or args.devices != "127.0.0.1:5555":
        run_cli(args)
    else:
        root = tk.Tk()
        app = AbuserApp(root)
        root.mainloop()
