# ─────────────────────────────────────────
# ModuTEC — Shared UI style constants
# ─────────────────────────────────────────

DARK_WIDGET = "background-color: #1e1e1e; color: #ecf0f1;"

DARK_INPUT = (
    "background-color: #121212; color: #ecf0f1;"
    "border: 1px solid #444; padding: 2px 4px;"
    "font-family: Consolas, monospace; font-size: 12px;"
)

DARK_BTN = (
    "QPushButton {"
    "  background-color: #2c3e50; color: #ecf0f1;"
    "  border: 1px solid #555; padding: 4px 10px;"
    "  font-size: 12px;"
    "}"
    "QPushButton:hover   { background-color: #3d5166; }"
    "QPushButton:pressed { background-color: #1a252f; }"
    "QPushButton:disabled{ color: #666; background-color: #222; }"
)

DARK_BTN_GREEN = (
    "QPushButton {"
    "  background-color: #1a6b3a; color: #ecf0f1;"
    "  border: 1px solid #2ecc71; padding: 4px 10px;"
    "  font-size: 12px;"
    "}"
    "QPushButton:hover   { background-color: #25a058; }"
    "QPushButton:pressed { background-color: #0f4525; }"
)

DARK_BTN_RED = (
    "QPushButton {"
    "  background-color: #6b1a1a; color: #ecf0f1;"
    "  border: 1px solid #e74c3c; padding: 4px 10px;"
    "  font-size: 12px;"
    "}"
    "QPushButton:hover   { background-color: #a02525; }"
    "QPushButton:pressed { background-color: #450f0f; }"
)

DARK_COMBO = (
    "QComboBox {"
    "  background-color: #121212; color: #ecf0f1;"
    "  border: 1px solid #444; padding: 2px 6px;"
    "  font-size: 12px;"
    "}"
    "QComboBox QAbstractItemView {"
    "  background-color: #1e1e1e; color: #ecf0f1;"
    "  selection-background-color: #2c3e50;"
    "}"
    "QComboBox::drop-down { border: none; }"
)

GROUPBOX_STYLE = (
    "QGroupBox {"
    "  color: #ecf0f1; border: 1px solid #444;"
    "  margin-top: 10px; font-weight: bold; font-size: 14px;"
    "}"
    "QGroupBox::title {"
    "  subcontrol-origin: margin; left: 10px; padding: 0 6px;"
    "}"
)

DIALOG_BG = "background-color: #1e1e1e; color: #ecf0f1;"