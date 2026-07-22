# Performance Firmware Hardware Validation

## Decision

Performance firmware `0.3.3` is **accepted for this controller**. OpenOCD
programming and byte verification passed, USB enumerated as `0483:5740` on
`COM4`, and the complete legacy host workflow passed. The tested 55,880-byte
BIN has SHA-256:

```text
04CD5791F3FB8466891C01A69E5CE4861DCF48B1CC23E22F3A85454038A94500
```

## Failure analysis and correction

Version `0.3.0` did not enumerate because it treated the STM32H743 HS USB core
as an embedded full-speed PHY on `PB14/PB15`. Read-only analysis of the working
controller showed that this board uses an external ULPI high-speed PHY. Version
`0.3.3` configures the observed ULPI pins on ports A, B, and C, enables both HS
and ULPI clocks, uses high-speed PCD mode, and exposes a stable unique USB serial
descriptor. No external calibration EEPROM write path exists in the firmware.

The direct reconstruction profile then isolated the remaining system layers:
it returned the eight-byte identity, read all 1,024 nonzero correction bytes,
and produced a valid 590-byte, 288-pixel frame. The final performance build
passed the same checks with TIM2/GPIO DMA and ADC DMA enabled.

## Measured capture results

Thirty-frame raw serial runs produced:

| Exposure | Sustained rate |
|---:|---:|
| 3 us | 1027.48 fps |
| 10 us | 1006.22 fps |
| 100 us | 665.08 fps |
| 1 ms | 164.27 fps |
| 10 ms | 19.53 fps |

The SWD diagnostic record reported 172 completed captures and zero failures.
At fixed 10 us, the integrated desktop GUI, REST API, and web application
reported 464.97 fps, 8,796 valid frames, zero invalid frames, 9 ms frame age,
and 288 sequence increments over 500 ms. The web root returned HTTP 200.

These values measure transport and acquisition, not calibrated optical
accuracy. Per-device wavelength coefficients, radiometry, external triggering,
the 5 MHz clock ceiling, and long-duration thermal behavior remain separate
validation tasks.

## Recovery evidence

The private original 2 MiB image remains available locally with SHA-256:

```text
67F1F6C421D56C2077D5A3F7417AA6F5213A2791D0C63AE5DAFBDBDF461764B4
```

It was previously restored and a complete post-restore readback matched this
hash exactly. The public repository contains only this hash, never the binary.
Option bytes and the external calibration EEPROM were not modified.
