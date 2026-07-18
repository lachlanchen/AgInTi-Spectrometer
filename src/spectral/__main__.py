"""Command-line entry point for probing, plotting, and the desktop GUI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .control_api import api_request
from .device import C12880Device, enumerate_ports, port_report
from .protocol import DEFAULT_EXPOSURE_MS


def probe(port: str | None, exposure_ms: float) -> int:
    report: dict[str, object] = {"ports": port_report(enumerate_ports())}
    device = C12880Device(port, exposure_ms)
    try:
        descriptor = device.connect()
        report["selected"] = descriptor.to_dict()
        report["controller"] = device.diagnostic_report()
        frame = device.acquire()
        report["frame"] = {
            "valid": True,
            "pixels": int(frame.counts.size),
            "minimum": float(frame.counts.min()),
            "maximum": float(frame.counts.max()),
            "prefix_words": frame.prefix_words,
            "raw_bytes": frame.raw_size,
            "exposure_ms": frame.exposure_ms,
        }
        result = 0
    except Exception as exc:
        report["frame"] = {
            "valid": False,
            "error": f"{type(exc).__name__}: {exc}",
            "raw_bytes": len(device.last_raw),
            "raw_nonzero": sum(bool(value) for value in device.last_raw),
            "raw_head_hex": device.last_raw[:64].hex(" "),
        }
        result = 2
    finally:
        device.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return result


def control(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Control a running Spectrum Studio")
    parser.add_argument("--url", default="http://127.0.0.1:8766")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    exposure = commands.add_parser("exposure")
    exposure.add_argument("value", type=float)
    exposure.add_argument("unit", choices=("us", "ms"), nargs="?", default="us")
    exposure_auto = commands.add_parser("exposure-auto")
    exposure_auto.add_argument("state", choices=("on", "off"))
    commands.add_parser("exposure-meter")
    y_auto = commands.add_parser("y-auto")
    y_auto.add_argument("state", choices=("on", "off"))
    commands.add_parser("y-fit")
    y_limits = commands.add_parser("y-limits")
    y_limits.add_argument("minimum", type=float)
    y_limits.add_argument("maximum", type=float)
    smoothing = commands.add_parser("smoothing")
    smoothing.add_argument("mode", choices=("raw", "fast", "smooth"))
    args = parser.parse_args(argv)
    if args.command == "status":
        response = api_request(args.url, "/api/v1/status")
    elif args.command == "exposure":
        response = api_request(
            args.url, "/api/v1/exposure", {"value": args.value, "unit": args.unit}
        )
    elif args.command == "exposure-auto":
        response = api_request(
            args.url, "/api/v1/exposure/auto", {"enabled": args.state == "on"}
        )
    elif args.command == "exposure-meter":
        response = api_request(args.url, "/api/v1/exposure/meter", {})
    elif args.command == "y-auto":
        response = api_request(
            args.url, "/api/v1/y-scale/auto", {"enabled": args.state == "on"}
        )
    elif args.command == "y-fit":
        response = api_request(args.url, "/api/v1/y-scale/fit", {})
    elif args.command == "y-limits":
        response = api_request(
            args.url,
            "/api/v1/y-scale/limits",
            {"minimum": args.minimum, "maximum": args.maximum},
        )
    else:
        response = api_request(
            args.url, "/api/v1/smoothing", {"mode": args.mode}
        )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0 if response.get("ok") else 2


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "ctl":
        return control(argv[1:])
    parser = argparse.ArgumentParser(description="C12880MA Spectrum Studio")
    parser.add_argument("--port", help="Explicit serial port, for example COM5")
    parser.add_argument(
        "--exposure-ms", type=float, default=DEFAULT_EXPOSURE_MS,
        help=f"Integration time in milliseconds (default: {DEFAULT_EXPOSURE_MS:g})",
    )
    parser.add_argument("--probe", action="store_true", help="Probe once and print JSON")
    parser.add_argument("--demo", action="store_true", help="Show only the vendor reference")
    parser.add_argument("--plot-example", metavar="PNG", help="Export the vendor reference plot")
    parser.add_argument("--api-host", default="127.0.0.1", help="Control API bind host")
    parser.add_argument("--api-port", type=int, default=8766, help="Control API port")
    args = parser.parse_args(argv)
    if args.probe:
        return probe(args.port, args.exposure_ms)
    if args.plot_example:
        from .plotting import export_vendor_sample
        path = export_vendor_sample(Path(args.plot_example))
        print(path.resolve())
        return 0
    from .gui import run_gui
    return run_gui(
        requested_port=args.port,
        demo_only=args.demo,
        api_host=args.api_host,
        api_port=args.api_port,
    )


if __name__ == "__main__":
    sys.exit(main())
