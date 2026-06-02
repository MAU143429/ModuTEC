import shutil
import subprocess
from pathlib import Path

import serial.tools.list_ports


ROOT_DIR = Path(__file__).resolve().parent.parent

FIRMWARE_DIR = ROOT_DIR / "firmware"

FILES = [
    FIRMWARE_DIR / "io_pots.py",
    FIRMWARE_DIR / "main.py",
]


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

        result = subprocess.run(
            [
                mpremote,
                "connect",
                port,
                "fs",
                "cp",
                str(file_path),
                ":"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                f"copying... {file_path.name}\n\n"
                f"{result.stderr}"
            )

        log(f"[FW] OK -> {file_path.name}")

    log("[FW] Restarting Pico...")

    result = subprocess.run(
        [
            mpremote,
            "connect",
            port,
            "reset"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            f"Error restarting Pico\n\n"
            f"{result.stderr}"
        )

    log("[FW] Firmware updated successfully")

    return port