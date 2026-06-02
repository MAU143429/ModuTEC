import math
import struct

# ── Definición explícita del orden de parámetros ──
PARAM_ORDER = ["param_1", "param_2", "param_3"]


def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


class State:
    """
    Estado de TECHNIQUE_NAME.
    Agregar aquí todas las variables que necesitan persistir entre frames.
    """

    __slots__ = (
        # Ejemplo: "phase_c", "lpf_y", etc.
    )

    def __init__(self):
        pass
        # Ejemplo:
        # self.phase_c = 0.0
        # self.lpf_y   = 0.0


def compute_frame(state, params, sys_cfg):
    """
    Interfaz estándar ModuTEC.

    Parámetros esperados en params (deben coincidir con config.json):
        - param_1 : descripción y unidades
        - param_2 : descripción y unidades
        - param_3 : descripción y unidades

    Retorna:
        payload_m   : bytearray int16 — señal mensaje / bits originales
        payload_mod : bytearray int16 — señal modulada
        payload_dem : bytearray int16 — señal demodulada / bits recuperados
    """

    # ── Extraer parámetros del sistema ──────────────────────────────────
    FS    = sys_cfg["fs"]
    N     = sys_cfg["n"]
    AMP   = sys_cfg["amp"]
    alpha = sys_cfg["alpha"]
    # Si la técnica es digital, también puede necesitar:
    # bit_rate    = sys_cfg["bit_rate"]
    # pattern_len = sys_cfg["pattern_len"]

    # ── Extraer parámetros de la técnica (vienen del config via pots) ───
    param_1 = params["param_1"]
    param_2 = params["param_2"]
    param_3 = params["param_3"]

    # ── Inicializar buffers de salida ────────────────────────────────────
    payload_m   = bytearray(2 * N)
    payload_mod = bytearray(2 * N)
    payload_dem = bytearray(2 * N)

    # ── Restaurar estado ─────────────────────────────────────────────────
    # Ejemplo:
    # phase_c = state.phase_c
    # lpf_y   = state.lpf_y

    # ── Loop de generación sample a sample ──────────────────────────────
    for i in range(N):

        # Calcular señales
        msg = 0.0  # señal mensaje normalizada -1..1
        s   = 0.0  # señal modulada normalizada
        dem = 0.0  # señal demodulada normalizada -1..1

        # Escribir muestras en buffers
        struct.pack_into("<h", payload_m,   2 * i, int(AMP * msg))
        struct.pack_into("<h", payload_mod, 2 * i, int(AMP * s))
        struct.pack_into("<h", payload_dem, 2 * i, int(AMP * dem))

        # Actualizar variables de fase u otras variables internas del loop

    # ── Guardar estado para el próximo frame ─────────────────────────────
    # Ejemplo:
    # state.phase_c = phase_c
    # state.lpf_y   = lpf_y

    return payload_m, payload_mod, payload_dem