from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from log_system.logger import LogManager


class LogCenterWidget(QGroupBox):
    def __init__(self, log_dir: str | Path, parent: QWidget | None = None) -> None:
        super().__init__("Debug / Log Center", parent)
        self.log_dir = Path(log_dir)
        self._setup_ui()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_logs)
        self._refresh_timer.start(5000)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Log Type:"))
        self.log_type_combo = QComboBox()
        self.log_type_combo.addItems(["app", "crash", "performance"])
        self.log_type_combo.currentTextChanged.connect(lambda _: self._refresh_logs())
        controls.addWidget(self.log_type_combo)
        controls.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_logs)
        controls.addWidget(self.refresh_btn)

        self.export_logs_btn = QPushButton("Export")
        self.export_logs_btn.clicked.connect(self._export_logs)
        controls.addWidget(self.export_logs_btn)

        self.clear_logs_btn = QPushButton("Clear")
        self.clear_logs_btn.clicked.connect(self._clear_logs)
        controls.addWidget(self.clear_logs_btn)
        layout.addLayout(controls)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.log_list = QListWidget()
        self.log_list.currentItemChanged.connect(self._show_detail)
        splitter.addWidget(self.log_list)

        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)
        self.detail_view.setStyleSheet("background-color: #0d1117; color: #c9d1d9; font-family: monospace; font-size: 12px;")
        splitter.addWidget(self.detail_view)

        splitter.setSizes([300, 400])
        layout.addWidget(splitter, 1)

        ai_layout = QHBoxLayout()
        ai_layout.addStretch()
        self.ai_analyze_btn = QPushButton("Analyze with AI (Coming Soon)")
        self.ai_analyze_btn.setEnabled(False)
        ai_layout.addWidget(self.ai_analyze_btn)
        layout.addLayout(ai_layout)

    def _refresh_logs(self) -> None:
        log_type = self.log_type_combo.currentText()
        try:
            log_manager = LogManager.get_instance()
            entries = log_manager.read_logs(log_type, lines=200)
        except RuntimeError:
            return

        self.log_list.clear()
        for entry in entries:
            level = entry.get("level", "INFO")
            msg = entry.get("message", entry.get("raw", ""))
            ts = entry.get("timestamp", "")
            display = f"[{level}] {msg[:80]}"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            item.setData(Qt.ItemDataRole.ToolTipRole, ts)

            if level == "ERROR" or level == "CRITICAL":
                item.setForeground(Qt.GlobalColor.red)
            elif level == "WARNING":
                item.setForeground(Qt.GlobalColor.yellow)
            else:
                item.setForeground(Qt.GlobalColor.white)

            self.log_list.addItem(item)

    def _show_detail(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if not current:
            return
        entry = current.data(Qt.ItemDataRole.UserRole)
        if entry:
            self.detail_view.setText(json.dumps(entry, indent=2, default=str))

    def _export_logs(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export Logs", str(self.log_dir / "exported_logs.json"), "JSON (*.json)")
        if path:
            log_type = self.log_type_combo.currentText()
            try:
                log_manager = LogManager.get_instance()
                entries = log_manager.read_logs(log_type, lines=1000)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(entries, f, indent=2, default=str)
            except RuntimeError:
                pass

    def _clear_logs(self) -> None:
        self.log_list.clear()
        self.detail_view.clear()
