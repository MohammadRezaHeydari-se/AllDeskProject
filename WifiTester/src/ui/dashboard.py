from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import List
from ..models.device import Device


class StatCard(QFrame):
    def __init__(self, title: str, initial_value: str = "0", color: str = "#2196F3"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            StatCard {{
                background: {color}15;
                border: 1px solid {color}40;
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        self.setMinimumHeight(100)
        layout = QVBoxLayout()
        self.value_label = QLabel(initial_value)
        vfont = QFont()
        vfont.setPointSize(28)
        vfont.setBold(True)
        self.value_label.setFont(vfont)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.title_label)

        self.setLayout(layout)

    def set_value(self, value: str):
        self.value_label.setText(value)


class DashboardView(QWidget):
    navigate = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel("Overview of your network")
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        self.total_card = StatCard("Total Devices", "0", "#2196F3")
        self.online_card = StatCard("Online", "0", "#4CAF50")
        self.blocked_card = StatCard("Blocked", "0", "#F44336")
        self.rules_card = StatCard("Active Rules", "0", "#FF9800")
        cards_layout.addWidget(self.total_card)
        cards_layout.addWidget(self.online_card)
        cards_layout.addWidget(self.blocked_card)
        cards_layout.addWidget(self.rules_card)
        layout.addLayout(cards_layout)

        layout.addSpacing(16)

        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("""
            QFrame { background: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 16px; }
            QLabel { color: #aaa; }
        """)
        ilayout = QVBoxLayout()
        self.info_label = QLabel("Scan your network to see connected devices.\n\nNetGuard uses ARP to discover devices on your LAN.\nNo router admin password needed.")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 13px; line-height: 1.5;")
        ilayout.addWidget(self.info_label)
        info_frame.setLayout(ilayout)
        layout.addWidget(info_frame)

        layout.addStretch()
        self.setLayout(layout)

    def update_stats(self, devices: List[Device], rules_count: int = 0):
        total = len(devices)
        online = sum(1 for d in devices if d.online)
        blocked = sum(1 for d in devices if d.blocked)
        self.total_card.set_value(str(total))
        self.online_card.set_value(str(online))
        self.blocked_card.set_value(str(blocked))
        self.rules_card.set_value(str(rules_count))
