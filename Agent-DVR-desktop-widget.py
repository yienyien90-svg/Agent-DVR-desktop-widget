# ============================================================
# Agent DVR - Desktop Overlay (CLEAN STABLE VERSION)
# ============================================================

import sys
import os
import signal

from PyQt6.QtCore import (
    Qt,
    QPoint,
    QRect,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
    QUrl,
    QTimer
)

from PyQt6.QtGui import QShortcut, QKeySequence, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QLabel,
    QLineEdit,
    QSlider,
)

from PyQt6.QtWebEngineWidgets import QWebEngineView


# ============================================================
# CONFIG
# ============================================================

AGENT_DVR_URL = "http://localhost:8090/?viewIndex=0#Live"

WINDOW_WIDTH = 762
WINDOW_HEIGHT = 520
WINDOW_OPACITY = 0.85

MARGIN = 10


def resource_path(*parts):
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


APP_ICON_PATH = resource_path("assets", "camera.ico")


def load_app_icon():
    icon = QIcon(APP_ICON_PATH)
    if icon.isNull():
        return QIcon()
    return icon


HEADER_BTN_STYLE = """
QPushButton {
    background: rgba(40, 40, 40, 180);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background: rgba(60, 60, 60, 220);
}
"""


# ============================================================
# WIDGET
# ============================================================

class CameraWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.drag_position = QPoint()
        self.hidden_side = False
        self.settings_visible = False
        self.agent_url = AGENT_DVR_URL
        self.app_icon = load_app_icon()

        self.setup_ui()
        self.place_restore_button()
        self.place_top_right()
        self.restore_btn.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        if not self.app_icon.isNull():
            self.restore_btn.setWindowIcon(self.app_icon)
        # keep restore button always on top if visible
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.keep_ui_on_top)
        self.timer.start(800)

    # ========================================================
    # KEEP UI SAFE
    # ========================================================
    def keep_ui_on_top(self):
        if self.restore_btn.isVisible():
            self.restore_btn.raise_()

    # ========================================================
    # UI SETUP
    # ========================================================
    def setup_ui(self):

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowOpacity(WINDOW_OPACITY)

        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        # -------------------------
        # LAYOUT
        # -------------------------
        layout = QVBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)

        self.browser = QWebEngineView()
        self.browser.load(QUrl(AGENT_DVR_URL))

        layout.addWidget(self.browser)
        self.setLayout(layout)

        # force correct stacking
        self.browser.lower()

        # ====================================================
        # SLIDE BUTTON (left arrow)
        # ====================================================
        self.show_button = QPushButton("◀", self)
        self.show_button.setFixedSize(28, 80)
        self.show_button.clicked.connect(self.toggle_side_hide)
        self.show_button.hide()

        # ====================================================
        # HEADER BUTTONS (minimize, settings, close)
        # ====================================================
        self.min_btn = QPushButton("−", self)
        self.min_btn.setFixedSize(26, 26)
        self.min_btn.setStyleSheet(HEADER_BTN_STYLE)
        self.min_btn.clicked.connect(self.hide_widget)

        self.settings_btn = QPushButton("⚙", self)
        self.settings_btn.setFixedSize(26, 26)
        self.settings_btn.setStyleSheet(HEADER_BTN_STYLE)
        self.settings_btn.clicked.connect(self.toggle_settings)

        self.close_btn = QPushButton("✕", self)
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setStyleSheet(HEADER_BTN_STYLE)
        self.close_btn.clicked.connect(self.close_widget)

        self._setup_settings_panel()

        # ====================================================
        # RESTORE BUTTON
        # ====================================================
        self.restore_btn = QPushButton(self)
        self.restore_btn.setFixedSize(42, 42)
        if not self.app_icon.isNull():
            self.restore_btn.setIcon(self.app_icon)
            self.restore_btn.setIconSize(QSize(28, 28))
        else:
            self.restore_btn.setText("📷")
        self.restore_btn.clicked.connect(self.show_widget)
        self.restore_btn.hide()

    # ========================================================
    # SETTINGS PANEL
    # ========================================================
    def _setup_settings_panel(self):

        self.settings_panel = QFrame(self)
        self.settings_panel.setStyleSheet(
            "QFrame { background: rgba(30, 30, 30, 235); border-radius: 8px; }"
            "QLabel { color: white; font-size: 12px; }"
            "QLineEdit { background: rgba(50, 50, 50, 255); color: white;"
            " border: 1px solid #555; border-radius: 4px; padding: 4px; }"
            "QSlider::groove:horizontal { height: 6px; background: #444;"
            " border-radius: 3px; }"
            "QSlider::handle:horizontal { width: 14px; margin: -4px 0;"
            " background: #4a9eff; border-radius: 7px; }"
        )
        self.settings_panel.hide()

        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(12, 10, 12, 10)
        panel_layout.setSpacing(8)

        panel_layout.addWidget(QLabel("URL Agent DVR"))

        url_row = QHBoxLayout()
        self.url_input = QLineEdit(self.agent_url)
        url_row.addWidget(self.url_input)

        apply_btn = QPushButton("Appliquer")
        apply_btn.setStyleSheet(HEADER_BTN_STYLE)
        apply_btn.setFixedHeight(28)
        apply_btn.clicked.connect(self.apply_settings)
        url_row.addWidget(apply_btn)
        panel_layout.addLayout(url_row)

        self.opacity_label = QLabel(
            f"Opacité : {int(WINDOW_OPACITY * 100)} %"
        )
        panel_layout.addWidget(self.opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(int(WINDOW_OPACITY * 100))
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        panel_layout.addWidget(self.opacity_slider)

        reload_btn = QPushButton("Recharger la page")
        reload_btn.setStyleSheet(HEADER_BTN_STYLE)
        reload_btn.clicked.connect(lambda: self.browser.reload())
        panel_layout.addWidget(reload_btn)

    def toggle_settings(self):

        self.settings_visible = not self.settings_visible
        self.settings_panel.setVisible(self.settings_visible)
        if self.settings_visible:
            self.settings_panel.raise_()

    def _on_opacity_changed(self, value):

        self.opacity_label.setText(f"Opacité : {value} %")
        self.setWindowOpacity(value / 100.0)

    def apply_settings(self):

        url = self.url_input.text().strip()
        if url:
            self.agent_url = url
            self.browser.load(QUrl(self.agent_url))

    def close_widget(self):

        app = QApplication.instance()
        force_exit(app, self)

    def _position_header_buttons(self):

        y = 6
        self.close_btn.move(self.width() - 34, y)
        self.settings_btn.move(self.width() - 66, y)
        self.min_btn.move(self.width() - 98, y)

    def _position_settings_panel(self):

        if not hasattr(self, "settings_panel"):
            return
        self.settings_panel.setGeometry(
            8, 38, self.width() - 16, min(160, self.height() - 50)
        )

    # ========================================================
    # POSITION WINDOW
    # ========================================================
    def place_top_right(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - MARGIN, MARGIN)

    # ========================================================
    # POSITION RESTORE BUTTON
    # ========================================================
    def place_restore_button(self):

        screen = QApplication.primaryScreen().availableGeometry()

        x = screen.right() - self.restore_btn.width() - 20
        y = screen.top() + 40

        self.restore_btn.move(x, y)
        self.restore_btn.show()
        self.restore_btn.raise_()
    # ========================================================
    # DRAG WINDOW
    # ========================================================
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(
                event.globalPosition().toPoint() - self.drag_position
            )

    # ========================================================
    # HIDE COMPLET (DISPARAÎT VRAIMENT)
    # ========================================================
    def hide_widget(self):

        self.hidden_side = False
        self.settings_visible = False
        self.settings_panel.hide()
        self.hide()

        self.place_restore_button()

        self.restore_btn.show()
        self.restore_btn.raise_()

    # ========================================================
    # RESTORE COMPLET
    # ========================================================
    def show_widget(self):

        self.show()
        self.raise_()

        self.restore_btn.hide()

    # ========================================================
    # SLIDE SIDE MODE
    # ========================================================
    def toggle_side_hide(self):

        screen = QApplication.primaryScreen().geometry()

        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(250)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        current = self.geometry()

        if not self.hidden_side:

            target = QRect(
                screen.width() - 20,
                current.y(),
                current.width(),
                current.height()
            )

            self.show_button.show()
            self.hidden_side = True

        else:

            target = QRect(
                screen.width() - self.width() - MARGIN,
                current.y(),
                current.width(),
                current.height()
            )

            self.show_button.hide()
            self.hidden_side = False

        anim.setStartValue(current)
        anim.setEndValue(target)
        anim.start()

    # ========================================================
    # RESIZE EVENTS (keep buttons aligned)
    # ========================================================
    def resizeEvent(self, event):

        super().resizeEvent(event)
        self._position_header_buttons()
        self._position_settings_panel()
        self.show_button.move(-6, int(self.height() / 2 - 40))


# ============================================================
# EXIT CLEAN
# ============================================================
def force_exit(app, widget):
    widget.close()
    app.quit()
    os._exit(0)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("Agent DVR Widget")

    app_icon = load_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    widget = CameraWidget()
    widget.show()

    shortcut = QShortcut(QKeySequence("Escape"), widget)
    shortcut.activated.connect(lambda: force_exit(app, widget))

    sys.exit(app.exec())