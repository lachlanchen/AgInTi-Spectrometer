"""Host backend for the AgInTi C12880 V2 high-rate firmware."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, asdict
import struct
import threading
import time

import numpy as np
import serial
from serial.tools import list_ports

from .protocol import SpectrumFrame, exposure_ticks
from .protocol_v2 import (
    COMMAND_HEADER, OP_CONFIGURE, OP_GET_CAPS, OP_HELLO, OP_START, OP_STOP,
    V2ProtocolError, V2StreamDecoder, build_command, decode_reply,
    reply_total_bytes,
)


class V2DeviceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class V2PortDescriptor:
    device: str
    description: str
    manufacturer: str | None
    vid: int | None
    pid: int | None
    serial_number: str | None
    score: int = 1000

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["vid_pid"] = (
            f"{self.vid:04X}:{self.pid:04X}"
            if self.vid is not None and self.pid is not None else None
        )
        return payload


class V2C12880Device:
    BAUDRATE = 256000
    SENSOR_CLOCK_HZ = 5_000_000

    def __init__(self, port: str | None = None, timeout: float = 0.03) -> None:
        self.requested_port = port
        self.timeout = timeout
        self.serial: serial.Serial | None = None
        self.descriptor: V2PortDescriptor | None = None
        self._lock = threading.RLock()
        self.exposure_ms = 0.01
        self.output_mask = 0x01
        self.trigger_mode = "internal"
        self.correction_words = np.empty(0, dtype=np.uint16)
        self.firmware_name = "AgInTi C12880 V2"
        self.transport_mode = "v2-stream"
        self.decoder = V2StreamDecoder()
        self.frames = deque(maxlen=128)
        self.command_sequence = 1
        self.last_frame_sequence: int | None = None
        self.sequence_gaps = 0
        self.last_raw = b""
        self._stream_started = False

    @property
    def is_open(self) -> bool:
        return bool(self.serial and self.serial.is_open)

    def _select_port(self) -> V2PortDescriptor:
        ports = list(list_ports.comports())
        if self.requested_port:
            selected = next((port for port in ports if port.device == self.requested_port), None)
            if selected is None:
                raise V2DeviceError(f"requested serial port {self.requested_port} is unavailable")
        else:
            selected = next(
                (port for port in ports if (port.vid, port.pid) == (0x0483, 0x5740)),
                None,
            )
            if selected is None:
                raise V2DeviceError("C12880 USB serial device not found")
        return V2PortDescriptor(
            selected.device, selected.description or "AgInTi C12880 V2",
            selected.manufacturer, selected.vid, selected.pid,
            selected.serial_number,
        )

    def _next_command(self, opcode: int, payload: bytes = b"") -> tuple[int, bytes]:
        sequence = self.command_sequence
        self.command_sequence = (sequence + 1) & 0xFFFFFFFF
        return sequence, build_command(opcode, sequence, payload)

    def _read_exact(self, size: int, deadline: float) -> bytes:
        assert self.serial is not None
        output = bytearray()
        while len(output) < size and time.monotonic() < deadline:
            chunk = self.serial.read(size - len(output))
            if chunk:
                output.extend(chunk)
        return bytes(output)

    def _request(self, opcode: int, payload: bytes = b"", timeout: float = 0.25):
        assert self.serial is not None
        sequence, command = self._next_command(opcode, payload)
        self.serial.write(command)
        self.serial.flush()
        deadline = time.monotonic() + timeout
        header = self._read_exact(COMMAND_HEADER.size, deadline)
        if len(header) != COMMAND_HEADER.size:
            raise V2DeviceError("V2 firmware did not reply")
        try:
            total = reply_total_bytes(header)
            body = self._read_exact(total - len(header), deadline)
            reply = decode_reply(header + body)
        except V2ProtocolError as exc:
            raise V2DeviceError(str(exc)) from exc
        if len(header) + len(body) != total:
            raise V2DeviceError("short V2 firmware reply")
        expected_reply_opcode = opcode | 0x80
        if (
            reply.sequence != sequence
            or reply.opcode != expected_reply_opcode
            or reply.status
        ):
            raise V2DeviceError(
                f"V2 command rejected: opcode=0x{reply.opcode:02X}, "
                f"expected=0x{expected_reply_opcode:02X}, status={reply.status}"
            )
        return reply

    def _send(self, opcode: int, payload: bytes = b"") -> None:
        assert self.serial is not None
        _sequence, command = self._next_command(opcode, payload)
        self.serial.write(command)

    def _configuration_payload(self) -> bytes:
        clocks = max(1, exposure_ticks(self.exposure_ms))
        return struct.pack(
            "<IIBB2x", self.SENSOR_CLOCK_HZ, clocks,
            self.output_mask & 0x03, 1,
        )

    def connect(self) -> V2PortDescriptor:
        with self._lock:
            if self.is_open:
                assert self.descriptor is not None
                return self.descriptor
            self.descriptor = self._select_port()
            try:
                self.serial = serial.Serial(
                    self.descriptor.device, self.BAUDRATE, timeout=self.timeout,
                    write_timeout=0.25,
                )
                self.serial.dtr = True
                self.serial.rts = True
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()
                try:
                    self.serial.set_buffer_size(rx_size=1 << 20, tx_size=65536)
                except (AttributeError, OSError, serial.SerialException):
                    pass
                hello = self._request(OP_HELLO, timeout=0.18)
                name = hello.payload.rstrip(b"\x00").decode("utf-8", errors="replace").strip()
                if name:
                    self.firmware_name = name
                self._request(OP_GET_CAPS, timeout=0.18)
                self._request(OP_CONFIGURE, self._configuration_payload(), timeout=0.18)
                self._request(OP_START, timeout=0.18)
                self._stream_started = True
                self.decoder.reset()
                self.frames.clear()
                self.last_frame_sequence = None
                return self.descriptor
            except Exception:
                self.close()
                raise

    def close(self) -> None:
        with self._lock:
            handle = self.serial
            self.serial = None
            if handle is not None:
                try:
                    if handle.is_open and self._stream_started:
                        _sequence, command = self._next_command(OP_STOP)
                        handle.write(command)
                        handle.flush()
                except Exception:
                    pass
                try:
                    handle.close()
                except Exception:
                    pass
            self._stream_started = False
            self.frames.clear()
            self.decoder.reset()

    def set_trigger_mode(self, trigger_mode: str) -> None:
        if trigger_mode not in ("internal", "external"):
            raise ValueError("trigger mode must be internal or external")
        self.trigger_mode = trigger_mode

    def _reconfigure(self) -> None:
        if self.is_open:
            self._send(OP_CONFIGURE, self._configuration_payload())
            self.frames.clear()

    def set_exposure(self, exposure_ms: float) -> None:
        value = min(1000.0, max(0.0002, float(exposure_ms)))
        if abs(value - self.exposure_ms) > 1e-12:
            self.exposure_ms = value
            self._reconfigure()

    def set_output_mask(self, output_mask: int) -> None:
        value = int(output_mask) & 0x03
        if value != self.output_mask:
            self.output_mask = value
            self._reconfigure()

    def _read_stream(self, deadline: float) -> None:
        assert self.serial is not None
        while not self.frames and time.monotonic() < deadline:
            waiting = self.serial.in_waiting
            request = min(65536, waiting if waiting > 0 else 4096)
            chunk = self.serial.read(request)
            if chunk:
                self.frames.extend(self.decoder.feed(chunk))

    def acquire(self, exposure_ms: float | None = None) -> SpectrumFrame:
        with self._lock:
            if not self.is_open:
                self.connect()
            if exposure_ms is not None:
                self.set_exposure(exposure_ms)
            deadline = time.monotonic() + max(0.25, self.exposure_ms / 1000.0 + 0.12)
            self._read_stream(deadline)
            if not self.frames:
                raise V2DeviceError("no valid spectrum frame received from V2 firmware")
            frame = self.frames.popleft()
            if frame.status & 0x03:
                raise V2DeviceError(f"sensor capture error flags: 0x{frame.status:08X}")
            if frame.active_pixels < 288 or len(frame.samples) < 288:
                raise V2DeviceError(f"V2 frame has only {frame.active_pixels} active pixels")
            if self.last_frame_sequence is not None:
                gap = (frame.sequence - self.last_frame_sequence - 1) & 0xFFFFFFFF
                if gap < 0x80000000:
                    self.sequence_gaps += gap
            self.last_frame_sequence = frame.sequence
            self.last_raw = frame.raw
            actual_exposure_ms = (
                frame.exposure_clocks * 1000.0 / frame.sensor_clock_hz
                if frame.sensor_clock_hz else self.exposure_ms
            )
            return SpectrumFrame(
                sequence=frame.sequence,
                timestamp_ns=time.time_ns(),
                exposure_ms=actual_exposure_ms,
                counts=np.asarray(frame.samples[:288], dtype=np.float64),
                prefix_words=(
                    frame.status, frame.dropped_frames,
                    frame.exposure_clocks, frame.sensor_clock_hz,
                ),
                raw_size=len(frame.raw),
                source=f"hardware-v2:{self.descriptor.device if self.descriptor else '?'}",
            )

    def diagnostic_report(self) -> dict[str, object]:
        return {
            "identity_raw_hex": "V2",
            "identity_valid": True,
            "correction_bytes": 0,
            "transport_mode": self.transport_mode,
            "firmware_name": self.firmware_name,
            "output_mask": self.output_mask,
            "trigger_mode": self.trigger_mode,
            "exposure_ms": self.exposure_ms,
            "sequence_gaps": self.sequence_gaps,
            "decoder_crc_errors": self.decoder.crc_errors,
            "decoder_discarded_bytes": self.decoder.discarded_bytes,
        }
