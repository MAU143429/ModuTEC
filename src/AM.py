import math
import struct


class State:
    """Estado para AM (mantiene continuidad entre frames)."""

    __slots__ = ("phase_m", "phase_c", "lpf_y")

    def __init__(self):
        self.phase_m = 0.0
        self.phase_c = 0.0
        self.lpf_y   = 0.0


def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def compute_frame(state, params, sys_cfg):
    """
    Interfaz estándar ModuTEC.
    params esperados: f_signal, f_carrier, mu
    Retorna: (payload_m, payload_mod, payload_dem) como bytearrays int16.
    """
    FS    = sys_cfg["fs"]
    N     = sys_cfg["n"]
    AMP   = sys_cfg["amp"]
    alpha = sys_cfg["alpha"]

    f_signal  = params["f_signal"]
    f_carrier = params["f_carrier"]
    mu        = params["mu"]

    wm = 2.0 * math.pi * f_signal  / FS
    wc = 2.0 * math.pi * f_carrier / FS

    payload_m   = bytearray(2 * N)
    payload_mod = bytearray(2 * N)
    payload_dem = bytearray(2 * N)

    norm    = 1.0 / (1.0 + mu) if mu > 0.0 else 1.0
    phase_m = state.phase_m
    phase_c = state.phase_c
    lpf_y   = state.lpf_y

    for i in range(N):
        msg = math.sin(phase_m)
        car = math.cos(phase_c)

        s    = (1.0 + mu * msg) * car
        prod = s * car
        lpf_y = lpf_y + alpha * (prod - lpf_y)

        if mu >= 0.02:
            msg_est = (2.0 * lpf_y - 1.0) / mu
        else:
            msg_est = 0.0

        msg_est = _clamp(msg_est, -1.0, 1.0)

        struct.pack_into("<h", payload_m,   2 * i, int(AMP * msg))
        struct.pack_into("<h", payload_mod, 2 * i, int(AMP * s * norm))
        struct.pack_into("<h", payload_dem, 2 * i, int(AMP * msg_est))

        phase_m += wm
        phase_c += wc
        if phase_m >= 2.0 * math.pi:
            phase_m -= 2.0 * math.pi
        if phase_c >= 2.0 * math.pi:
            phase_c -= 2.0 * math.pi

    state.phase_m = phase_m
    state.phase_c = phase_c
    state.lpf_y   = lpf_y

    return payload_m, payload_mod, payload_dem