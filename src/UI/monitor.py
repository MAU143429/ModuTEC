import sys
import time

import serial
import numpy as np
from PyQt5.QtGui import QIcon
import serial.tools.list_ports
from PyQt5.QtWidgets import QStyle
from ui_help        import HelpDialog
from PyQt5 import QtCore, QtWidgets, QtGui
from ui_config_tool import ConfigToolDialog
from serial_worker  import SerialParser, BAUD
from metrics import (
    analog_ncc,
    digital_ncc,
    ncc_color,
    nrmse,
    ncc_std,
    nrmse_color,
    std_color
)
import pyqtgraph as pg
from ui_styles import (
    DARK_BTN, DARK_BTN_GREEN, DARK_BTN_RED,
    DARK_COMBO,
    TOOLBAR_STYLE, RIGHT_PANEL, SETTINGS_PANEL,
    LABEL_TITLE, LABEL_SECTION, LABEL_MUTED, LABEL_VALUE,
    LOG_BOX
)

chunk_counter = 0

class TripleScope(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModuTEC Monitor")
        self.setWindowIcon(QIcon("src/assets/logo.png"))
        self.resize(1400, 850)

        # Internal state
        self.meta       = None
        self.frames     = 0
        self.last_fps_t = time.time()
        self.running    = False
        self.ser        = None
        self.parser     = SerialParser()
        self.ncc_history = []
        self.last_frame_ts = None
        self.latency_ms    = 0.0
        self.latency_avg   = 0.0

        self._build_ui()
        self.refresh_ports()
        
    
        # Main tick timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(5)

    # ══════════════════════════════════════════════════════════════
    # UI construction
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_v = QtWidgets.QVBoxLayout(central)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(0)

        main_v.addWidget(self._build_toolbar())
        main_v.addWidget(self._build_body())

    def _build_toolbar(self):
        toolbar = QtWidgets.QWidget()
        toolbar.setFixedHeight(44)
        toolbar.setStyleSheet(TOOLBAR_STYLE)
        lay = QtWidgets.QHBoxLayout(toolbar)
        lay.setContentsMargins(10, 4, 10, 4)
        lay.setSpacing(8)

        # Help button — top left
        self.btn_help = QtWidgets.QPushButton()
        self.btn_help.setIcon(QIcon("src/assets/help.png"))
        self.btn_help.setFixedSize(28, 28)
        self.btn_help.setStyleSheet(DARK_BTN)
        self.btn_help.setToolTip("Help / User Guide")
        self.btn_help.clicked.connect(self.show_help)
        lay.addWidget(self.btn_help)

        lay.addStretch()
 
        # COM dropdown
        com_lbl = QtWidgets.QLabel("Port:")
        com_lbl.setStyleSheet(LABEL_MUTED)
        lay.addWidget(com_lbl)

        self.com_combo = QtWidgets.QComboBox()
        self.com_combo.setMinimumWidth(230)
        self.com_combo.setStyleSheet(DARK_COMBO)
        lay.addWidget(self.com_combo)

        btn_refresh = QtWidgets.QPushButton()
        btn_refresh.setIcon(QIcon("src/assets/refresh.png"))
        btn_refresh.setFixedSize(28, 28)
        btn_refresh.setStyleSheet(DARK_BTN)
        btn_refresh.clicked.connect(self.refresh_ports)
        lay.addWidget(btn_refresh)

        lay.addSpacing(12)

        # Config Tool
        self.btn_cfg = QtWidgets.QPushButton(" Configuration Tool")
        self.btn_cfg.setIcon(QIcon("src/assets/config.png"))
        self.btn_cfg.setStyleSheet(DARK_BTN)
        self.btn_cfg.clicked.connect(self.open_config_tool)
        lay.addWidget(self.btn_cfg)

        lay.addSpacing(12)

        # RUN / STOP
        self.btn_run = QtWidgets.QPushButton("RUN")
        self.btn_run.setFixedWidth(72)
        self.btn_run.setStyleSheet(DARK_BTN_GREEN)
        self.btn_run.clicked.connect(self.toggle_monitor)
        lay.addWidget(self.btn_run)

        return toolbar

    def _build_body(self):
        body_w = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout(body_w)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(8)

        # Plots (left 75%)
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.setBackground("#1e1e1e")
        lay.addWidget(self.glw, stretch=75)

        self.p1 = self.glw.addPlot(row=0, col=0, title="MESSAGE")
        self.p2 = self.glw.addPlot(row=1, col=0, title="MODULATED")
        self.p3 = self.glw.addPlot(row=2, col=0, title="DEMODULATED")

        self.c1 = self.p1.plot(pen=pg.mkPen(color="#f1c40f", width=1.5))
        self.c2 = self.p2.plot(pen=pg.mkPen(color="#1abc9c", width=1.5))
        self.c3 = self.p3.plot(pen=pg.mkPen(color="#9b59b6", width=1.5))

        for p in (self.p1, self.p2, self.p3):
            p.showGrid(x=True, y=True, alpha=0.3)
            p.setYRange(-16000, 16000)
            p.getAxis("left").setStyle(tickFont=QtGui.QFont("Consolas", 8))
            p.getAxis("bottom").setStyle(tickFont=QtGui.QFont("Consolas", 8))

        # Right panel (25%)
        right_panel = QtWidgets.QWidget()
        right_panel.setStyleSheet(RIGHT_PANEL)
        right_lay = QtWidgets.QVBoxLayout(right_panel)
        right_lay.setContentsMargins(8, 8, 8, 8)
        right_lay.setSpacing(10)
        lay.addWidget(right_panel, stretch=25)

        self._build_settings_panel(right_lay)
        self._build_ncc_log(right_lay)

        return body_w

    def _build_settings_panel(self, parent_layout):
        lbl = QtWidgets.QLabel("Current Settings")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setStyleSheet(LABEL_TITLE)
        parent_layout.addWidget(lbl)

        self.settings_grid = QtWidgets.QWidget()
        self.settings_grid.setStyleSheet(SETTINGS_PANEL)
        self.grid_layout = QtWidgets.QGridLayout(self.settings_grid)
        self.grid_layout.setContentsMargins(4, 4, 4, 4)
        self.grid_layout.setSpacing(4)
        parent_layout.addWidget(self.settings_grid)

    def _build_ncc_log(self, parent_layout):
        lbl = QtWidgets.QLabel("Metrics Log")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setStyleSheet(LABEL_SECTION)
        parent_layout.addWidget(lbl)

        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(LOG_BOX)
        self.log_box.setFont(QtGui.QFont("Consolas", 9))
        self.log_box.setReadOnly(True)
        self.log_box.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        parent_layout.addWidget(self.log_box, stretch=1)

    # ══════════════════════════════════════════════════════════════
    # COM port helpers
    # ══════════════════════════════════════════════════════════════
    def refresh_ports(self):
        self.com_combo.clear()
        ports = list(serial.tools.list_ports.comports())
        usb_ports = []
        for p in ports:
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").lower()
            if "bluetooth" in desc:
                continue
            if "usb" in desc or "usb" in hwid:
                usb_ports.append(p)
        if not usb_ports:
            self.com_combo.addItem("— No USB Serial Ports —")
            return
        for p in sorted(usb_ports, key=lambda x: x.device):
            self.com_combo.addItem(p.device, userData=p.device)

    def _selected_port(self):
        return self.com_combo.itemData(self.com_combo.currentIndex())

    # ══════════════════════════════════════════════════════════════
    # Run / Stop
    # ══════════════════════════════════════════════════════════════
    def toggle_monitor(self):
        if self.running:
            self._stop_monitor()
        else:
            self._start_monitor()

    def _start_monitor(self):
        port = self._selected_port()
        if not port:
            QtWidgets.QMessageBox.warning(
                self, "No port selected",
                "Please select a COM port before starting the monitor."
            )
            return
        try:
            self.ser = serial.Serial(port, BAUD, timeout=0.001)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error opening port", f"Could not open {port}:\n{e}"
            )
            return
        self.parser.reset()
        self.running = True
        self.btn_run.setText("STOP")
        self.btn_run.setStyleSheet(DARK_BTN_RED)
        self.com_combo.setEnabled(False)
        self.setWindowTitle(
            f"ModuTEC Monitor | RUNNING - {port} | "
            f"FPS: {self.frames} | "
            f"Latency: {self.latency_avg:.1f} ms"
        )

    def _stop_monitor(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
        self.btn_run.setText("RUN")
        self.btn_run.setStyleSheet(DARK_BTN_GREEN)
        self.com_combo.setEnabled(True)
        self.setWindowTitle("ModuTEC Monitor | STOPPED")

    # ══════════════════════════════════════════════════════════════
    # Config Tool / Help
    # ══════════════════════════════════════════════════════════════
    def open_config_tool(self):
        if self.running:
            self._stop_monitor()
        ConfigToolDialog(self).exec_()

    def show_help(self):
        HelpDialog(self).exec_()

    # ══════════════════════════════════════════════════════════════
    # Close
    # ══════════════════════════════════════════════════════════════
    def closeEvent(self, event):
        self._stop_monitor()
        event.accept()

    # ══════════════════════════════════════════════════════════════
    # Main tick
    # ══════════════════════════════════════════════════════════════
    def tick(self):
        if not self.running:
            return

        raw = self.parser.read_available(self.ser)
        if raw:
            self.parser.feed(raw)

        # Drain metadata frames
        while True:
            meta, consumed = self.parser.try_read_meta()
            if meta is None:
                break
            self.meta = meta
            self.parser.consume(consumed)
            self.update_settings_panel()

        # Drain signal frames — render only the latest
        last_frame = None
        while True:
            frame, consumed = self.parser.try_read_frame()
            if frame is None:
                break
            last_frame = frame
            self.parser.consume(consumed)

        if last_frame:

            now = time.perf_counter()

            if self.last_frame_ts is not None:

                dt = now - self.last_frame_ts

                self.latency_ms = dt * 1000.0

                # suavizado simple
                if self.latency_avg == 0.0:
                    self.latency_avg = self.latency_ms
                else:
                    self.latency_avg = (
                        0.9 * self.latency_avg +
                        0.1 * self.latency_ms
                    )

            self.last_frame_ts = now

            self.update_ui(last_frame)
            self.frames += 1

        # FPS in title bar
        now = time.time()
        if now - self.last_fps_t > 1.0:
            port = self._selected_port() or "?"
            self.setWindowTitle(
                f"ModuTEC Monitor | RUNNING - {port} | "
                f"FPS: {self.frames} | "
                f"Latency: {self.latency_avg:.1f} ms"
            )
            self.frames     = 0
            self.last_fps_t = now

    # ══════════════════════════════════════════════════════════════
    # Settings panel
    # ══════════════════════════════════════════════════════════════
    def _clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_row(self, row, label_text, value_text, value_color="#ecf0f1"):
        lbl = QtWidgets.QLabel(label_text)
        lbl.setStyleSheet(LABEL_MUTED)
        val = QtWidgets.QLabel(value_text)
        val.setStyleSheet(LABEL_VALUE)
        val.setAlignment(QtCore.Qt.AlignRight)
        self.grid_layout.addWidget(lbl, row, 0)
        self.grid_layout.addWidget(val, row, 1)

    def update_settings_panel(self):
        if self.meta is None:
            return
        self._clear_grid()
        row = 0

        self._add_row(row, "Technique", self.meta["id"], "#3498db"); row += 1
        self._add_row(row, "Type", self.meta["type"].capitalize());   row += 1

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("color: #444;")
        self.grid_layout.addWidget(sep, row, 0, 1, 2); row += 1

        sys_info = self.meta.get("system", {})
        self._add_row(row, "Sample Rate (FS)", f"{sys_info.get('fs', '-')} Hz");  row += 1
        self._add_row(row, "Frame Size (N)",   str(sys_info.get('n', '-')));       row += 1
        self._add_row(row, "Amplitude (AMP)",  str(sys_info.get('amp', '-')));     row += 1
        self._add_row(row, "Alpha (LPF)",      str(sys_info.get('alpha', '-')));   row += 1

        if self.meta["type"] == "digital":
            self._add_row(row, "Bit Rate",       f"{sys_info.get('bit_rate', '-')} bps"); row += 1
            self._add_row(row, "Pattern Length", str(sys_info.get('pattern_len', '-'))); row += 1

        sep2 = QtWidgets.QFrame()
        sep2.setFrameShape(QtWidgets.QFrame.HLine)
        sep2.setStyleSheet("color: #444;")
        self.grid_layout.addWidget(sep2, row, 0, 1, 2); row += 1

        for pot_cfg in self.meta["pots"]:
            val = getattr(self, f"_pot_val_{pot_cfg['pot']}", "—")
            self._add_row(row, pot_cfg["label"], str(val)); row += 1

    # ══════════════════════════════════════════════════════════════
    # Plot update and NCC
    # ══════════════════════════════════════════════════════════════
    def update_ui(self, frame):
        global chunk_counter
        mode, N, FS, p1, p2, p3 = frame[:6]
        y_msg, y_mod, y_dem     = frame[6], frame[7], frame[8]

        self._pot_val_1 = f"{p1:.2f}"
        self._pot_val_2 = f"{p2:.2f}"
        self._pot_val_3 = f"{p3:.2f}"

        # Live-update pot values in settings grid
        if self.meta is not None:
            pot_vals   = {1: p1, 2: p2, 3: p3}
            total_rows = self.grid_layout.rowCount()
            pots       = self.meta["pots"]
            for i, pot_cfg in enumerate(pots):
                target_row = total_rows - len(pots) + i
                val_item   = self.grid_layout.itemAtPosition(target_row, 1)
                if val_item and val_item.widget():
                    val_item.widget().setText(f"{pot_vals[pot_cfg['pot']]:.2f}")

        t_ms = (np.arange(N) / FS) * 1000.0
        self.c1.setData(t_ms, y_msg)
        self.c2.setData(t_ms, y_mod)
        self.c3.setData(t_ms, y_dem)

        if self.meta is not None:
            tech_id   = self.meta["id"]
            tech_type = self.meta["type"]
            pots      = {p["pot"]: p for p in self.meta["pots"]}

            label_p1 = pots.get(1, {}).get("label", "P1")
            label_p2 = pots.get(2, {}).get("label", "P2")
            label_p3 = pots.get(3, {}).get("label", "P3")

            self.p1.setTitle(f"MESSAGE ({tech_id}) | {label_p1}: {p1:.2f}")
            self.p2.setTitle(f"MODULATED ({tech_id}) | {label_p2}: {p2:.2f}")
            self.p3.setTitle(f"DEMODULATED ({tech_id}) | {label_p3}: {p3:.2f}")

            chunk_counter += 1

            # NCC
            ncc_val = (
                analog_ncc(y_msg, y_dem)
                if tech_type == "analog"
                else digital_ncc(y_msg, y_dem)
            )

            # NRMSE
            nrmse_val = nrmse(y_msg, y_dem)
            # Update NCC history
            self.ncc_history.append(ncc_val)

            # Sliding window
            if len(self.ncc_history) > 50:
                self.ncc_history.pop(0)

            # STD NCC
            std_val = ncc_std(self.ncc_history)

            # Colors
            ncc_col    = ncc_color(ncc_val)
            nrmse_col  = nrmse_color(nrmse_val)
            
            std_col    = std_color(std_val)

            # Timestamp
            ts = time.strftime("%H:%M:%S")

            log_line = (
                f'<span style="color:#555;">[{ts}]</span> '

                f'<span style="color:#3498db; font-weight:bold;">'
                f'[{tech_id}]'
                f'</span> '

                f'<span style="color:#ecf0f1;">'
                f'CHUNK #{chunk_counter:04d}'
                f'</span>'

                f'<br>'

                f'<span style="color:#888;">NCC:</span> '
                f'<span style="color:{ncc_col}; font-weight:bold;">'
                f'{ncc_val:.1f}%'
                f'</span> '

                f'| '

                f'<span style="color:#888;">NRMSE:</span> '
                f'<span style="color:{nrmse_col}; font-weight:bold;">'
                f'{nrmse_val:.4f}'
                f'</span> '

                f'| '

                f'<span style="color:#888;">σNCC:</span> '
                f'<span style="color:{std_col}; font-weight:bold;">'
                f'{std_val:.2f}'
                f'</span>'

                f'<br>'
            )
            
            self.log_box.append(log_line)
            
            
            sb = self.log_box.verticalScrollBar()
            sb.setValue(sb.maximum())


# ─────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app.setStyle("Fusion")

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window,        QtGui.QColor("#1e1e1e"))
    palette.setColor(QtGui.QPalette.WindowText,    QtGui.QColor("#ecf0f1"))
    palette.setColor(QtGui.QPalette.Base,          QtGui.QColor("#121212"))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#1e1e1e"))
    palette.setColor(QtGui.QPalette.Text,          QtGui.QColor("#ecf0f1"))
    palette.setColor(QtGui.QPalette.Button,        QtGui.QColor("#2c3e50"))
    palette.setColor(QtGui.QPalette.ButtonText,    QtGui.QColor("#ecf0f1"))
    app.setPalette(palette)

    win = TripleScope()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()