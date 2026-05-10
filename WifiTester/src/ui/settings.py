from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QMessageBox, QFormLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..core.auth import check_password, set_password


class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addSpacing(8)

        pass_frame = QFrame()
        pass_frame.setFrameShape(QFrame.StyledPanel)
        pass_frame.setStyleSheet("""
            QFrame { background: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 16px; }
        """)
        pass_layout = QVBoxLayout()

        section_title = QLabel("Change Password")
        section_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #fff;")
        pass_layout.addWidget(section_title)
        pass_layout.addSpacing(8)

        form = QFormLayout()
        self.current_pw = QLineEdit()
        self.current_pw.setEchoMode(QLineEdit.Password)
        self.current_pw.setPlaceholderText("Current password")
        form.addRow("Current:", self.current_pw)

        self.new_pw = QLineEdit()
        self.new_pw.setEchoMode(QLineEdit.Password)
        self.new_pw.setPlaceholderText("New password")
        form.addRow("New:", self.new_pw)

        self.confirm_pw = QLineEdit()
        self.confirm_pw.setEchoMode(QLineEdit.Password)
        self.confirm_pw.setPlaceholderText("Confirm new password")
        form.addRow("Confirm:", self.confirm_pw)

        pass_layout.addLayout(form)
        pass_layout.addSpacing(8)

        change_btn = QPushButton("Update Password")
        change_btn.setStyleSheet("""
            QPushButton { background: #FF9800; color: white; border: none;
                          padding: 10px 20px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #F57C00; }
        """)
        change_btn.clicked.connect(self._on_change_password)
        pass_layout.addWidget(change_btn)
        pass_frame.setLayout(pass_layout)
        layout.addWidget(pass_frame)

        layout.addSpacing(16)

        danger_frame = QFrame()
        danger_frame.setFrameShape(QFrame.StyledPanel)
        danger_frame.setStyleSheet("""
            QFrame { background: #1e1e1e; border: 1px solid #F44336; border-radius: 8px; padding: 16px; }
        """)
        danger_layout = QVBoxLayout()

        danger_title = QLabel("Reset App")
        danger_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #F44336;")
        danger_layout.addWidget(danger_title)
        danger_layout.addSpacing(8)

        clear_btn = QPushButton("Clear All Data & Reset")
        clear_btn.setStyleSheet("""
            QPushButton { background: #F44336; color: white; border: none;
                          padding: 10px 20px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #D32F2F; }
        """)
        clear_btn.clicked.connect(self._on_clear_data)
        danger_layout.addWidget(clear_btn)

        danger_frame.setLayout(danger_layout)
        layout.addWidget(danger_frame)

        layout.addStretch()
        self.setLayout(layout)

    def _on_change_password(self):
        current = self.current_pw.text()
        new_pw = self.new_pw.text()
        confirm = self.confirm_pw.text()

        if not current:
            QMessageBox.warning(self, "Error", "Enter your current password.")
            return
        if not check_password(current):
            QMessageBox.warning(self, "Error", "Current password is incorrect.")
            return
        if not new_pw:
            QMessageBox.warning(self, "Error", "Enter a new password.")
            return
        if new_pw != confirm:
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            return

        set_password(new_pw)
        QMessageBox.information(self, "Success", "Password updated.")
        self.current_pw.clear()
        self.new_pw.clear()
        self.confirm_pw.clear()

    def _on_clear_data(self):
        from PySide6.QtWidgets import QInputDialog
        reply = QMessageBox.warning(
            self, "Confirm Reset",
            "This will delete all data (devices, rules, settings).\n\n"
            "You will need to set up NetGuard again.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        password, ok = QInputDialog.getText(
            self, "Confirm Password", "Enter password to confirm reset:",
            QLineEdit.Password,
        )
        if not ok or not password:
            return
        if not check_password(password):
            QMessageBox.warning(self, "Error", "Incorrect password.")
            return

        from ..utils.storage import init_db
        import os
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "netguard.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        init_db()
        QMessageBox.information(self, "Reset", "All data cleared. Restart the app.")
