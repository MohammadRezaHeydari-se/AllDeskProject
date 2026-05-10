from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class PasswordSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NetGuard - First Time Setup")
        self.setFixedSize(380, 260)
        self._password = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel("NetGuard Setup")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel("Set a password to protect NetGuard")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        layout.addWidget(QLabel("App Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        layout.addWidget(self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Confirm password")
        layout.addWidget(self.confirm_input)

        layout.addSpacing(10)
        save_btn = QPushButton("Save & Continue")
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.setLayout(layout)

    def _on_save(self):
        pw = self.password_input.text()
        confirm = self.confirm_input.text()
        if not pw:
            QMessageBox.warning(self, "Error", "Password is required.")
            return
        if pw != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        self._password = pw
        self.accept()

    def get_password(self):
        return self._password


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NetGuard - Login")
        self.setFixedSize(380, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("NetGuard")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel("Home Network Manager")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.returnPressed.connect(self._on_login)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Unlock")
        self.login_btn.clicked.connect(self._on_login)
        layout.addWidget(self.login_btn)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

        layout.addStretch()
        self.setLayout(layout)
        self.password_input.setFocus()

    def _on_login(self):
        from ..core.auth import check_password
        password = self.password_input.text()
        if check_password(password):
            self.accept()
        else:
            self.status_label.setText("Incorrect password")
            self.password_input.clear()
            self.password_input.setFocus()
