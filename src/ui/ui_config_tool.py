import os
import ast
import json
import serial
import shutil
import subprocess
from PyQt5.QtGui import QIcon
import serial.tools.list_ports
from PyQt5 import QtCore, QtWidgets, QtGui
from ui_styles import (
    DARK_BTN,
    DARK_INPUT,
    DARK_COMBO,
    GROUPBOX_STYLE,
    DIALOG_BG,
    LABEL_MUTED,
    LABEL_TITLE,
    LABEL_VALUE,
    CARD_STYLE
)


class ConfigToolDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ModuTEC Configuration Tool")
        self.setMinimumSize(900, 620)
        self.setStyleSheet(DIALOG_BG)

        self.tech_data  = [{}, {}]
        self.tech_paths = [None, None]
        self._last_config_path = None
        self._last_py_paths    = [None, None]
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        )

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        # ── Title ─────────────────────────────────────────────────
        title = QtWidgets.QLabel("ModuTEC Configuration Tool")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(LABEL_TITLE)
        root.addWidget(title)

        # ── Three-column body ──────────────────────────────────────
        body = QtWidgets.QHBoxLayout()
        body.setSpacing(20)
        root.addLayout(body)

        self.tech_panels = []
        for idx in range(2):
            panel = self._make_tech_panel(idx)
            self.tech_panels.append(panel)
            if idx == 0:
                body.addWidget(panel, stretch=5)
                body.addWidget(self._make_sys_panel(), stretch=4)
            else:
                body.addWidget(panel, stretch=5)

        # ── Bottom buttons ─────────────────────────────────────────
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(16)
        btn_row.addStretch()

        self.btn_create = QtWidgets.QPushButton(" Create Configuration File")
        self.btn_create.setIcon(QIcon("src/assets/create.png"))
        self.btn_create.setStyleSheet(DARK_BTN)
        self.btn_create.setFixedHeight(38)
        self.btn_create.clicked.connect(self.create_config)
        btn_row.addWidget(self.btn_create)

        self.btn_upload = QtWidgets.QPushButton("Upload Configuration")
        self.btn_upload.setIcon(QIcon("src/assets/upload.png"))
        self.btn_upload.setStyleSheet(DARK_BTN)
        self.btn_upload.setFixedHeight(38)
        self.btn_upload.setEnabled(False)
        self.btn_upload.clicked.connect(self.upload_config)
        btn_row.addWidget(self.btn_upload)

        btn_row.addStretch()
        root.addLayout(btn_row)

        # Status bar
        self.status_lbl = QtWidgets.QLabel("")
        self.status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.status_lbl.setStyleSheet(LABEL_MUTED)
        root.addWidget(self.status_lbl)


    @staticmethod
    def _section_label(text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(
            "color: #95a5a6; font-size: 11px; font-weight: bold;"
            "letter-spacing: 1px; text-transform: uppercase;"
        )
        return lbl

    # ── Tech panel ────────────────────────────────────────────────
    def _make_tech_panel(self, idx):
        panel = QtWidgets.QGroupBox(f"  Technique {idx + 1}")
        panel.setStyleSheet(GROUPBOX_STYLE)
        lay = QtWidgets.QVBoxLayout(panel)
        lay.setSpacing(12)
        lay.setContentsMargins(14, 18, 14, 14)

        # Load button + filename
        load_row = QtWidgets.QHBoxLayout()
        btn_load = QtWidgets.QPushButton(" Load .py file")
        btn_load.setIcon(QIcon("src/assets/pyicon.png"))
        btn_load.setStyleSheet(DARK_BTN)
        btn_load.setFixedHeight(32)
        btn_load.clicked.connect(lambda _, i=idx: self.load_technique(i))
        load_row.addWidget(btn_load)
        lay.addLayout(load_row)

        fn_lbl = QtWidgets.QLabel("— file not loaded —")
        fn_lbl.setStyleSheet(
            "color: #555; font-size: 12px; font-style: italic;"
        )
        fn_lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(fn_lbl)

        # Divider
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("color: #333;")
        lay.addWidget(sep)

        # Type selector
        type_row = QtWidgets.QHBoxLayout()
        type_lbl = QtWidgets.QLabel("Type of technique:")
        type_lbl.setStyleSheet("color: #95a5a6; font-size: 13px;")
        type_combo = QtWidgets.QComboBox()
        type_combo.addItems(["Analog", "Digital"])
        type_combo.setStyleSheet(DARK_COMBO)
        type_combo.setFixedHeight(28)
        type_row.addWidget(type_lbl)
        type_row.addStretch()
        type_row.addWidget(type_combo)
        lay.addLayout(type_row)

        # Variables header
        lay.addWidget(self._section_label("Parameters and ranges"))

        # Variable rows
        var_widgets = []
        for v in range(3):
            var_frame = QtWidgets.QFrame()
            var_frame.setStyleSheet(CARD_STYLE)
            vf_lay = QtWidgets.QVBoxLayout(var_frame)
            vf_lay.setContentsMargins(10, 8, 10, 8)
            vf_lay.setSpacing(6)

            v_label = QtWidgets.QLabel(f"Variable {v+1}:  —")
            v_label.setStyleSheet(LABEL_VALUE)
            vf_lay.addWidget(v_label)

            range_row = QtWidgets.QHBoxLayout()
            range_row.setSpacing(8)

            lbl_min = QtWidgets.QLabel("Min")
            lbl_min.setStyleSheet(LABEL_MUTED)
            spin_min = QtWidgets.QDoubleSpinBox()

            lbl_max = QtWidgets.QLabel("Max")
            lbl_max.setStyleSheet(LABEL_MUTED)
            spin_max = QtWidgets.QDoubleSpinBox()

            for sp in (spin_min, spin_max):
                sp.setRange(-999999, 999999)
                sp.setDecimals(2)
                sp.setStyleSheet(DARK_INPUT)
                sp.setFixedWidth(100)
                sp.setFixedHeight(26)
            spin_min.setValue(0.0)
            spin_max.setValue(100.0)

            range_row.addWidget(lbl_min)
            range_row.addWidget(spin_min)
            range_row.addStretch()
            range_row.addWidget(lbl_max)
            range_row.addWidget(spin_max)
            vf_lay.addLayout(range_row)

            lay.addWidget(var_frame)
            var_widgets.append((v_label, spin_min, spin_max))

        
        lay.addStretch()

        panel._fn_lbl      = fn_lbl
        panel._type_combo  = type_combo
        panel._var_widgets = var_widgets
        return panel

    # ── System params panel ───────────────────────────────────────
    def _make_sys_panel(self):
        panel = QtWidgets.QGroupBox("  System")
        panel.setStyleSheet(GROUPBOX_STYLE)
        lay = QtWidgets.QVBoxLayout(panel)
        lay.setContentsMargins(14, 18, 14, 14)
        lay.setSpacing(10)

        lay.addWidget(self._section_label("System parameters"))

        def mk_field(label_text, lo, hi, val, dec=0):
            row = QtWidgets.QHBoxLayout()
            lbl = QtWidgets.QLabel(label_text)
            lbl.setStyleSheet(LABEL_MUTED)
            lbl.setFixedWidth(110)
            sp = QtWidgets.QDoubleSpinBox()
            sp.setRange(lo, hi)
            sp.setDecimals(dec)
            sp.setValue(val)
            sp.setStyleSheet(DARK_INPUT)
            sp.setFixedHeight(26)
            row.addWidget(lbl)
            row.addWidget(sp, stretch=1)
            return row, sp

        fields_def = [
            ("Sample Rate",    1000,   96000,  5000,   0),
            ("Frames",         32,     4096,   256,    0),
            ("Amplitude",      1,      32767,  14000,  0),
            ("Baud Rate",      9600,   921600, 115200, 0),
            ("Bit Rate",       1,      100000, 400,    1),
            ("Pattern Length", 4,      1024,   32,     0),
            ("Alpha",          0.001,  1.0,    0.08,   3),
        ]

        self._sys_spins = {}
        for name, lo, hi, val, dec in fields_def:
            row, sp = mk_field(name, lo, hi, val, dec)
            lay.addLayout(row)
            self._sys_spins[name] = sp
            
        
        logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap("src/assets/logo.png") 
        pixmap = pixmap.scaled(
            170, 170,  # tamaño deseado
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        logo.setPixmap(pixmap)
        logo.setAlignment(QtCore.Qt.AlignCenter)

        lay.addWidget(logo)
        
        lay.addStretch()
        return panel

    # ── Convenience refs ──────────────────────────────────────────
    @property
    def sp_fs(self):          return self._sys_spins["Sample Rate"]
    @property
    def sp_n(self):           return self._sys_spins["Frames"]
    @property
    def sp_amp(self):         return self._sys_spins["Amplitude"]
    @property
    def sp_baud(self):        return self._sys_spins["Baud Rate"]
    @property
    def sp_bitrate(self):     return self._sys_spins["Bit Rate"]
    @property
    def sp_pattern_len(self): return self._sys_spins["Pattern Length"]
    @property
    def sp_alpha(self):       return self._sys_spins["Alpha"]

    # ── Load technique file ───────────────────────────────────────
    def load_technique(self, idx):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, f"Load technique {idx+1}", "", "Python files (*.py)"
        )
        if not path:
            return

        param_names = self._extract_params(path)
        if param_names is None:
            QtWidgets.QMessageBox.warning(
                self, "Error",
                "It could not extract parameters from compute_frame().\n"
                "Make sure the file follows the ModuTEC structure."
            )
            return

        self.tech_paths[idx] = path
        panel = self.tech_panels[idx]
        panel._fn_lbl.setText(f"✔  {os.path.basename(path)}")
        panel._fn_lbl.setStyleSheet(
            "color: #2ecc71; font-size: 12px; font-style: normal; font-weight: bold;"
        )

        for v, (v_label, spin_min, spin_max) in enumerate(panel._var_widgets):
            if v < len(param_names):
                v_label.setText(f"Variable {v+1}:  {param_names[v]}")
            else:
                v_label.setText(f"Variable {v+1}:  —")

        self.tech_data[idx] = {
            "id":     os.path.splitext(os.path.basename(path))[0],
            "file":   os.path.basename(path),
            "params": param_names,
        }
        self.status_lbl.setText(f"Technique {idx+1} loaded: {os.path.basename(path)}")

    def _extract_params(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception:
            return None

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "PARAM_ORDER":
                        if isinstance(node.value, ast.List):
                            params = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    params.append(elt.value)
                            return params

        return None

    # ── Create config.json ────────────────────────────────────────
    def create_config(self):
        if not self.tech_data[0] or not self.tech_data[1]:
            QtWidgets.QMessageBox.warning(
                self, "Missing techniques",
                "You must load both .py files before creating the configuration."
            )
            return

        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save config.json", "config.json", "JSON (*.json)"
        )
        if not save_path:
            return

        techniques = []
        for idx in range(2):
            panel   = self.tech_panels[idx]
            td      = self.tech_data[idx]
            params  = td.get("params", [])
            tc_type = panel._type_combo.currentText()

            pots = []
            for v, (v_label, spin_min, spin_max) in enumerate(panel._var_widgets):
                if v < len(params):
                    pots.append({
                        "pot":   v + 1,
                        "param": params[v],
                        "label": params[v].replace("_", " ").title(),
                        "min":   round(spin_min.value(), 4),
                        "max":   round(spin_max.value(), 4),
                    })

            techniques.append({
                "id":   td["id"],
                "file": td["file"],
                "type": tc_type,
                "pots": pots,
            })

        sys_cfg = {
            "fs":          int(self.sp_fs.value()),
            "n":           int(self.sp_n.value()),
            "amp":         int(self.sp_amp.value()),
            "baud":        int(self.sp_baud.value()),
            "bit_rate":    round(self.sp_bitrate.value(), 2),
            "pattern_len": int(self.sp_pattern_len.value()),
            "alpha":       round(self.sp_alpha.value(), 4),
        }

        config = {"techniques": techniques, "system": sys_cfg}

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not save:\n{e}")
            return

        self._last_config_path = save_path
        self._last_py_paths    = list(self.tech_paths)
        self.btn_upload.setEnabled(True)
        self.status_lbl.setText(f"Configuration saved to: {save_path}")

    # ── Upload via mpremote ───────────────────────────────────────
    def upload_config(self):
        parent = self.parent()

        if not parent or not hasattr(parent, "_selected_port"):
            QtWidgets.QMessageBox.warning(
                self, "Error",
                "Could not access selected port from monitor."
            )
            return

        port = parent._selected_port()

        if not port:
            QtWidgets.QMessageBox.warning(
                self, "No port selected",
                "Please select a COM port in the monitor first."
            )
            return

        cfg_path = self._last_config_path
        py1      = self._last_py_paths[0]
        py2      = self._last_py_paths[1]

        if not cfg_path or not py1 or not py2:
            QtWidgets.QMessageBox.warning(
                self, "Error",
                "First create the configuration."
            )
            return

        mpremote = shutil.which("mpremote")
        if not mpremote:
            QtWidgets.QMessageBox.critical(
                self, "mpremote not found",
                "mpremote is not in the system PATH.\n"
                "Install it with:  pip install mpremote"
            )
            return

        cmds = [
            [mpremote, "connect", port, "fs", "cp", cfg_path, ":"],
            [mpremote, "connect", port, "fs", "cp", py1,      ":"],
            [mpremote, "connect", port, "fs", "cp", py2,      ":"],
            [mpremote, "connect", port, "reset"],
        ]

        self.status_lbl.setText(f"Loading to {port}…")
        QtWidgets.QApplication.processEvents()

        errors = []
        for cmd in cmds:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    errors.append(f"{' '.join(cmd)}\n{result.stderr.strip()}")
            except subprocess.TimeoutExpired:
                errors.append(f"Timeout: {' '.join(cmd)}")
            except Exception as e:
                errors.append(str(e))

        if errors:
            QtWidgets.QMessageBox.critical(
                self, "Errors while loading",
                "Some commands failed:\n\n" + "\n\n".join(errors)
            )
        else:
            self.status_lbl.setText(f"Loaded to {port} and reset!")
            QtWidgets.QMessageBox.information(
                self, "Success",
                f"Files copied and device reset on {port}."
            )