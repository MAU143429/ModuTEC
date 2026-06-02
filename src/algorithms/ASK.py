import math
import struct

PARAM_ORDER = ["seed", "f_carrier", "threshold"]


def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


class State:
    """Estado para ASK/OOK (bitstream pseudo-aleatorio repetible)."""

    __slots__ = (
        "phase_c",
        "lpf_y",
        "sample_ctr",
        "pattern",
        "pattern_len",
        "samples_per_bit",
        "last_seed",
        "last_thr_q",
        "last_bit",
    )

    def __init__(self):
        self.phase_c         = 0.0
        self.lpf_y           = 0.0
        self.sample_ctr      = 0
        self.pattern         = None
        self.pattern_len     = 0
        self.samples_per_bit = 50
        self.last_seed       = None
        self.last_thr_q      = None
        self.last_bit        = 0


def _lcg_next(u32_state):
    u32_state = (1664525 * u32_state + 1013904223) & 0xFFFFFFFF
    return u32_state, (u32_state / 4294967296.0)


def _gen_bit_pattern(seed, threshold, nbits):
    """
    Genera patrón pseudoaleatorio binario usando:
        r > threshold -> 1
        r <= threshold -> 0
    """
    threshold = _clamp(threshold, 0.0, 1.0)

    st = seed & 0xFFFFFFFF

    bits = bytearray(nbits)

    for i in range(nbits):
        st, r = _lcg_next(st)
        bits[i] = 1 if r > threshold else 0

    return bits


def compute_frame(state, params, sys_cfg):
    """
    Interfaz estándar ModuTEC.

    params:
        seed
        f_carrier
        threshold

    retorna:
        payload_m
        payload_mod
        payload_dem
    """

    FS          = sys_cfg["fs"]
    N           = sys_cfg["n"]
    AMP         = sys_cfg["amp"]
    alpha       = sys_cfg["alpha"]
    bit_rate    = sys_cfg["bit_rate"]
    pattern_len = sys_cfg["pattern_len"]

    seed      = int(params["seed"])
    f_carrier = params["f_carrier"]
    threshold = params["threshold"]

    spb = int(FS / bit_rate)

    if spb < 4:
        spb = 4

    state.samples_per_bit = spb

    thr   = _clamp(threshold, 0.0, 1.0)
    thr_q = int(thr * 100)

    # Regenerar patrón solo cuando cambia seed o threshold TX
    if (
        state.pattern is None
        or state.pattern_len != pattern_len
        or state.last_seed != seed
        or state.last_thr_q != thr_q
    ):
        state.pattern     = _gen_bit_pattern(seed, thr, pattern_len)
        state.pattern_len = pattern_len
        state.sample_ctr  = 0
        state.lpf_y       = 0.0

        state.last_seed   = seed
        state.last_thr_q  = thr_q

    wc         = 2.0 * math.pi * f_carrier / FS
    phase_c    = state.phase_c
    lpf_y      = state.lpf_y
    sample_ctr = state.sample_ctr

    bits = state.pattern
    plen = state.pattern_len

    payload_m   = bytearray(2 * N)
    payload_mod = bytearray(2 * N)
    payload_dem = bytearray(2 * N)

    last_bit = state.last_bit

    # Histéresis del detector
    hysteresis = 0.08

    thr_high = _clamp(thr + hysteresis, 0.0, 1.0)
    thr_low  = _clamp(thr - hysteresis, 0.0, 1.0)

    for i in range(N):

        # =========================================================
        # GENERACIÓN DEL BIT
        # =========================================================

        bit_idx = (sample_ctr // spb) % plen

        b = 1 if bits[bit_idx] else 0

        msg = 1.0 if b else -1.0

        # =========================================================
        # MODULACIÓN ASK/OOK
        # =========================================================

        car = math.cos(phase_c)

        s = (1.0 if b else 0.0) * car

        # =========================================================
        # DEMODULACIÓN COHERENTE
        # =========================================================

        prod = s * car

        # LPF recursivo
        lpf_y = lpf_y + alpha * (prod - lpf_y)

        # Compensación de amplitud promedio cos²
        b_est = 2.0 * lpf_y

        # =========================================================
        # DETECTOR CON HISTÉRESIS
        # =========================================================

        if last_bit == 0:
            b_hat = 1 if b_est > thr_high else 0
        else:
            b_hat = 0 if b_est < thr_low else 1

        last_bit = b_hat

        dem = 1.0 if b_hat else -1.0

        # =========================================================
        # PAYLOADS
        # =========================================================

        struct.pack_into("<h", payload_m,   2 * i, int(AMP * msg))
        struct.pack_into("<h", payload_mod, 2 * i, int(AMP * s))
        struct.pack_into("<h", payload_dem, 2 * i, int(AMP * dem))

        # =========================================================
        # UPDATE
        # =========================================================

        phase_c += wc

        if phase_c >= 2.0 * math.pi:
            phase_c -= 2.0 * math.pi

        sample_ctr += 1

    # =============================================================
    # GUARDAR ESTADO
    # =============================================================

    state.phase_c    = phase_c
    state.lpf_y      = lpf_y
    state.sample_ctr = sample_ctr
    state.last_bit   = last_bit

    return payload_m, payload_mod, payload_dem