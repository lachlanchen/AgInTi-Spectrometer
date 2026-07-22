# AgInTi C12880MA Firmware SDK

This directory contains a clean-room STM32H743 firmware and host SDK for the
C12880MA spectrometer controller. It is based on observed interfaces and
read-only hardware analysis; it does not contain the vendor binary or recovered
vendor pseudocode.

## Safety status

Performance firmware `0.3.3` is hardware-validated on the target controller.
The reconstruction image also passed identity, calibration-memory, and frame
tests. The coordinator remains compile-validated only. Before programming a
different controller, preserve all of the following:

- the existing 2 MiB internal-flash image;
- external EEPROM calibration bytes, including `0x0000..0x0fff` and the area
  beginning at `0x1068`;
- option-byte and read-protection register values;
- the MCU UID and a hash manifest of every backup.

The firmware deliberately implements EEPROM reads but no EEPROM writes.

## Versioned firmware set

Three independent source images are maintained:

- `reconstruction_h743/`: vendor-compatible, direct/blocking clean-room rewrite;
- `stm32h7/`: maximum-throughput TIM2/GPIO DMA and ADC DMA implementation;
- `coordinator_h743/`: dual-lamp modulation, telemetry, cooling, LUT, and trigger controller.

The exact 2 MiB vendor read-back remains private and ignored. Its public
SHA-256 is recorded in `BUILD-MANIFEST.json`. Build all three source images
without touching hardware with `./scripts/build_c12880_firmware_suite.ps1`.

> **Hardware result (2026-07-22):** version `0.3.0` failed because it assumed
> the embedded full-speed PHY. Version `0.3.3` configures the board's external
> ULPI PHY and passed USB, identity, EEPROM, DMA-frame, GUI, API, and web tests.
> The original firmware was also restored and matched by a full 2 MiB readback.
> See
> `HARDWARE-VALIDATION.json` and
> `docs/performance-firmware-first-flash-20260722.md`.

## Recovered board contract

| Function | STM32H743 signal |
|---|---|
| C12880MA `ST` | `PE2` |
| C12880MA `CLK` | `PE3` |
| Analog video | `PA0 / ADC1_INP16` |
| External trigger | `PE9 / EXTI9_5` |
| Output/mode bits | `PE13`, `PE14` |
| Calibration EEPROM | software I2C on `PB6/PB7`, address `0xA0` |
| USB device | `USB_OTG_HS` with external ULPI PHY: `PA3/PA5`, `PB0/PB1/PB5/PB10-PB13`, `PC0/PC2/PC3` |

## Design

- Hardware-timed clock edges via TIM2 requests and DMA writes to `GPIOE_BSRR`.
- ADC1 external triggering plus DMA into non-cacheable D2 SRAM.
- Two frame slots so USB transmission can overlap the next acquisition.
- Legacy 590-byte frames for existing software and a framed V2 stream with
  sequence, timestamp, exposure, status, drop count, and CRC-32.
- A slower `DIRECT` backend for timing comparison and fault isolation.
- No dynamic allocation in the application data path.
- Safe outputs and a non-returning panic path.

The performance target defaults to 1 MHz and exposes 100 kHz to 5 MHz. The
upper endpoint uses the shortest ADC sample window and represents a compile-
validated hardware ceiling candidate, not a measured guarantee. The
reconstruction uses the observed 5 MHz integration-tick basis with the direct
capture path.

## Fetch and build

From the repository root in PowerShell:

```powershell
./scripts/fetch_c12880_firmware_deps.ps1
./scripts/build_c12880_firmware.ps1 -Engine DMA -Configuration Release
```

Build products are written to `firmware/sdk/build-dma/`:

- `aginti_c12880_h743.elf`
- `aginti_c12880_h743.bin`
- `aginti_c12880_h743.hex`
- `aginti_c12880_h743.map`

The scripts contain no OpenOCD, ST-Link, erase, or program command.

For the reference backend:

```powershell
./scripts/build_c12880_firmware.ps1 -Engine DIRECT -Configuration Release
```

## Host SDK

```powershell
python -m pip install -e firmware/sdk/python
aginti-c12880 --port COM7 identity
aginti-c12880 --port COM7 stream --exposure-us 1000 --clock-hz 1000000
```

V2 continuous streaming avoids one host request per frame. The compatibility
mode remains available for the existing 590-byte request-response protocol.

## Dual-H7 synchronized controller

`coordinator_h743/` is a second, independent firmware target for the Geek
STM32H743IIT6 board. It keeps the spectrometer MCU dedicated to acquisition
while the coordinator owns dual-lamp PWM, slow optical/electrical telemetry,
cooling protection, LUT execution, and the acquisition trigger.

```powershell
./scripts/build_dual_h7_coordinator.ps1
python firmware/sdk/tools/coordinator_cli.py --port COM7 status
```

The coordinator is also compile-validated only. The build script never calls
OpenOCD and never programs either board. Wiring, commands, timing limits, and
the calibration workflow are documented in `docs/dual-h7-control.md`.

## Current validation boundary

On-device testing establishes USB enumeration, identity, read-only EEPROM
access, 288-pixel DMA capture, legacy framing, and host integration from 3 us
through 10 ms. It does not establish absolute radiometric accuracy, per-device
wavelength calibration, the advertised 5 MHz ceiling, external triggering, or
long-duration thermal stability. Those checks remain in `docs/architecture.md`
and the Chinese monograph under `publications/c12880_firmware_sdk/`.
