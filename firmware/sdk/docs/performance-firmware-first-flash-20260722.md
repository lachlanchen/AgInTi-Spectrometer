# Performance Firmware Validation Correction

## Corrected decision

Performance firmware `0.3.3` is **transport-valid but optically rejected**.
It programmed and verified, enumerated through the external ULPI PHY, returned
the `c12880` identity and 1,024 correction bytes, and delivered valid 590-byte
packets. These checks did not prove that the ADC payload represented light.

Subsequent optical A/B testing found an almost flat 39k-count trace with only
about 256 counts of span. The original firmware, under the same protocol,
showed strong exposure-dependent spectral structure. Historical `0.3.3` tags
are retained for traceability but must not be interpreted as optical approval.

## Throughput result and the 400 FPS observation

The rejected image nevertheless measured 1,027 fps at 3 us and 1,006 fps at
10 us in a minimal serial loop. The integrated GUI/API path measured about
465 fps because each frame requires a host request, validation, publication,
and API sharing. The graph itself renders at a fixed 30 Hz. Acquisition FPS,
render FPS, and exposure-limited FPS are separate quantities.

With the restored original firmware, measured frame rate falls as integration
time rises: a current-room auto-exposure sweep moved from hundreds of fps at
short exposure toward about 160 fps near 1.5 ms. A brighter input, wider optical
coupling, or lower target exposure is required for both high SNR and high FPS.

## Root causes found

- The direct reconstruction had initially used a 1 MHz clock despite the
  legacy protocol encoding 5,000 integration ticks per millisecond.
- The original ADC runs continuously and is read once per pixel clock; the DMA
  trigger scheme sampled a stable baseline instead.
- The original PLL2 configuration gives ADC1 an approximately 36.05 MHz clock.
- The original firmware replaces buffer words 291-294 with word 284 to hide
  the analog line-return tail. Those edge bins are not independent samples.

Experimental `0.3.4` source records these findings but remains pending a clean
end-to-end optical retest. The target is currently running the hash-verified
private original image.

## Scientific interpretation

The application displays a nominal 340-850 nm axis unless the individual
Hamamatsu test-sheet polynomial is supplied. ADC counts include source power,
optical throughput, detector responsivity, electronics gain, and exposure.
They are not absolute spectral irradiance. Quantitative work requires dark
subtraction and wavelength/radiometric calibration.
