from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QFrame, QLabel, QApplication,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from typing import List

from ..ui.dashboard import DashboardView
from ..ui.device_list import DeviceListView
from ..ui.device_detail import DeviceDetailView
from ..ui.scheduler_ui import SchedulerView
from ..ui.settings import SettingsView

from ..models.device import Device
from ..models.rule import ScheduleRule

from ..core.scanner import NetworkScanner
from ..core.blocker import DeviceBlocker
from ..core.scheduler import Scheduler


class NavButton(QPushButton):
    def __init__(self, text: str, icon_char: str = ""):
        super().__init__(f"  {icon_char}  {text}" if icon_char else text)
        self.setCheckable(True)
        self.setFixedHeight(42)
        self.setStyleSheet("""
            NavButton {
                background: transparent; color: #aaa; border: none;
                text-align: left; padding: 8px 16px; font-size: 13px;
                border-radius: 6px;
            }
            NavButton:hover {
                background: #2a2a2a; color: #fff;
            }
            NavButton:checked {
                background: #2196F3; color: white; font-weight: bold;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._devices: List[Device] = []
        self._rules: List[ScheduleRule] = []

        self.scanner = NetworkScanner()
        self.blocker = DeviceBlocker()
        self.scheduler = Scheduler(
            block_callback=self._on_schedule_block,
            unblock_callback=self._on_schedule_unblock,
            is_blocked_fn=lambda mac: self.blocker.is_blocked(mac),
        )

        self.setWindowTitle("NetGuard - Home Network Manager")
        self.setMinimumSize(960, 640)
        self._setup_ui()
        self._connect_signals()

        self.scanner.set_callback(self._on_scan_complete)
        self.scanner.start_continuous_scan(interval=30)
        self.scheduler.start()

        QTimer.singleShot(2000, self._do_initial_scan)

    def _setup_ui(self):
        central = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background: #1a1a1a; border-right: 1px solid #2a2a2a;")
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(4)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)

        app_title = QLabel("NetGuard")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff; padding: 8px 12px;")
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacing(16)

        self.nav_dashboard = NavButton("Dashboard", "📊")
        self.nav_devices = NavButton("Devices", "📡")
        self.nav_scheduler = NavButton("Schedules", "⏰")
        self.nav_settings = NavButton("Settings", "⚙")

        sidebar_layout.addWidget(self.nav_dashboard)
        sidebar_layout.addWidget(self.nav_devices)
        sidebar_layout.addWidget(self.nav_scheduler)
        sidebar_layout.addSpacing(16)
        sidebar_layout.addWidget(self.nav_settings)
        sidebar_layout.addStretch()

        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #555; font-size: 11px; padding: 8px 12px;")
        sidebar_layout.addWidget(version_label)

        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)

        self.stack = QStackedWidget()
        self.dashboard = DashboardView()
        self.device_list = DeviceListView()
        self.device_detail = DeviceDetailView()
        self.scheduler_view = SchedulerView()
        self.settings_view = SettingsView()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.device_list)
        self.stack.addWidget(self.device_detail)
        self.stack.addWidget(self.scheduler_view)
        self.stack.addWidget(self.settings_view)

        main_layout.addWidget(self.stack)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.nav_dashboard.clicked.connect(lambda: self._navigate_to(0))
        self.nav_devices.clicked.connect(lambda: self._navigate_to(1))
        self.nav_scheduler.clicked.connect(lambda: self._navigate_to(3))
        self.nav_settings.clicked.connect(lambda: self._navigate_to(4))

        self.nav_dashboard.setChecked(True)

    def _connect_signals(self):
        self.device_list.device_selected.connect(self._on_device_selected)
        self.device_list.scan_btn.clicked.connect(self._do_manual_scan)
        self.device_detail.back.connect(lambda: self._navigate_to(1))
        self.device_detail.toggle_block.connect(self._on_toggle_block)
        self.scheduler_view.rules_changed.connect(self._on_rules_changed)

    def _navigate_to(self, index: int):
        self.stack.setCurrentIndex(index)
        for btn in [self.nav_dashboard, self.nav_devices, self.nav_scheduler, self.nav_settings]:
            btn.setChecked(False)
        if index == 0:
            self.nav_dashboard.setChecked(True)
        elif index == 1:
            self.nav_devices.setChecked(True)
        elif index == 3:
            self.nav_scheduler.setChecked(True)
        elif index == 4:
            self.nav_settings.setChecked(True)

    def _do_initial_scan(self):
        self.scanner.scan()

    def _do_manual_scan(self):
        self.scanner.scan()

    def _on_scan_complete(self, devices: List[Device]):
        self._devices = devices
        self._rules = self.scheduler.rules
        self.dashboard.update_stats(devices, len(self._rules))
        self.device_list.set_devices(devices)
        self.scheduler_view.set_data(self._rules, devices)

    def _on_device_selected(self, device: Device):
        self.device_detail.show_device(device)
        self._navigate_to(2)

    def _on_toggle_block(self, device: Device):
        if device.blocked:
            self.blocker.unblock_device(device.mac)
            device.blocked = False
        else:
            self.blocker.block_device(device.ip, device.mac)
            device.blocked = True
        self.device_detail.show_device(device)
        self.device_list.set_devices(self._devices)
        self.dashboard.update_stats(self._devices, len(self._rules))

    def _on_schedule_block(self, mac: str, ip: str):
        target_ip = ip
        for d in self._devices:
            if d.mac == mac:
                target_ip = d.ip
                d.blocked = True
                break
        self.blocker.block_device(target_ip, mac)
        self._refresh_ui()

    def _on_schedule_unblock(self, mac: str):
        self.blocker.unblock_device(mac)
        for d in self._devices:
            if d.mac == mac:
                d.blocked = False
        self._refresh_ui()

    def _on_rules_changed(self):
        self.scheduler.load()
        self._rules = self.scheduler.rules
        self.scheduler_view.set_data(self._rules, self._devices)
        self.dashboard.update_stats(self._devices, len(self._rules))

    def _refresh_ui(self):
        self.dashboard.update_stats(self._devices, len(self._rules))
        self.device_list.set_devices(self._devices)

    def closeEvent(self, event):
        self.scanner.stop_continuous_scan()
        self.blocker.stop_blocking()
        self.scheduler.stop()
        event.accept()
