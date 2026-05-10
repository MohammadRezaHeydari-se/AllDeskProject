import sqlite3
import os
from datetime import time, datetime
from typing import List, Optional
from ..models.device import Device
from ..models.rule import ScheduleRule

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "netguard.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS devices (
            mac TEXT PRIMARY KEY,
            ip TEXT NOT NULL,
            hostname TEXT DEFAULT 'Unknown',
            vendor TEXT DEFAULT 'Unknown',
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            online INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS schedule_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            start_hour INTEGER DEFAULT 22,
            start_minute INTEGER DEFAULT 0,
            end_hour INTEGER DEFAULT 7,
            end_minute INTEGER DEFAULT 0,
            days TEXT DEFAULT '0,1,2,3,4,5,6'
        );
    """)
    conn.commit()
    conn.close()


def get_setting(key: str, default: str = "") -> str:
    conn = _get_conn()
    cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
        (key, value, value),
    )
    conn.commit()
    conn.close()


def save_devices(devices: List[Device]):
    conn = _get_conn()
    now = datetime.now().isoformat()
    for d in devices:
        conn.execute(
            """INSERT INTO devices (mac, ip, hostname, vendor, first_seen, last_seen, online, blocked)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(mac) DO UPDATE SET
                 ip = excluded.ip,
                 hostname = excluded.hostname,
                 vendor = excluded.vendor,
                 last_seen = excluded.last_seen,
                 online = excluded.online,
                 blocked = excluded.blocked""",
            (d.mac, d.ip, d.hostname, d.vendor, d.first_seen.isoformat(), now, int(d.online), int(d.blocked)),
        )
    conn.commit()
    conn.close()


def load_devices() -> List[Device]:
    conn = _get_conn()
    cursor = conn.execute("SELECT * FROM devices ORDER BY online DESC, last_seen DESC")
    devices = []
    for row in cursor:
        devices.append(Device(
            mac=row["mac"],
            ip=row["ip"],
            hostname=row["hostname"],
            vendor=row["vendor"],
            first_seen=datetime.fromisoformat(row["first_seen"]),
            last_seen=datetime.fromisoformat(row["last_seen"]),
            online=bool(row["online"]),
            blocked=bool(row["blocked"]),
        ))
    conn.close()
    return devices


def save_rules(rules: List[ScheduleRule]):
    conn = _get_conn()
    conn.execute("DELETE FROM schedule_rules")
    for r in rules:
        days_str = ",".join(str(d) for d in (r.days or list(range(7))))
        conn.execute(
            """INSERT INTO schedule_rules (mac, enabled, start_hour, start_minute, end_hour, end_minute, days)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (r.mac, int(r.enabled), r.start_time.hour, r.start_time.minute,
             r.end_time.hour, r.end_time.minute, days_str),
        )
    conn.commit()
    conn.close()


def load_rules() -> List[ScheduleRule]:
    conn = _get_conn()
    cursor = conn.execute("SELECT * FROM schedule_rules")
    rules = []
    for row in cursor:
        rules.append(ScheduleRule(
            id=row["id"],
            mac=row["mac"],
            enabled=bool(row["enabled"]),
            start_time=time(row["start_hour"], row["start_minute"]),
            end_time=time(row["end_hour"], row["end_minute"]),
            days=[int(x) for x in row["days"].split(",") if x],
        ))
    conn.close()
    return rules
