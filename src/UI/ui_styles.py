# ─────────────────────────────────────────
# ModuTEC — Centralized UI Styles
# ─────────────────────────────────────────

# 🎨 COLORS (single source of truth)
BG_MAIN        = "#1e1e1e"
BG_SECONDARY   = "#252526"
BG_INPUT       = "#2d2d2d"

TEXT_MAIN      = "#ecf0f1"
TEXT_MUTED     = "#95a5a6"

BORDER         = "#3c3c3c"
BORDER_SOFT    = "#444"

PRIMARY        = "#007acc"
PRIMARY_HOVER  = "#2899f5"
PRIMARY_ALT    = "#3498db"

SUCCESS        = "#007acc"
SUCCESS_HOVER  = "#2899f5"

DANGER         = "#6b1a1a"
DANGER_HOVER   = "#a02525"

LOG_BG         = "#121212"


# ─────────────────────────────────────────
# GLOBAL
# ─────────────────────────────────────────
DIALOG_BG = f"""
background-color: {BG_MAIN};
color: {TEXT_MAIN};
"""

DARK_WIDGET = f"""
background-color: {BG_MAIN};
color: {TEXT_MAIN};
"""


# ─────────────────────────────────────────
# BUTTONS
# ─────────────────────────────────────────
DARK_BTN = f"""
QPushButton {{
    background-color: {BG_INPUT};
    color: {TEXT_MAIN};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: #3a3a3a;
}}
QPushButton:pressed {{
    background-color: {PRIMARY};
}}
"""

DARK_BTN_GREEN = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {PRIMARY_HOVER};
}}
"""

DARK_BTN_RED = f"""
QPushButton {{
    background-color: {DANGER};
    color: {TEXT_MAIN};
    border: 1px solid #e74c3c;
    border-radius: 6px;
    padding: 6px 12px;
}}
QPushButton:hover {{
    background-color: {DANGER_HOVER};
}}
QPushButton:pressed {{
    background-color: #450f0f;
}}
"""


# ─────────────────────────────────────────
# INPUTS
# ─────────────────────────────────────────
DARK_INPUT = """
QDoubleSpinBox {
    background-color: #2d2d2d;
    color: #e6e6e6;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 12px;
}

QDoubleSpinBox::up-button,
QDoubleSpinBox::down-button {
    width: 0px;
    height: 0px;
    border: none;
}

QDoubleSpinBox::up-arrow,
QDoubleSpinBox::down-arrow {
    width: 0px;
    height: 0px;
}
"""


# ─────────────────────────────────────────
# COMBOBOX
# ─────────────────────────────────────────
DARK_COMBO = """
QComboBox {
    background-color: #2d2d2d;
    color: #e6e6e6;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
}

QComboBox::drop-down {
    border: none;
    width: 0px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    color: #ecf0f1;
    border: 1px solid #3c3c3c;
}
"""


# ─────────────────────────────────────────
# LABELS
# ─────────────────────────────────────────
LABEL_TITLE = f"""
color: {TEXT_MAIN};
font-size: 15px;
font-weight: bold;
border-bottom: 1px solid {BORDER_SOFT};
padding-bottom: 6px;
"""

LABEL_SECTION = f"""
color: {TEXT_MAIN};
font-size: 18px;
font-weight: bold;
border-bottom: 1px solid {BORDER_SOFT};
padding-bottom: 4px;
"""

LABEL_MUTED = f"""
color: {TEXT_MUTED};
font-size: 13px;
"""

LABEL_VALUE = f"""
color: {TEXT_MAIN};
font-size: 13px;
font-weight: bold;
"""


# ─────────────────────────────────────────
# PANELS
# ─────────────────────────────────────────
TOOLBAR_STYLE = f"""
background-color: {BG_SECONDARY};
border-bottom: 1px solid {BORDER};
"""

RIGHT_PANEL = f"""
background-color: {BG_MAIN};
"""

SETTINGS_PANEL = f"""
background-color: {BG_MAIN};
"""

CARD_STYLE = f"""
background: transparent;
border: 1px solid #2a2a2a;
border-radius: 6px;
"""


# ─────────────────────────────────────────
# TEXT AREA (LOG)
# ─────────────────────────────────────────
LOG_BOX = f"""
background-color: {LOG_BG};
color: {TEXT_MAIN};
font-family: Consolas, monospace;
font-size: 13px;
border: 1px solid #333;
border-radius: 6px;
"""


# ─────────────────────────────────────────
# GROUPBOX
# ─────────────────────────────────────────
GROUPBOX_STYLE = f"""
QGroupBox {{
    color: {TEXT_MAIN};
    border: 1px solid {BORDER_SOFT};
    margin-top: 10px;
    font-weight: bold;
    font-size: 14px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
}}
"""