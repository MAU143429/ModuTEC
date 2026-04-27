import struct
import json
import numpy as np

# ─────────────────────────────────────────
# Protocol constants
# ─────────────────────────────────────────
SYNC         = b"MDT2"
SYNC_META    = b"MDTM"
HEADER_FMT   = "<BHHfff"
HEADER_LEN   = struct.calcsize(HEADER_FMT)
META_LEN_FMT = "<H"
META_LEN_LEN = struct.calcsize(META_LEN_FMT)

BAUD = 115200


class SerialParser:
    """
    Holds the receive buffer and parses MDT2 / MDTM frames.
    Completely decoupled from Qt — call feed() then try_read_* in the tick loop.
    """

    def __init__(self):
        self.buf = bytearray()

    def reset(self):
        self.buf = bytearray()

    def feed(self, data: bytes):
        self.buf.extend(data)
        if len(self.buf) > 500_000:
            self.buf = self.buf[-100_000:]

    def read_available(self, ser) -> bytes:
        """Read all waiting bytes from an open serial.Serial instance."""
        try:
            n = ser.in_waiting
            if n > 0:
                return ser.read(n)
        except Exception as e:
            print(f"[SerialParser] read error: {e}")
        return b""

    # ── Frame parsers ─────────────────────────────────────────────

    def try_read_meta(self):
        """
        Extract the next MDTM metadata frame.
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
            return None, idx + 1

        return meta, start_json + json_len

    def try_read_frame(self):
        """
        Extract the next MDT2 signal frame.
        Returns (frame_tuple, bytes_consumed) or (None, 0).
        frame_tuple = (mode, N, FS, p1, p2, p3, y_msg, y_mod, y_dem)
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

    def consume(self, n: int):
        del self.buf[:n]