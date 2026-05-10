from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QTimeEdit, QCheckBox, QLineEdit,
    QDialogButtonBox, QMessageBox, QComboBox,
)
from PySide6.QtCore import Qt, Signal, QTime
from PySide6.QtGui import QFont
from typing import List, Optional
from ..models.rule import ScheduleRule
from ..models.device import Device
from datetime import time


class RuleEditDialog(QDialog):
    def __init__(self, devices: List[Device], rule: Optional[ScheduleRule] = None, parent=None):
        super().__init__(parent)
        self._rule = rule
        self._devices = devices
        self._result: Optional[ScheduleRule] = None
        self.setWindowTitle("Edit Rule" if rule else "Add Rule")
        self.setFixedSize(400, 320)
        self._setup_ui()
        if rule:
            self._populate(rule)

    def _setup_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.device_combo = QComboBox()
        for d in self._devices:
            label = f"{d.hostname} ({d.mac})" if d.hostname != "Unknown" else f"{d.ip} ({d.mac})"
            self.device_combo.addItem(label, d.mac)
        form.addRow("Device:", self.device_combo)

        self.start_time = QTimeEdit(QTime(22, 0))
        self.start_time.setDisplayFormat("HH:mm")
        form.addRow("Block From:", self.start_time)

        self.end_time = QTimeEdit(QTime(7, 0))
        self.end_time.setDisplayFormat("HH:mm")
        form.addRow("Block Until:", self.end_time)

        self.mon = QCheckBox("Monday")
        self.tue = QCheckBox("Tuesday")
        self.wed = QCheckBox("Wednesday")
        self.thu = QCheckBox("Thursday")
        self.fri = QCheckBox("Friday")
        self.sat = QCheckBox("Saturday")
        self.sun = QCheckBox("Sunday")

        days_layout = QVBoxLayout()
        days_layout.addWidget(self.mon)
        days_layout.addWidget(self.tue)
        days_layout.addWidget(self.wed)
        days_layout.addWidget(self.thu)
        days_layout.addWidget(self.fri)
        days_layout.addWidget(self.sat)
        days_layout.addWidget(self.sun)
        form.addRow("Days:", days_layout)

        self.enabled_cb = QCheckBox("Enable rule")
        self.enabled_cb.setChecked(True)
        form.addRow("", self.enabled_cb)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def _populate(self, rule: ScheduleRule):
        idx = self.device_combo.findData(rule.mac)
        if idx >= 0:
            self.device_combo.setCurrentIndex(idx)
        self.start_time.setTime(QTime(rule.start_time.hour, rule.start_time.minute))
        self.end_time.setTime(QTime(rule.end_time.hour, rule.end_time.minute))
        self.enabled_cb.setChecked(rule.enabled)
        day_map = {0: self.mon, 1: self.tue, 2: self.wed, 3: self.thu,
                   4: self.fri, 5: self.sat, 6: self.sun}
        for d, cb in day_map.items():
            if rule.days and d in rule.days:
                cb.setChecked(True)

    def _on_accept(self):
        mac = self.device_combo.currentData()
        start = self.start_time.time()
        end = self.end_time.time()
        days = []
        day_map = [(0, self.mon), (1, self.tue), (2, self.wed), (3, self.thu),
                   (4, self.fri), (5, self.sat), (6, self.sun)]
        for d, cb in day_map:
            if cb.isChecked():
                days.append(d)

        if not days:
            QMessageBox.warning(self, "Error", "Select at least one day.")
            return

        self._result = ScheduleRule(
            id=self._rule.id if self._rule else 0,
            mac=mac,
            enabled=self.enabled_cb.isChecked(),
            start_time=time(start.hour(), start.minute()),
            end_time=time(end.hour(), end.minute()),
            days=days,
        )
        self.accept()

    def get_rule(self) -> Optional[ScheduleRule]:
        return self._result


class SchedulerView(QWidget):
    rules_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules: List[ScheduleRule] = []
        self._devices: List[Device] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        title = QLabel("Schedules")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.add_btn = QPushButton("+ Add Rule")
        self.add_btn.setStyleSheet("""
            QPushButton { background: #4CAF50; color: white; border: none;
                          padding: 8px 20px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #388E3C; }
        """)
        self.add_btn.clicked.connect(self._on_add)
        header_layout.addWidget(self.add_btn)
        layout.addLayout(header_layout)

        subtitle = QLabel("Schedule internet access for each device")
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Device", "From", "Until", "Days", "Enabled", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { background: #1e1e1e; border: 1px solid #333; border-radius: 4px; }
            QHeaderView::section { background: #252525; color: #aaa; padding: 8px; border: none; }
        """)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def set_data(self, rules: List[ScheduleRule], devices: List[Device]):
        self._rules = rules
        self._devices = devices
        self._refresh()

    def _refresh(self):
        self.table.setRowCount(len(self._rules))
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for row, r in enumerate(self._rules):
            device_name = r.mac
            for d in self._devices:
                if d.mac == r.mac:
                    device_name = d.hostname if d.hostname != "Unknown" else d.ip
                    break
            self.table.setItem(row, 0, QTableWidgetItem(device_name))
            self.table.setItem(row, 1, QTableWidgetItem(r.start_time.strftime("%H:%M")))
            self.table.setItem(row, 2, QTableWidgetItem(r.end_time.strftime("%H:%M")))
            days_str = ", ".join(day_names[d] for d in (r.days or []))
            self.table.setItem(row, 3, QTableWidgetItem(days_str))
            self.table.setItem(row, 4, QTableWidgetItem("Yes" if r.enabled else "No"))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(4, 2, 4, 2)
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("background: #FF9800; color: white; border: none; padding: 4px 12px; border-radius: 3px;")
            edit_btn.clicked.connect(lambda checked, r=r: self._on_edit(r))
            delete_btn = QPushButton("Del")
            delete_btn.setStyleSheet("background: #F44336; color: white; border: none; padding: 4px 12px; border-radius: 3px;")
            delete_btn.clicked.connect(lambda checked, r=r: self._on_delete(r))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 5, btn_widget)

    def _on_add(self):
        if not self._devices:
            QMessageBox.information(self, "Info", "Scan your network first to see devices.")
            return
        dialog = RuleEditDialog(self._devices, parent=self)
        if dialog.exec():
            rule = dialog.get_rule()
            if rule:
                self.rules_changed.emit()

    def _on_edit(self, rule: ScheduleRule):
        dialog = RuleEditDialog(self._devices, rule, parent=self)
        if dialog.exec():
            self.rules_changed.emit()

    def _on_delete(self, rule: ScheduleRule):
        reply = QMessageBox.question(self, "Confirm", "Delete this rule?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.rules_changed.emit()
