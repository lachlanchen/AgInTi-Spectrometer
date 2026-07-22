# AgInTi C12880MA Firmware SDK

This directory contains a clean-room STM32H743 firmware and host SDK for the
C12880MA spectrometer controller. It is based on observed interfaces and
read-only hardware analysis; it does not contain the vendor binary or recovered
vendor pseudocode.

## Safety status

Performance firmware `0.3.3` is **transport-validated but optically rejected**.
It enumerates and sends structurally valid frames, but its payload measured an
almost flat ADC baseline rather than the incident spectrum. The hash-verified
original firmware is currently restored and is the only optically accepted
image. The `0.3.4` direct reconstruction is experimental; the coordinator
remains compile-validated only. Before programming a different controller,
preserve all of the following:

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

> **Hardware result (2026-07-22):** version `0.3.3` fixed the external ULPI
> transport and reached about 1,027 request/response fps at 3 us, but later
> optical A/B testing rejected its ADC payload. The original firmware was
> restored, matched by a full 2 MiB readback, and recovered exposure-dependent
> spectra. See
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

- Experimental hardware-timed clock edges via TIM2/GPIO DMA and ADC DMA.
- A vendor-timing direct backend using continuous ADC1 conversion for optical
  reconstruction and fault isolation.
- Two frame slots so USB transmission can overlap the next acquisition.
- Legacy 590-byte frames for existing software and a framed V2 stream with
  sequence, timestamp, exposure, status, drop count, and CRC-32.
- A slower `DIRECT` backend for timing comparison and fault isolation.
- No dynamic allocation in the application data path.
- Safe outputs and a non-returning panic path.

The legacy protocol uses 5,000 integration ticks per millisecond. The direct
reconstruction therefore defaults to the observed 5 MHz tick basis. DMA remains
an experimental throughput path until it reproduces the original optical A/B
response, including the controller's copied line-tail bins.

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
access, legacy framing, and transport throughput. Those checks do **not** imply
correct optical sampling. Optical acceptance requires exposure response,
spectral shape agreement with the original firmware, edge-bin checks, and a
dark/reference acquisition. Absolute radiometry, individual wavelength
coefficients, external triggering, and long-duration thermal stability remain
unvalidated.
