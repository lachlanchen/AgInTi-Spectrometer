# Optical Data and Visualization Contract

## What the display means

- **Acquisition FPS** is the rate of validated 590-byte hardware frames.
- **View FPS** is fixed at 30 Hz so plotting does not throttle acquisition.
- **Nominal wavelength** is a linear 340-850 nm axis. It is not the individual
  sensor's polynomial calibration.
- **Detector counts** are relative ADC values, not spectral irradiance.

The API exposes three arrays:

- `raw_counts`: unmodified 16-bit controller samples;
- `processed_counts`: EEPROM response correction and optional dark subtraction,
  with no display smoothing;
- `display_counts`: the optional display-only filter output.

CSV recording remains raw. Scientific metrics use `processed_counts`, not the
smoothed curve.

## Why 400 FPS can coexist with a poor-looking trace

Short integration raises FPS but reduces photon signal relative to the
electronic offset. In the present room-light test, auto exposure converged near
1.5 ms for a useful detector range, reducing acquisition toward roughly
160 fps. At shorter exposure the board can exceed 400 fps, but the trace may be
dominated by baseline noise. This is a photon/throughput tradeoff, not a GUI
refresh defect.

## Calibration workflow

1. Block the input and capture a dark reference at the same exposure.
2. Reopen the input and enable auto exposure or meter once.
3. Keep raw smoothing for quantitative inspection; use display smoothing only
   for presentation.
4. Install the per-device wavelength polynomial from the Hamamatsu test sheet.
5. Measure a calibrated lamp if radiometric units are required.

The original controller copies its final three displayed edge bins from a
stable earlier bin to suppress line-return artifacts. Do not interpret those
three bins as independent near-infrared measurements.
