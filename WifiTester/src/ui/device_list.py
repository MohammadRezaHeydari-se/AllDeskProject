from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import List, Optional
from ..models.device import Device


class DeviceListView(QWidget):
    device_selected = Signal(Device)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._devices: List[Device] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        title = QLabel("Devices")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.scan_btn = QPushButton("Scan Now")
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3; color: white; border: none;
                padding: 8px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        header_layout.addWidget(self.scan_btn)
        layout.addLayout(header_layout)

        subtitle = QLabel("All devices discovered on your network")
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["IP", "MAC", "Hostname", "Vendor", "Status", "Blocked"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1e1e1e; border: 1px solid #333;
                border-radius: 4px; gridline-color: #2a2a2a;
            }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected { background: #2196F3; }
            QHeaderView::section {
                background: #252525; color: #aaa; padding: 8px;
                border: none; border-bottom: 1px solid #333;
                font-weight: bold;
            }
        """)
        self.table.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def set_devices(self, devices: List[Device]):
        self._devices = devices
        self.table.setRowCount(len(devices))
        for row, d in enumerate(devices):
            self.table.setItem(row, 0, QTableWidgetItem(d.ip))
            self.table.setItem(row, 1, QTableWidgetItem(d.mac))
            self.table.setItem(row, 2, QTableWidgetItem(d.hostname))
            self.table.setItem(row, 3, QTableWidgetItem(d.vendor))
            status = "Online" if d.online else "Offline"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#4CAF50" if d.online else "#888"))
            self.table.setItem(row, 4, status_item)

            blocked = "Yes" if d.blocked else "No"
            blocked_item = QTableWidgetItem(blocked)
            blocked_item.setForeground(QColor("#F44336" if d.blocked else "#888"))
            self.table.setItem(row, 5, blocked_item)

    def _on_item_clicked(self, item):
        row = item.row()
        if 0 <= row < len(self._devices):
            self.device_selected.emit(self._devices[row])
