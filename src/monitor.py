import sys
import time
import struct
import json

import numpy as np
import serial

from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg

from metrics import analog_ncc, digital_ncc, ncc_color

# ─────────────────────────────────────────
# Connection settings
# ─────────────────────────────────────────
PORT = "COM6"
BAUD = 115200

# ─────────────────────────────────────────
# Protocol
# ─────────────────────────────────────────
SYNC         = b"MDT2"
SYNC_META    = b"MDTM"
HEADER_FMT   = "<BHHfff"
HEADER_LEN   = struct.calcsize(HEADER_FMT)
META_LEN_FMT = "<H"
META_LEN_LEN = struct.calcsize(META_LEN_FMT)

# ─────────────────────────────────────────
# Chunk counter
# ─────────────────────────────────────────
chunk_counter = 0


class TripleScope(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModuTEC Monitor")
        self.resize(1400, 850)

        # Internal state
        self.meta       = None
        self.frames     = 0
        self.last_fps_t = time.time()

        # Serial
        self.ser = serial.Serial(PORT, BAUD, timeout=0.001)
        self.buf = bytearray()

        # ── Main layout ───────────────────────────────────────────────
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root_layout = QtWidgets.QHBoxLayout(central)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(8)

        # ── Left panel: plots (75%) ───────────────────────────────────
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.setBackground("#1e1e1e")
        root_layout.addWidget(self.glw, stretch=75)

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

        # ── Right panel (25%) ─────────────────────────────────────────
        right_panel = QtWidgets.QWidget()
        right_panel.setStyleSheet("background-color: #1e1e1e;")
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(10)
        root_layout.addWidget(right_panel, stretch=25)

        # ── Current Settings ──────────────────────────────────────────
        settings_label = QtWidgets.QLabel("Current Settings")
        settings_label.setAlignment(QtCore.Qt.AlignCenter)
        settings_label.setStyleSheet(
            "color: #ecf0f1; font-size: 15px; font-weight: bold;"
            "border-bottom: 1px solid #444; padding-bottom: 4px;"
        )
        right_layout.addWidget(settings_label)

        self.settings_grid = QtWidgets.QWidget()
        self.settings_grid.setStyleSheet("background-color: #1e1e1e;")
        self.grid_layout = QtWidgets.QGridLayout(self.settings_grid)
        self.grid_layout.setContentsMargins(4, 4, 4, 4)
        self.grid_layout.setSpacing(4)
        right_layout.addWidget(self.settings_grid)

        # ── NCC Log ───────────────────────────────────────────────────
        log_label = QtWidgets.QLabel("NCC Log")
        log_label.setAlignment(QtCore.Qt.AlignCenter)
        log_label.setStyleSheet(
            "color: #ecf0f1; font-size: 18px; font-weight: bold;"
            "border-bottom: 1px solid #444; padding-bottom: 4px;"
        )
        right_layout.addWidget(log_label)

        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(
            "background-color: #121212;"
            "color: #ecf0f1;"
            "font-family: Consolas, monospace;"
            "font-size: 13px;"
            "border: 1px solid #333;"
        )
        self.log_box.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        right_layout.addWidget(self.log_box, stretch=1)

        # ── Timer ─────────────────────────────────────────────────────
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(5)

    def closeEvent(self, event):
        if self.ser.is_open:
            self.ser.close()
        event.accept()

    # ─────────────────────────────────────────
    # Serial reading
    # ─────────────────────────────────────────
    def read_some(self):
        try:
            n = self.ser.in_waiting
            if n > 0:
                return self.ser.read(n)
        except Exception as e:
            print(f"Serial read error: {e}")
        return b""

    def feed(self, data: bytes):
        self.buf.extend(data)
        if len(self.buf) > 500000:
            self.buf = self.buf[-100000:]

    # ─────────────────────────────────────────
    # Frame parsing
    # ─────────────────────────────────────────
    def try_read_meta(self):
        """
        Attempts to extract a MDTM metadata frame from the buffer.
        Returns (meta_dict, bytes_consumed) or (None, 0).
        """
        idx = self.buf.find(SYNC_META)
        if idx < 0:
            return None, 0

        start = idx + len(SYNC_META)
        if len(self.buf) < start + META_LEN_LEN:
            return None, 0

        json_len   = struct.unpack_from(META_LEN_FMT, self.buf, start)[0]
        start_json = start + META_LEN_LEN

        if len(self.buf) < start_json + json_len:
            return None, 0

        raw_json = self.buf[start_json: start_json + json_len]
        try:
            meta = json.loads(raw_json.decode("utf-8"))
        except Exception:
            return None, idx + 1  # discard byte and retry

        return meta, start_json + json_len

    def try_read_frame(self):
        """
        Attempts to extract a MDT2 signal frame from the buffer.
        Returns (frame_data, bytes_consumed) or (None, 0).
        """
        idx = self.buf.find(SYNC)
        if idx < 0:
            return None, 0

        start = idx + len(SYNC)
        if len(self.buf) < start + HEADER_LEN:
            return None, 0

        header_data              = self.buf[start: start + HEADER_LEN]
        mode, N, FS, p1, p2, p3 = struct.unpack(HEADER_FMT, header_data)

        payload_len     = 2 * N * 3
        total_frame_len = len(SYNC) + HEADER_LEN + payload_len

        if len(self.buf) < idx + total_frame_len:
            return None, 0

        payload_start = start + HEADER_LEN
        payload       = self.buf[payload_start: idx + total_frame_len]

        a     = np.frombuffer(payload, dtype=np.int16)
        y_msg = a[0:N].astype(np.float32)
        y_mod = a[N:2*N].astype(np.float32)
        y_dem = a[2*N:3*N].astype(np.float32)

        return (mode, N, FS, p1, p2, p3, y_msg, y_mod, y_dem), idx + total_frame_len

    # ─────────────────────────────────────────
    # Main tick
    # ─────────────────────────────────────────
    def tick(self):
        new_data = self.read_some()
        if new_data:
            self.feed(new_data)

        # Process metadata frames
        while True:
            meta, consumed = self.try_read_meta()
            if meta is None:
                break
            self.meta = meta
            del self.buf[:consumed]
            self.update_settings_panel()

        # Process signal frames (drain loop, only render the latest)
        last_frame = None
        while True:
            frame, consumed = self.try_read_frame()
            if frame is None:
                break
            last_frame = frame
            del self.buf[:consumed]

        if last_frame:
            self.update_ui(last_frame)
            self.frames += 1

        # FPS in title bar
        now = time.time()
        if now - self.last_fps_t > 1.0:
            self.setWindowTitle(f"ModuTEC Monitor | FPS: {self.frames}")
            self.frames     = 0
            self.last_fps_t = now

    # ─────────────────────────────────────────
    # Settings panel
    # ─────────────────────────────────────────
    def _clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_row(self, row, label_text, value_text, value_color="#ecf0f1"):
        lbl = QtWidgets.QLabel(label_text)
        lbl.setStyleSheet("color: #95a5a6; font-size: 13px;")
        val = QtWidgets.QLabel(value_text)
        val.setStyleSheet(f"color: {value_color}; font-size: 13px; font-weight: bold;")
        val.setAlignment(QtCore.Qt.AlignRight)
        self.grid_layout.addWidget(lbl, row, 0)
        self.grid_layout.addWidget(val, row, 1)

    def update_settings_panel(self):
        if self.meta is None:
            return

        self._clear_grid()
        row = 0

        # Active technique
        self._add_row(row, "Technique", self.meta["id"], "#3498db")
        row += 1

        # Type
        self._add_row(row, "Type", self.meta["type"].capitalize())
        row += 1

        # Divider
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("color: #444;")
        self.grid_layout.addWidget(sep, row, 0, 1, 2)
        row += 1

        # System parameters
        sys_info = self.meta.get("system", {})
        self._add_row(row, "Sample Rate (FS)", f"{sys_info.get('fs', '-')} Hz")
        row += 1
        self._add_row(row, "Frame Size (N)", str(sys_info.get('n', '-')))
        row += 1
        self._add_row(row, "Amplitude (AMP)", str(sys_info.get('amp', '-')))
        row += 1
        self._add_row(row, "Alpha (LPF)", str(sys_info.get('alpha', '-')))
        row += 1

        if self.meta["type"] == "digital":
            self._add_row(row, "Bit Rate", f"{sys_info.get('bit_rate', '-')} bps")
            row += 1
            self._add_row(row, "Pattern Length", str(sys_info.get('pattern_len', '-')))
            row += 1

        # Divider
        sep2 = QtWidgets.QFrame()
        sep2.setFrameShape(QtWidgets.QFrame.HLine)
        sep2.setStyleSheet("color: #444;")
        self.grid_layout.addWidget(sep2, row, 0, 1, 2)
        row += 1

        # Pot labels (values updated live in update_ui)
        for pot_cfg in self.meta["pots"]:
            label = pot_cfg["label"]
            attr  = f"_pot_val_{pot_cfg['pot']}"
            val   = getattr(self, attr, "—")
            self._add_row(row, label, str(val))
            row += 1

    # ─────────────────────────────────────────
    # Plot update and NCC
    # ─────────────────────────────────────────
    def update_ui(self, frame):
        global chunk_counter
        mode, N, FS, p1, p2, p3 = frame[:6]
        y_msg, y_mod, y_dem     = frame[6], frame[7], frame[8]

        # Store pot values for the settings panel
        self._pot_val_1 = f"{p1:.2f}"
        self._pot_val_2 = f"{p2:.2f}"
        self._pot_val_3 = f"{p3:.2f}"

        # Refresh pot value labels in grid
        if self.meta is not None:
            pots       = self.meta["pots"]
            pot_vals   = {1: p1, 2: p2, 3: p3}
            total_rows = self.grid_layout.rowCount()

            for i, pot_cfg in enumerate(pots):
                target_row = total_rows - len(pots) + i
                val_item   = self.grid_layout.itemAtPosition(target_row, 1)
                if val_item and val_item.widget():
                    raw_val = pot_vals[pot_cfg["pot"]]
                    val_item.widget().setText(f"{raw_val:.2f}")

        # Time axis
        t_ms = (np.arange(N) / FS) * 1000.0

        self.c1.setData(t_ms, y_msg)
        self.c2.setData(t_ms, y_mod)
        self.c3.setData(t_ms, y_dem)

        # Plot titles
        if self.meta is not None:
            tech_id   = self.meta["id"]
            tech_type = self.meta["type"]
            pots      = {p["pot"]: p for p in self.meta["pots"]}

            label_p1 = pots[1]["label"] if 1 in pots else "P1"
            label_p2 = pots[2]["label"] if 2 in pots else "P2"
            label_p3 = pots[3]["label"] if 3 in pots else "P3"

            self.p1.setTitle(f"MESSAGE ({tech_id}) | {label_p1}: {p1:.2f}")
            self.p2.setTitle(f"MODULATED ({tech_id}) | {label_p2}: {p2:.2f}")
            self.p3.setTitle(f"DEMODULATED ({tech_id}) | {label_p3}: {p3:.2f}")

            # ── Compute NCC ───────────────────────────────────────────
            chunk_counter += 1
            if tech_type == "analog":
                ncc_val = analog_ncc(y_msg, y_dem)
            else:
                ncc_val = digital_ncc(y_msg, y_dem)

            color    = ncc_color(ncc_val)
            ts       = time.strftime("%H:%M:%S")
            log_line = (
                f'<span style="color:#555;">[{ts}]</span> '
                f'<span style="color:#3498db;">[{tech_id}]</span> '
                f'Chunk #{chunk_counter} — NCC: '
                f'<span style="color:{color}; font-weight:bold;">{ncc_val:.1f}%</span>'
            )
            self.log_box.append(log_line)

            # Auto-scroll to bottom
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