import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ..core.auth import is_first_run, set_password
from ..utils.storage import init_db
from ..ui.login import PasswordSetupDialog, LoginDialog
from .main_window import MainWindow


def main():
    QApplication.setOrganizationName("NetGuard")
    QApplication.setApplicationName("NetGuard")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', 'SF Pro', 'Ubuntu', sans-serif;
        }
        QLineEdit {
            background: #1e1e1e; border: 1px solid #333;
            padding: 8px; border-radius: 4px; color: #fff;
        }
        QLineEdit:focus {
            border: 1px solid #2196F3;
        }
        QMessageBox {
            background: #1e1e1e;
        }
        QMessageBox QLabel {
            color: #e0e0e0;
        }
        QMessageBox QPushButton {
            background: #333; color: #fff; border: none;
            padding: 6px 20px; border-radius: 4px;
        }
        QMessageBox QPushButton:hover {
            background: #444;
        }
    """)

    init_db()

    if is_first_run():
        dialog = PasswordSetupDialog()
        if dialog.exec():
            set_password(dialog.get_password())
        else:
            return 1

    login = LoginDialog()
    if login.exec():
        window = MainWindow()
        window.show()
        return app.exec()

    return 1
