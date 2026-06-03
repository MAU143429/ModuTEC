import shutil
import os
import subprocess
from pathlib import Path
import serial.tools.list_ports
from resource_path import resource_path


FILES = [
    Path(resource_path("firmware/io_pots.py")),
    Path(resource_path("firmware/main.py")),
]

def run_hidden(cmd):

    startupinfo = None
    creationflags = 0

    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        creationflags = subprocess.CREATE_NO_WINDOW

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        startupinfo=startupinfo,
        creationflags=creationflags
    )

def find_pico_port():
    """
    Detecta automáticamente una Raspberry Pi Pico.
    """

    for port in serial.tools.list_ports.comports():

        if port.vid == 0x2E8A:
            return port.device

    return None


def flash_firmware(log_callback=None):

    mpremote = shutil.which("mpremote")

    if not mpremote:
        raise RuntimeError(
            "mpremote is not installed.\n\n"
            "Run:\n"
            "pip install mpremote"
        )

    port = find_pico_port()

    if port is None:
        raise RuntimeError(
            "No Raspberry Pi Pico found."
        )

    def log(msg):
        if log_callback:
            log_callback(msg)

    log(f"[FW] Pico detected at {port}")

    for file_path in FILES:

        log(f"[FW] Copying {file_path.name}...")

        result = run_hidden(
            [
                mpremote,
                "connect",
                port,
                "fs",
                "cp",
                str(file_path),
                ":"
            ]
        )

        if result.returncode != 0:

            raise RuntimeError(
                f"copying... {file_path.name}\n\n"
                f"{result.stderr}"
            )

        log(f"[FW] OK -> {file_path.name}")

    log("[FW] Restarting Pico...")

    result = run_hidden(
        [
            mpremote,
            "connect",
            port,
            "reset"
        ]
    )

    if result.returncode != 0:

        raise RuntimeError(
            f"Error restarting Pico\n\n"
            f"{result.stderr}"
        )

    log("[FW] Firmware updated successfully")

    return port