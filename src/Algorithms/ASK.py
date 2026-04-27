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
    )

    def __init__(self):
        self.phase_c        = 0.0
        self.lpf_y          = 0.0
        self.sample_ctr     = 0
        self.pattern        = None
        self.pattern_len    = 0
        self.samples_per_bit = 50
        self.last_seed      = None
        self.last_thr_q     = None


def _lcg_next(u32_state):
    u32_state = (1664525 * u32_state + 1013904223) & 0xFFFFFFFF
    return u32_state, (u32_state / 4294967296.0)


def _gen_bit_pattern(seed, threshold, nbits):
    threshold = _clamp(threshold, 0.0, 1.0)
    st   = seed & 0xFFFFFFFF
    bits = bytearray(nbits)
    for i in range(nbits):
        st, r = _lcg_next(st)
        bits[i] = 1 if r > threshold else 0
    return bits


def compute_frame(state, params, sys_cfg):
    """
    Interfaz estándar ModuTEC.
    params esperados: seed, f_carrier, threshold
    Retorna: (payload_m, payload_mod, payload_dem) como bytearrays int16.
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

    if (state.pattern is None
            or state.pattern_len != pattern_len
            or state.last_seed   != seed
            or state.last_thr_q  != thr_q):
        state.pattern     = _gen_bit_pattern(seed, thr, pattern_len)
        state.pattern_len = pattern_len
        state.sample_ctr  = 0
        state.lpf_y       = 0.0
        state.last_seed   = seed
        state.last_thr_q  = thr_q

    wc       = 2.0 * math.pi * f_carrier / FS
    phase_c  = state.phase_c
    lpf_y    = state.lpf_y
    sample_ctr = state.sample_ctr
    bits     = state.pattern
    plen     = state.pattern_len

    payload_m   = bytearray(2 * N)
    payload_mod = bytearray(2 * N)
    payload_dem = bytearray(2 * N)

    for i in range(N):
        bit_idx = (sample_ctr // spb) % plen
        b       = 1 if bits[bit_idx] else 0
        msg     = 1.0 if b else -1.0
        car     = math.cos(phase_c)
        s       = (1.0 if b else 0.0) * car

        prod  = s * car
        lpf_y = lpf_y + alpha * (prod - lpf_y)

        b_est = 2.0 * lpf_y
        b_hat = 1 if b_est > thr else 0
        dem   = 1.0 if b_hat else -1.0

        struct.pack_into("<h", payload_m,   2 * i, int(AMP * msg))
        struct.pack_into("<h", payload_mod, 2 * i, int(AMP * s))
        struct.pack_into("<h", payload_dem, 2 * i, int(AMP * dem))

        phase_c    += wc
        if phase_c >= 2.0 * math.pi:
            phase_c -= 2.0 * math.pi
        sample_ctr += 1

    state.phase_c    = phase_c
    state.lpf_y      = lpf_y
    state.sample_ctr = sample_ctr

    return payload_m, payload_mod, payload_dem