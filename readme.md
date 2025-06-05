ABUSER v5
ABUSER v5 is a Python-based automation tool designed to send messages to Android devices via ADB (Android Debug Bridge). It features a GUI for managing names, messages ("galis"), and settings, and supports CLI mode for integration with other tools, such as Discord bots. The tool is intended for private testing and ethical use only.
Features

GUI Interface: Manage names, messages, and settings via a Tkinter-based interface.
Message Automation: Send formatted messages (40 dots + name + message) to multiple Android devices.
ADB Integration: Supports multiple devices with configurable tap coordinates and delays.
Randomization: Optionally randomize messages from a JSON file.
Logging: Detailed logs saved to logs/abuser.log.
CLI Mode: Run via command-line for bot integration (e.g., with [AMD PRO MAX]).

Requirements

Python 3.8+
ADB (Android Debug Bridge) installed and configured
Python packages:pip install pyperclip


Android device(s) or emulator(s) with USB debugging enabled

Installation

Clone the repository:git clone https://github.com/ahmedsalim91/ABUSER.git
cd ABUSER


Install dependencies:pip install pyperclip


Ensure ADB is installed and devices are connected:adb devices


Place galis.json and config.json in ~/Desktop/abuser/ (see samples below).

Usage
GUI Mode
Run the tool:
python abuser.py


Names Tab: Enter names, choose distribution (even or alternate), and generate temp.json.
Messages Tab: Auto-detect devices, preview messages, and start/stop sending.
Galis Tab: Add, edit, or delete messages (galis.json).
Settings Tab: Configure delays, tap coordinates, and randomization.

CLI Mode
For bot integration (e.g., [AMD PRO MAX]):
python abuser.py --devices 127.0.0.1:5555 --names Alice,Bob


--devices: Comma-separated ADB device IDs.
--names: Comma-separated names for message generation.

Configuration
config.json
Sample configuration (~/Desktop/abuser/config.json):
{
    "devices": ["127.0.0.1:5555"],
    "delay": 1.0,
    "paste_delay": 0.3,
    "randomize": false,
    "theme": "dark",
    "tap_coords": {"x1": 1119, "y1": 654, "x2": 1197, "y2": 670}
}


paste_delay: Delay after pasting messages (adjust if messages send too fast).
tap_coords: Screen coordinates for input field and send button (adjust for your app).

galis.json
Sample messages (~/Desktop/abuser/galis.json):
{
    "0": "BAAP AAGYA VAPAS !! DADDY!",
    "1": "Test message"
}

File Structure
ABUSER/
├── abuser.py       # Main script
├── README.md       # Documentation
├── .gitignore      # Git ignore file
├── config.json     # Configuration
├── galis.json          # Messages
├── temp.json       # Generated names (auto-created)
├── logs/           # Log files
│   └── abuser.log

Notes

Ethical Use: Use only for private testing or with explicit permission. Misuse may violate platform policies or terms of service.
Logs: Check logs/abuser.log for debugging.
Integration: Compatible with Discord bots via CLI mode (e.g., /runtool abuser2/abuser2.py --devices ...).
Support: For issues, open a GitHub issue or contact the repo owner.

License
MIT License (see LICENSE file, to be added).

Developed by Ahmed Salim
