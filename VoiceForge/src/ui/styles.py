STYLESHEET = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget {
    color: #e0e0e0;
    font-family: "Segoe UI", "SF Pro Display", "Ubuntu", sans-serif;
    font-size: 13px;
}
QLabel {
    color: #e0e0e0;
}
QLabel#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    padding: 10px 0;
}
QLabel#sectionLabel {
    font-size: 14px;
    font-weight: 600;
    color: #a0a0c0;
    padding: 5px 0;
}
QComboBox {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e0e0e0;
    min-height: 20px;
}
QComboBox:hover {
    border: 1px solid #e94560;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #16213e;
    border: 1px solid #0f3460;
    selection-background-color: #e94560;
    color: #e0e0e0;
}
QPushButton {
    background-color: #0f3460;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    color: #e0e0e0;
    font-weight: 600;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #e94560;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #c73a50;
}
QPushButton:disabled {
    background-color: #2a2a4a;
    color: #606080;
}
QPushButton#generateBtn {
    background-color: #e94560;
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    padding: 12px 30px;
    border-radius: 8px;
}
QPushButton#generateBtn:hover {
    background-color: #ff6b81;
}
QPushButton#generateBtn:disabled {
    background-color: #4a2a3a;
    color: #806070;
}
QPlainTextEdit {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 12px;
    color: #e0e0e0;
    font-size: 14px;
    selection-background-color: #e94560;
}
QPlainTextEdit:focus {
    border: 1px solid #e94560;
}
QProgressBar {
    background-color: #16213e;
    border: none;
    border-radius: 6px;
    text-align: center;
    color: #e0e0e0;
    height: 20px;
}
QProgressBar::chunk {
    background-color: #e94560;
    border-radius: 6px;
}
QGroupBox {
    border: 1px solid #0f3460;
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #a0a0c0;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #16213e;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #e94560;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}
QSlider::sub-page:horizontal {
    background: #e94560;
    border-radius: 2px;
}
QListWidget {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 4px;
}
QListWidget::item {
    padding: 6px 10px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #e94560;
    color: #ffffff;
}
QListWidget::item:hover {
    background-color: #0f3460;
}
QTabWidget::pane {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #0f3460;
    color: #a0a0c0;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #16213e;
    color: #ffffff;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #0f3460;
    background-color: #16213e;
}
QCheckBox::indicator:checked {
    background-color: #e94560;
    border-color: #e94560;
}
QSpinBox, QDoubleSpinBox {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e0e0e0;
}
QSplitter::handle {
    background-color: #0f3460;
    width: 2px;
}
"""
