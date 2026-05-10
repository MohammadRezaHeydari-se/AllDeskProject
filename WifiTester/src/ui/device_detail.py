from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ..models.device import Device


class DeviceDetailView(QWidget):
    back = Signal()
    toggle_block = Signal(Device)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._device: Device = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.back_btn = QPushButton("← Back to Devices")
        self.back_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #2196F3;
                          border: none; font-size: 13px; text-align: left; padding: 4px 0; }
            QPushButton:hover { color: #64B5F6; }
        """)
        self.back_btn.clicked.connect(self.back.emit)
        layout.addWidget(self.back_btn)

        self.name_label = QLabel("Select a device")
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        layout.addWidget(self.name_label)

        self.vendor_label = QLabel("")
        self.vendor_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(self.vendor_label)

        layout.addSpacing(12)

        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("""
            QFrame { background: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 16px; }
        """)
        grid = QGridLayout()
        grid.setSpacing(8)

        self.ip_label = QLabel("IP:")
        self.ip_label.setStyleSheet("font-weight: bold; color: #aaa;")
        self.ip_value = QLabel("")
        grid.addWidget(self.ip_label, 0, 0)
        grid.addWidget(self.ip_value, 0, 1)

        self.mac_label = QLabel("MAC:")
        self.mac_label.setStyleSheet("font-weight: bold; color: #aaa;")
        self.mac_value = QLabel("")
        grid.addWidget(self.mac_label, 1, 0)
        grid.addWidget(self.mac_value, 1, 1)

        self.vendor_label2 = QLabel("Vendor:")
        self.vendor_label2.setStyleSheet("font-weight: bold; color: #aaa;")
        self.vendor_value = QLabel("")
        grid.addWidget(self.vendor_label2, 2, 0)
        grid.addWidget(self.vendor_value, 2, 1)

        self.status_label = QLabel("Status:")
        self.status_label.setStyleSheet("font-weight: bold; color: #aaa;")
        self.status_value = QLabel("")
        grid.addWidget(self.status_label, 3, 0)
        grid.addWidget(self.status_value, 3, 1)

        self.first_seen_label = QLabel("First Seen:")
        self.first_seen_label.setStyleSheet("font-weight: bold; color: #aaa;")
        self.first_seen_value = QLabel("")
        grid.addWidget(self.first_seen_label, 4, 0)
        grid.addWidget(self.first_seen_value, 4, 1)

        self.last_seen_label = QLabel("Last Seen:")
        self.last_seen_label.setStyleSheet("font-weight: bold; color: #aaa;")
        self.last_seen_value = QLabel("")
        grid.addWidget(self.last_seen_label, 5, 0)
        grid.addWidget(self.last_seen_value, 5, 1)

        info_frame.setLayout(grid)
        layout.addWidget(info_frame)

        layout.addSpacing(12)

        self.block_btn = QPushButton("Block Internet")
        self.block_btn.setStyleSheet("""
            QPushButton {
                background: #F44336; color: white; border: none;
                padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #D32F2F; }
        """)
        self.block_btn.clicked.connect(self._on_toggle_block)
        layout.addWidget(self.block_btn)

        layout.addStretch()
        self.setLayout(layout)

    def show_device(self, device: Device):
        self._device = device
        self.name_label.setText(device.hostname if device.hostname != "Unknown" else device.ip)
        self.vendor_label.setText(f"{device.vendor} · {device.ip}")
        self.ip_value.setText(device.ip)
        self.mac_value.setText(device.mac)
        self.vendor_value.setText(device.vendor)
        self.status_value.setText("Online" if device.online else "Offline")
        self.status_value.setStyleSheet(f"color: {'#4CAF50' if device.online else '#888'};")
        self.first_seen_value.setText(device.first_seen.strftime("%Y-%m-%d %H:%M"))
        self.last_seen_value.setText(device.last_seen.strftime("%Y-%m-%d %H:%M"))
        self.block_btn.setText("Unblock Internet" if device.blocked else "Block Internet")
        self.block_btn.setStyleSheet(f"""
            QPushButton {{
                background: {'#4CAF50' if device.blocked else '#F44336'}; color: white; border: none;
                padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {'#388E3C' if device.blocked else '#D32F2F'}; }}
        """)

    def _on_toggle_block(self):
        if self._device:
            self.toggle_block.emit(self._device)
