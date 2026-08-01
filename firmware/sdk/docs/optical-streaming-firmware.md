# Optical Streaming Firmware 0.4

## Purpose

`aginti_c12880_optical_streaming_h743` is the conservative high-throughput
candidate for the STM32H743 C12880MA controller. It combines the optical timing
that correlated with the vendor spectrum (`r = 0.9973` over the central 286
bins in the previous offline comparison) with continuous V2 USB streaming.
It does not reuse the optically rejected ADC-at-every-clock DMA path.

## Capture contract

The profile reproduces the recovered acquisition order:

```text
8 pre-clocks
ST high
4 lead clocks + requested exposure clocks
ST low
90 dummy clocks
start ADC1 in continuous 16-bit mode
1 readout clock
repeat 294 times: wait for EOC -> read ADC -> advance one clock
repair vendor line-return tail
```

This distinction is essential. Integration clocks can run at the requested
sensor-clock basis, but ADC readout is conversion-paced. Triggering the 16-bit
ADC once per 5 MHz clock outruns the configured ADC conversion and previously
returned a nearly constant electronic baseline.

Hamamatsu specifies a minimum ST-high period of six clocks, a complete scan
period of at least 381 clocks, and acquisition of the first video value at the
89th TRG edge after ST falls. The recovered board adds its established
controller offsets and captures 294 values for the 288-pixel legacy payload.
Official timing source:
<https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/ssd/c12880ma_c16767ma_kacc1226e.pdf>.

## Throughput architecture

- Four statically allocated, 32-byte-aligned slots absorb USB scheduling jitter.
- Ready slots are transmitted in sequence order, including across sequence wrap.
- Capture and asynchronous USB HS/CDC transfer can overlap.
- V2 frames carry sequence, timestamp, exposure, status, drop count, and CRC-32.
- The legacy 590-byte request/response protocol remains available.
- Calibration EEPROM access remains read-only.
- No allocation occurs in the firmware data path.

The host SDK requests up to 64 KiB per serial read, enlarges the Windows receive
buffer when supported, validates CRC, and counts sequence gaps. Plotting should
remain decoupled from acquisition.

## Validation state

The source profile is not a substitute for an optical A/B test. Before it is
accepted for measurements:

1. Reconfirm the private vendor backup hash.
2. Program only with explicit authorization.
3. Compare dark, broadband, and narrowband sources at equal exposure.
4. Require correct exposure scaling, spectral peak location, and shape.
5. Require zero CRC errors and report all sequence gaps.
6. Restore the vendor image immediately if optical acceptance fails.

Until those checks pass, the hash-verified vendor firmware remains the
scientific reference.
