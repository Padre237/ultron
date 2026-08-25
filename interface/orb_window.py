"""
Fenêtre PyQt5 frameless pour l'orbe Jarvis.
- Transparente, sans bordure, toujours au premier plan
- Overlay texte temps réel (transcription + réponse)
- Draggable à la souris
- Icône dans la barre système
- change_state() thread-safe via pyqtSignal
"""

import os
import sys

from PyQt5.QtCore    import Qt, QUrl, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtGui     import QColor, QIcon, QPixmap, QPainter, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon,
                              QMenu, QLabel, QVBoxLayout, QWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

HTML_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_orb.html")
ORB_WIDTH  = 520
ORB_HEIGHT = 580   # Un peu plus haut pour l'overlay texte


def _make_tray_icon() -> QIcon:
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(0, 212, 255))
    p.setPen(Qt.NoPen)
    p.drawEllipse(4, 4, 24, 24)
    p.setBrush(QColor(255, 255, 255, 180))
    p.drawEllipse(10, 10, 8, 8)
    p.end()
    return QIcon(px)


class SilentPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, src):
        pass


class OrbWindow(QMainWindow):
    _state_signal = pyqtSignal(str, str)   # (state, text)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("JARVIS")
        self.resize(ORB_WIDTH, ORB_HEIGHT)
        self._center()

        # ── Widget central ────────────────────────────────────────────
        container = QWidget(self)
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Vue web (orbe animée)
        self._web = QWebEngineView()
        self._web.setPage(SilentPage(self._web))
        self._web.page().setBackgroundColor(Qt.transparent)
        self._web.setAttribute(Qt.WA_TranslucentBackground)
        self._web.setFixedHeight(520)
        self._web.load(QUrl.fromLocalFile(HTML_PATH))
        layout.addWidget(self._web)

        # Overlay texte
        self._text_label = QLabel("")
        self._text_label.setAlignment(Qt.AlignCenter)
        self._text_label.setWordWrap(True)
        self._text_label.setFixedHeight(55)
        self._text_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                letter-spacing: 1px;
                padding: 4px 12px;
                background: transparent;
            }
        """)
        layout.addWidget(self._text_label)

        self.setCentralWidget(container)

        # ── Drag ──────────────────────────────────────────────────────
        self._drag_pos = None

        # ── Tray ──────────────────────────────────────────────────────
        self._tray = QSystemTrayIcon(_make_tray_icon(), self)
        self._tray.setToolTip("JARVIS")
        menu = QMenu()
        menu.addAction("Afficher / Masquer", self._toggle)
        menu.addSeparator()
        menu.addAction("Quitter", QApplication.quit)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_clicked)
        self._tray.show()

        # ── Signal thread-safe ────────────────────────────────────────
        self._state_signal.connect(self._apply_state)

        # Couleurs des états pour le texte overlay
        self._state_colors = {
            "rest":      "#00d4ff",
            "listening": "#ffaa00",
            "working":   "#ff00ff",
            "speaking":  "#00ff88",
        }

    # ── API publique ──────────────────────────────────────────────────────────
    def change_state(self, state: str, text: str = ""):
        self._state_signal.emit(state, text)

    @pyqtSlot(str, str)
    def _apply_state(self, state: str, text: str):
        # Mettre à jour l'orbe JS
        js = f"if(typeof changeState==='function'){{changeState('{state}');}}"
        self._web.page().runJavaScript(js)

        # Mettre à jour le texte overlay
        color = self._state_colors.get(state, "#00d4ff")
        self._text_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-family: 'Courier New', monospace;
                font-size: 11px;
                letter-spacing: 1px;
                padding: 4px 12px;
                background: transparent;
                text-shadow: 0 0 8px {color};
            }}
        """)
        # Tronquer le texte si trop long
        display = text[:80] + "…" if len(text) > 80 else text
        self._text_label.setText(display)

    # ── Drag ──────────────────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def _tray_clicked(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._toggle()

    def _toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self._center()

    def closeEvent(self, e):
        e.ignore()
        self.hide()

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )


# ── Singleton ─────────────────────────────────────────────────────────────────
_app    = None
_window = None


def start_orb() -> OrbWindow:
    global _app, _window
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")
    _app = QApplication.instance() or QApplication(sys.argv)
    _app.setApplicationName("JARVIS")
    _app.setQuitOnLastWindowClosed(False)
    _window = OrbWindow()
    _window.show()
    return _window


def run_event_loop():
    if _app:
        _app.exec_()
