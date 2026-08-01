# C12880 Firmware and GUI Validation

Date: 2026-08-01

## Active Board State

The board is currently running the **original vendor firmware** on `COM3`.
Its USB identity is `VID_0483&PID_5740\356038593333`. The final GUI test
received 156 valid 288-pixel frames, zero invalid frames, and approximately
342.9 acquisition FPS at 560.113 us auto exposure. The displayed wavelength
axis is nominal (340--850 nm), detector values are relative counts, and the
result is not radiometrically calibrated.

Three independent 2 MiB SWD reads matched this SHA-256:

```text
67F1F6C421D56C2077D5A3F7417AA6F5213A2791D0C63AE5DAFBDBDF461764B4
```

The binaries and verified archive remain under `firmware/private/`, which is
ignored by Git. They must never be published.

## Performance Comparison

The original firmware was measured before flashing:

| Exposure | Raw request/response FPS | Mean spectral span | Mean peak |
|---:|---:|---:|---:|
| 10 us | 881.57 | 3,153.63 | 4,577.78 |
| 100 us | 754.80 | 5,522.26 | 6,946.44 |
| 1,000 us | 244.87 | 60,233.74 | 61,669.22 |

The optical V2 image built successfully with SHA-256
`403E60B1599BC1F4661BE3BCBBC8A57BB59A1E213A4557521774CF83325A7643`.
It booted on `COM4` and answered CRC-protected `HELLO`, capabilities,
configuration, start, and stop commands as firmware 0.4. However, it emitted
no valid spectrum frames and did not pass repeated-open testing. Its usable
measurement FPS is therefore **zero**. It is experimental and must not replace
the vendor firmware until capture and reconnect tests pass.

## GUI Changes

- `C12880Device` preserves the vendor implementation and adds automatic
  legacy/V2 selection.
- A failed serial read closes the stale handle and retries with bounded
  0.2--2.0 second backoff instead of accumulating invalid frames forever.
- The GUI now reports `LINK READY`, `LIVE`, `RECONNECTING`, or
  `DEVICE OFFLINE` instead of `FRAME FAULT`.
- Desktop and web views use plain-language sensor-disconnection messages.
- V2 parsing validates command, reply, and frame CRCs before publishing data.

## Safe Flashing and Recovery

Use `scripts/flash_c12880_firmware_guarded.ps1`. It requires an explicit flash
authorization flag, reads all 2 MiB before programming, checks the expected
current hash, verifies the new image, and attempts vendor recovery if
programming fails. Do not flash an experimental build without ST-Link attached
and a separately verified vendor recovery image.
