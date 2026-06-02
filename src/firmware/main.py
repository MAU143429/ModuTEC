import time
import struct
import sys
import json

from io_pots import Inputs

# ─────────────────────────────────────────
# Utilidades de mapeo
# ─────────────────────────────────────────
def lerp(a, b, x):
    return a + (b - a) * x

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def map_pot(raw, pot_cfg):
    val = lerp(pot_cfg["min"], pot_cfg["max"], raw)
    return clamp(val, pot_cfg["min"], pot_cfg["max"])

# ─────────────────────────────────────────
# Cargar configuración
# ─────────────────────────────────────────
with open("config.json", "r") as f:
    cfg = json.load(f)

techniques = cfg["techniques"]
sys_cfg    = cfg["system"]

# ─────────────────────────────────────────
# Carga dinámica de técnicas desde config
# ─────────────────────────────────────────
_state_map  = {}
_runner_map = {}

for tech in techniques:
    module_name = tech["file"].replace(".py", "")
    mod = __import__(module_name)
    _state_map[tech["id"]]  = mod.State()
    _runner_map[tech["id"]] = mod.compute_frame

# ─────────────────────────────────────────
# Protocolo serial
# ─────────────────────────────────────────
SYNC         = b"MDT2"
HEADER_FMT   = "<BHHfff"
HEADER_LEN   = struct.calcsize(HEADER_FMT)

SYNC_META    = b"MDTM"
META_LEN_FMT = "<H"

# ─────────────────────────────────────────
# Método de envío de metadata
# ─────────────────────────────────────────
def send_meta(out, tech, sys_cfg):
    meta = {
        "id":   tech["id"],
        "type": tech["type"],
        "pots": [
            {"pot": p["pot"], "param": p["param"], "label": p["label"]}
            for p in tech["pots"]
        ],
        "system": {
            "fs":          sys_cfg["fs"],
            "n":           sys_cfg["n"],
            "amp":         sys_cfg["amp"],
            "bit_rate":    sys_cfg["bit_rate"],
            "pattern_len": sys_cfg["pattern_len"],
            "alpha":       sys_cfg["alpha"],
        },
    }
    payload = json.dumps(meta).encode("utf-8")
    out.write(SYNC_META)
    out.write(struct.pack(META_LEN_FMT, len(payload)))
    out.write(payload)

# ─────────────────────────────────────────
# Hardware
# ─────────────────────────────────────────
inp = Inputs(pot1_pin=26, pot2_pin=27, pot3_pin=28, sw_pin=5)
out = sys.stdout.buffer

# ─────────────────────────────────────────
# Loop principal
# ─────────────────────────────────────────
last_tech_idx = -1

while True:
    mode_idx_0, x1, x2, x3 = inp.read()

    tech_idx = 0 if mode_idx_0 else 1
    tech     = techniques[tech_idx]
    tech_id  = tech["id"]

    # Enviar metadata solo cuando cambia la técnica
    if tech_idx != last_tech_idx:
        send_meta(out, tech, sys_cfg)
        last_tech_idx = tech_idx

    # Mapear pots a parámetros según config
    raw_vals = [x1, x2, x3]
    params   = {}
    p1_val = p2_val = p3_val = 0.0

    for pot_cfg in tech["pots"]:
        pot_num = pot_cfg["pot"]
        raw     = raw_vals[pot_num - 1]
        val     = map_pot(raw, pot_cfg)
        params[pot_cfg["param"]] = val

        if pot_num == 1: p1_val = float(val)
        if pot_num == 2: p2_val = float(val)
        if pot_num == 3: p3_val = float(val)

    # Ejecutar técnica
    state  = _state_map[tech_id]
    runner = _runner_map[tech_id]
    payload_m, payload_mod, payload_dem = runner(state, params, sys_cfg)

    # Enviar frame de señal
    header = SYNC + struct.pack(
        HEADER_FMT,
        tech_idx,
        sys_cfg["n"],
        sys_cfg["fs"],
        p1_val, p2_val, p3_val
    )

    out.write(header)
    out.write(payload_m)
    out.write(payload_mod)
    out.write(payload_dem)

    time.sleep_ms(20)