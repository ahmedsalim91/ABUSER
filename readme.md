# ABUSER v5 🚀

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

**ABUSER v5** is a powerful Python-based automation tool designed for sending messages to Android devices via ADB (Android Debug Bridge). Featuring an intuitive Tkinter GUI and CLI support, it’s perfect for testing message automation in controlled environments. Whether you're managing multiple devices or integrating with Discord bots like **[AMD PRO MAX]**, ABUSER v5 offers flexibility and ease of use.

> ⚠️ **Important**: This tool is for **private testing** and **ethical use** only. Misuse, such as sending unsolicited or harmful messages, may violate platform policies or laws. Use responsibly.

---

## ✨ Features

- **User-Friendly GUI**: Manage names, messages, and settings with a sleek Tkinter interface.
- **Multi-Device Support**: Send messages to multiple Android devices simultaneously via ADB.
- **Customizable Messages**: Load messages from `galis.json` with optional randomization.
- **Flexible Configuration**: Adjust tap coordinates, delays, and themes via `config.json`.
- **CLI Mode**: Integrate with bots (e.g., **[AMD PRO MAX]**) for automated workflows.
- **Detailed Logging**: Track actions in `logs/abuser.log` for debugging.
- **Cross-Platform**: Runs on Windows, Linux, and macOS with Python 3.8+.

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **ADB**: Install Android Debug Bridge ([Guide](https://developer.android.com/tools/adb))
- **Android Device/Emulator**: Enable USB debugging
- **Python Package**:
  ```bash
  pip install pyperclip
  ```

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/ahmedsalim91/ABUSER.git
   cd ABUSER
   ```
2. Install dependencies:
   ```bash
   pip install pyperclip
   ```
3. Create the `~/Desktop/abuser/` directory:
   ```bash
   mkdir ~/Desktop/abuser
   ```
4. Copy `config.json` and `galis.json` to `~/Desktop/abuser/` (see samples below).
5. Connect your Android device/emulator:
   ```bash
   adb devices
   ```

---

## 🚀 Usage

### GUI Mode
Launch the tool:
```bash
python abuser.py
```

- **Names Tab**: Add names (e.g., "Alice", "Bob") and generate `temp.json` with even or alternate distribution.
- **Messages Tab**: Auto-detect devices, preview messages, and start/stop sending.
- **Galis Tab**: Add, edit, or delete messages in `galis.json`.
- **Settings Tab**: Configure delays (`delay`, `paste_delay`), tap coordinates, and randomization.

### CLI Mode
For integration with Discord bots (e.g., **[AMD PRO MAX]**):
```bash
python abuser.py --devices 127.0.0.1:5555 --names Alice,Bob
```

- `--devices`: Comma-separated ADB device IDs (e.g., `127.0.0.1:5555`).
- `--names`: Comma-separated names for message generation.

**Example Output**:
```
........................................
Alice BAAP AAGYA VAPAS !! DADDY!
```

---

## 📂 File Structure

```
ABUSER/
├── abuser.py       # Main script
├── README.md       # Documentation
├── .gitignore      # Git ignore file
├── config.json     # Configuration
├── galis.json      # Messages
├── temp.json       # Generated names (auto-created)
├── logs/           # Log files
│   └── abuser.log
```

### Sample `config.json`
Place in `~/Desktop/abuser/config.json`:
```json
{
    "devices": ["127.0.0.1:5555"],
    "delay": 1.0,
    "paste_delay": 0.3,
    "randomize": false,
    "theme": "dark",
    "tap_coords": {"x1": 1119, "y1": 654, "x2": 1197, "y2": 670}
}
```

- `delay`: Time between messages (seconds).
- `paste_delay`: Delay after pasting (adjust if messages send too fast).
- `tap_coords`: Screen coordinates for input field (`x1, y1`) and send button (`x2, y2`).

### Sample `galis.json`
Place in `~/Desktop/abuser/galis.json`:
```json
{
    "0": "BAAP AAGYA VAPAS !! DADDY!",
    "1": "Test message"
}
```

---

## 🖥️ Configuration

- **Tap Coordinates**: Adjust `tap_coords` in `config.json` to match your app’s input field and send button. Use ADB to find coordinates:
  ```bash
  adb shell getevent
  ```
- **Delays**: Increase `paste_delay` (e.g., to 0.5) if messages fail to send.
- **Randomization**: Set `"randomize": true` in `config.json` for random message selection.

---

## 📝 Notes

- **Ethical Use**: This tool is for **testing in controlled environments**. Do not use for spamming, harassment, or violating terms of service.
- **Debugging**: Check `logs/abuser.log` for detailed logs (e.g., ADB commands, errors).
- **Bot Integration**: Use CLI mode with Discord bots (e.g., `/runtool abuser/abuser.py --devices ...` in **[AMD PRO MAX]**).
- **Compatibility**: Tested with emulators (e.g., `127.0.0.1:5555`) and physical devices.

---

## 🐛 Troubleshooting

- **No Devices Detected**:
  ```bash
  adb devices
  ```
  Ensure your device is connected and USB debugging is enabled.
- **Messages Not Sending**:
  - Increase `paste_delay` in `config.json` or Settings tab.
  - Verify `tap_coords` match your app’s layout.
- **Errors**: Check `logs/abuser.log` or open a GitHub issue.

---

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

---

## 📜 License

[MIT License](LICENSE) © [Ahmed Salim](https://github.com/ahmedsalim91)

---

## 🌟 About the Developer

Built by [Ahmed Salim](https://github.com/ahmedsalim91), a passionate developer creating tools for automation and testing. Follow me on GitHub for more projects!

> **Disclaimer**: This tool is provided as-is for educational purposes. The developer is not responsible for misuse or damages caused by improper use.
