# NetGuard — Home Network Manager

**Parental control & network management for your home WiFi — no router password required.**

NetGuard discovers every device on your network, lets you pause internet per-device, set time schedules, and monitor activity — all from a desktop app connected to your LAN.

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  NetGuard App                     │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐ │
│  │ Dashboard │  │  Devices  │  │   Scheduler    │ │
│  └─────┬────┘  └────┬─────┘  └───────┬────────┘ │
│        └────────────┼────────────────┘           │
│                ┌────▼─────┐                      │
│                │   Core   │                      │
│                │ Scanner  │                      │
│                │ Blocker  │                      │
│                │ Scheduler│                      │
│                └────┬─────┘                      │
│                ┌────▼─────┐                      │
│                │  Network │  ← ARP (scapy)       │
│                └──────────┘                      │
└──────────────────────────────────────────────────┘
```

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| **Entry** | `src/main.py` | Sets `sys.path`, invokes `app.app.main()` |
| **App** | `src/app/` | QApplication, main window, lifecycle |
| **Core** | `src/core/` | Scanner (ARP), Blocker (ARP spoof), Scheduler, Auth |
| **UI** | `src/ui/` | PySide6 components: login, dashboard, device list, scheduler |
| **Models** | `src/models/` | Device, ScheduleRule dataclasses |
| **Utils** | `src/utils/` | Network info, MAC vendor lookup, SQLite storage |

## Tech Stack

- **Python 3.12+** — Core language
- **PySide6** — Desktop UI framework
- **scapy** — ARP scanning & spoofing
- **bcrypt** — Password hashing
- **SQLite** — Local storage (schedules, config)

## Features

- **Network Scan** — Discover all devices on your LAN (IP, MAC, vendor, hostname)
- **Per-Device Pause** — Block/unblock internet for any device via ARP spoofing
- **Scheduled Rules** — Set time-based internet access (e.g., block 10pm–7am on school nights)
- **Dashboard** — Live overview: online count, blocked count, active rules
- **Password Protection** — App entry password + admin password for settings
- **No Router Access Needed** — Works on any network you're connected to

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run (auto-elevates to root on Linux/macOS)
python launch.py

# Or manually:
#   sudo venv/bin/python src/main.py
#   python src/main.py --debug  (no root)
```

## Security

- Single password required at launch (set on first run)
- Password protects the app — no one opens it without it
- No data ever leaves your machine
- All blocking uses ARP spoofing — no router config is modified

## License

MIT
