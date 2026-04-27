from PyQt5 import QtCore, QtWidgets
from ui_styles import DARK_BTN, DIALOG_BG


class HelpDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ModuTEC — Ayuda")
        self.setMinimumSize(560, 460)
        self.setStyleSheet(DIALOG_BG)

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
            "background-color: #121212; color: #ecf0f1;"
            "font-family: Consolas, monospace; font-size: 12px;"
            "border: 1px solid #333;"
        )
        text.setHtml("""
<style>
  h3  { color: #3498db; margin-bottom: 2px; }
  p   { margin: 4px 0 10px 0; }
  li  { margin: 2px 0; }
  b   { color: #f1c40f; }
</style>

<h3>1. Seleccionar puerto COM</h3>
<p>Usa el dropdown en la barra superior para elegir el puerto COM donde está conectado
el ModuTEC Modulator (Raspberry Pi Pico). Solo se muestran puertos con dispositivos
detectados. Usa <b>⟳</b> para refrescar la lista.</p>

<h3>2. Activar / Desactivar monitor</h3>
<p>El botón <b>RUN / STOP</b> inicia o pausa la lectura serial. Detén el monitor antes de
cargar una nueva configuración para liberar el puerto.</p>

<h3>3. Config Tool</h3>
<p>Abre la ventana de configuración con el botón <b>Config Tool</b>. Desde ahí puedes:</p>
<ul>
  <li>Cargar dos archivos <b>.py</b> de técnica (deben seguir la plantilla ModuTEC).</li>
  <li>Asignar rangos min/max para cada parámetro (pot).</li>
  <li>Ajustar parámetros del sistema (FS, N, AMP, etc.).</li>
  <li>Crear el archivo <b>config.json</b> y copiarlo al dispositivo vía <b>mpremote</b>.</li>
</ul>

<h3>4. NCC Log</h3>
<p>El panel derecho muestra en tiempo real la métrica de correlación normalizada (NCC)
entre la señal mensaje y la señal demodulada.<br>
<b style="color:#2ecc71;">Verde &gt;70%</b> —
<b style="color:#f39c12;">Amarillo 65–70%</b> —
<b style="color:#e74c3c;">Rojo &lt;65%</b></p>

<h3>5. Flujo típico de uso</h3>
<p>
1. Conecta el Pico → selecciona el COM → RUN<br>
2. Para cambiar config: STOP → Config Tool → crear → cargar → RUN
</p>
""")
        lay.addWidget(text)

        close_btn = QtWidgets.QPushButton("Cerrar")
        close_btn.setStyleSheet(DARK_BTN)
        close_btn.clicked.connect(self.accept)
        lay.addWidget(close_btn, alignment=QtCore.Qt.AlignRight)