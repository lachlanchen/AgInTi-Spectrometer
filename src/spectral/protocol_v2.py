"""AgInTi C12880 V2 command and streaming-frame codecs."""

from __future__ import annotations

from dataclasses import dataclass
import struct
import zlib


COMMAND_MAGIC = b"ASC2"
REPLY_MAGIC = b"ASR2"
FRAME_MAGIC = b"ASP2"
PROTOCOL_VERSION = 2

COMMAND_HEADER = struct.Struct("<4sBBHIHHI")
FRAME_HEADER = struct.Struct("<4sBBHIIQIIHHIII")
COMMAND_CRC_OFFSET = 16
FRAME_CRC_OFFSET = 44

OP_HELLO = 0x01
OP_GET_CAPS = 0x02
OP_CONFIGURE = 0x10
OP_START = 0x12
OP_STOP = 0x13


class V2ProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class V2Reply:
    opcode: int
    status: int
    sequence: int
    payload: bytes


@dataclass(frozen=True)
class V2Frame:
    flags: int
    sequence: int
    timestamp_us: int
    exposure_clocks: int
    sensor_clock_hz: int
    active_pixels: int
    raw_samples: int
    status: int
    dropped_frames: int
    samples: tuple[int, ...]
    raw: bytes


def _record_crc(record: bytes, offset: int) -> int:
    scratch = bytearray(record)
    scratch[offset : offset + 4] = b"\x00\x00\x00\x00"
    return zlib.crc32(scratch) & 0xFFFFFFFF


def build_command(opcode: int, sequence: int, payload: bytes = b"", flags: int = 0) -> bytes:
    record = bytearray(
        COMMAND_HEADER.pack(
            COMMAND_MAGIC,
            PROTOCOL_VERSION,
            opcode & 0xFF,
            flags & 0xFFFF,
            sequence & 0xFFFFFFFF,
            len(payload),
            0,
            0,
        )
        + payload
    )
    struct.pack_into("<I", record, COMMAND_CRC_OFFSET, _record_crc(record, COMMAND_CRC_OFFSET))
    return bytes(record)


def reply_total_bytes(header: bytes) -> int:
    if len(header) < COMMAND_HEADER.size:
        raise V2ProtocolError("short V2 reply header")
    magic, version, _opcode, _flags, _sequence, payload_bytes, _reserved, _crc = COMMAND_HEADER.unpack_from(header)
    if magic != REPLY_MAGIC or version != PROTOCOL_VERSION:
        raise V2ProtocolError("invalid V2 reply signature")
    if payload_bytes > 8192:
        raise V2ProtocolError("implausible V2 reply length")
    return COMMAND_HEADER.size + payload_bytes


def decode_reply(record: bytes) -> V2Reply:
    total = reply_total_bytes(record)
    if len(record) != total:
        raise V2ProtocolError("incomplete V2 reply")
    _magic, _version, opcode, status, sequence, _payload_bytes, _reserved, crc = COMMAND_HEADER.unpack_from(record)
    if crc != _record_crc(record, COMMAND_CRC_OFFSET):
        raise V2ProtocolError("V2 reply CRC mismatch")
    return V2Reply(opcode, status, sequence, record[COMMAND_HEADER.size:])


def decode_frame(record: bytes) -> V2Frame:
    if len(record) < FRAME_HEADER.size:
        raise V2ProtocolError("short V2 frame")
    fields = FRAME_HEADER.unpack_from(record)
    (
        magic, version, header_bytes, flags, sequence, payload_bytes,
        timestamp_us, exposure_clocks, sensor_clock_hz, active_pixels,
        raw_samples, status, dropped_frames, crc,
    ) = fields
    if magic != FRAME_MAGIC or version != PROTOCOL_VERSION or header_bytes != FRAME_HEADER.size:
        raise V2ProtocolError("invalid V2 frame signature")
    total = header_bytes + payload_bytes
    if payload_bytes % 2 or payload_bytes > 8192 or total != len(record):
        raise V2ProtocolError("invalid V2 frame length")
    if crc != _record_crc(record, FRAME_CRC_OFFSET):
        raise V2ProtocolError("V2 frame CRC mismatch")
    samples = struct.unpack_from(f"<{payload_bytes // 2}H", record, header_bytes)
    if active_pixels > len(samples) or raw_samples > len(samples):
        raise V2ProtocolError("invalid V2 sample counts")
    return V2Frame(
        flags, sequence, timestamp_us, exposure_clocks, sensor_clock_hz,
        active_pixels, raw_samples, status, dropped_frames, samples, record,
    )


class V2StreamDecoder:
    """Separate replies and validated spectrum frames from one CDC stream."""

    def __init__(self) -> None:
        self.buffer = bytearray()
        self.discarded_bytes = 0
        self.crc_errors = 0

    def reset(self) -> None:
        self.buffer.clear()

    def feed(self, data: bytes) -> list[V2Frame]:
        if data:
            self.buffer.extend(data)
        frames: list[V2Frame] = []
        while True:
            positions = [
                position
                for position in (self.buffer.find(FRAME_MAGIC), self.buffer.find(REPLY_MAGIC))
                if position >= 0
            ]
            if not positions:
                if len(self.buffer) > 3:
                    removed = len(self.buffer) - 3
                    del self.buffer[:removed]
                    self.discarded_bytes += removed
                break
            start = min(positions)
            if start:
                del self.buffer[:start]
                self.discarded_bytes += start

            if self.buffer.startswith(REPLY_MAGIC):
                if len(self.buffer) < COMMAND_HEADER.size:
                    break
                try:
                    total = reply_total_bytes(self.buffer[: COMMAND_HEADER.size])
                except V2ProtocolError:
                    del self.buffer[0]
                    self.discarded_bytes += 1
                    continue
                if len(self.buffer) < total:
                    break
                record = bytes(self.buffer[:total])
                del self.buffer[:total]
                try:
                    decode_reply(record)
                except V2ProtocolError:
                    self.crc_errors += 1
                continue

            if len(self.buffer) < FRAME_HEADER.size:
                break
            try:
                header = FRAME_HEADER.unpack_from(self.buffer)
                header_bytes, payload_bytes = header[2], header[5]
                if header_bytes != FRAME_HEADER.size or payload_bytes > 8192 or payload_bytes % 2:
                    raise V2ProtocolError("invalid streaming header")
                total = header_bytes + payload_bytes
            except (struct.error, V2ProtocolError):
                del self.buffer[0]
                self.discarded_bytes += 1
                continue
            if len(self.buffer) < total:
                break
            record = bytes(self.buffer[:total])
            del self.buffer[:total]
            try:
                frames.append(decode_frame(record))
            except V2ProtocolError:
                self.crc_errors += 1
        return frames
