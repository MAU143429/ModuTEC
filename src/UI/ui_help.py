from PyQt5 import QtCore, QtWidgets
from ui_styles import DARK_BTN, DIALOG_BG


class HelpDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ModuTEC — Ayuda")
        self.setMinimumSize(560, 460)
        self.setStyleSheet(DIALOG_BG)
        
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        )

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        title = QtWidgets.QLabel("Guía de uso — ModuTEC Monitor")
        title.setStyleSheet(
            "color: #ecf0f1; font-size: 15px; font-weight: bold;"
            "border-bottom: 1px solid #444; padding-bottom: 6px;"
        )
        title.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(title)

        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        text.setStyleSheet(
            "background-color: #1e1e1e;"   # ← igual que el resto
            "color: #ecf0f1;"
            "font-family: Consolas, monospace;"
            "font-size: 12px;"
            "border: 1px solid #333;"
        )
        text.setHtml("""
<style>
  h3  { color: #3498db; margin-bottom: 2px; }
  p   { margin: 4px 0 10px 0; }
  li  { margin: 2px 0; }
  b   { color: #f1c40f; }
</style>

<h1>....</h1>

""")
        lay.addWidget(text)

        close_btn = QtWidgets.QPushButton("Cerrar")
        close_btn.setStyleSheet(DARK_BTN)
        close_btn.clicked.connect(self.accept)
        lay.addWidget(close_btn, alignment=QtCore.Qt.AlignRight)