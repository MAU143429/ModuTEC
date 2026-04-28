# ─────────────────────────────────────────
# ModuTEC — Shared UI style constants
# ─────────────────────────────────────────

DARK_WIDGET = "background-color: #1e1e1e; color: #ecf0f1;"

DARK_INPUT = (
    "QDoubleSpinBox {"
    "  background-color: #2d2d2d;"      # mismo color base que botones
    "  color: #e6e6e6;"
    "  border: 1px solid #3c3c3c;"
    "  border-radius: 4px;"
    "  padding: 2px 6px;"
    "  font-size: 12px;"
    "}"
    
    "QDoubleSpinBox:hover {"
    "  border: 1px solid #555;"
    "}"
    
    "QDoubleSpinBox:focus {"
    "  border: 1px solid #005f99;"
    "  background-color: #333333;"
    "}"
    
    "QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {"
    "  width: 14px;"
    "  background: transparent;"
    "}"
    
    "QDoubleSpinBox::up-arrow {"
    "  image: url(src/assets/arrow_up.png);"   # opcional
    "  width: 8px;"
    "  height: 8px;"
    "}"
    
    "QDoubleSpinBox::down-arrow {"
    "  image: url(src/assets/arrow_down.png);" # opcional
    "  width: 8px;"
    "  height: 8px;"
    "}"
)

DARK_BTN = (
    "QPushButton {"
    "  background-color: #2d2d2d;"
    "  color: #e6e6e6;"
    "  border: 1px solid #3c3c3c;"
    "  border-radius: 6px;"
    "  padding: 6px 12px;"
    "  font-size: 12px;"
    "}"
    
        "QPushButton:hover {"
    "  padding: 8px;"
    "}"
    
    "QPushButton:pressed {"
    "  background-color: #005f99;"
    "}"
)

DARK_BTN_GREEN = (
    "QPushButton {"
    "  background-color: #007acc;"
    "  color: white;"
    "  border-radius: 6px;"
    "  padding: 6px 12px;"
    "  font-weight: bold;"
    "}"
    "QPushButton:hover {"
    "  background-color: #2899f5;"
    "}"
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
    "  background-color: #2d2d2d;"
    "  color: #e6e6e6;"
    "  border: 1px solid #3c3c3c;"
    "  border-radius: 6px;"
    "  padding: 4px 10px;"
    "  font-size: 12px;"
    "}"
    
    "QComboBox:hover {"
    "  border: 1px solid #555;"
    "}"
    
    "QComboBox:focus {"
    "  border: 1px solid #005f99;"
    "}"
    
    "QComboBox::drop-down {"
    "  border: none;"
    "  width: 20px;"
    "}"
    
    "QComboBox::down-arrow {"
    "  image: url(assets/icons/arrow_down.png);"  # opcional
    "  width: 10px;"
    "  height: 10px;"
    "}"
    
    "QComboBox QAbstractItemView {"
    "  background-color: #1e1e1e;"
    "  color: #ecf0f1;"
    "  border: 1px solid #3c3c3c;"
    "  selection-background-color: #005f99;"
    "  selection-color: #ffffff;"
    "}"
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