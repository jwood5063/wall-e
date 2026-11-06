# ESP32 arm test

Bench test for the Pavv 6DOF robot arm kit (6 standard PWM servos + claw)
driven directly by the spare ESP32-S3-WROOM — no separate controller board.

- `pavv-arm-esp32s3-test/pavv-arm-esp32s3-test.ino` — Arduino sketch:
  staggered attach/centre at boot, one-at-a-time sweeps (`sweepall`),
  per-servo selection/nudge/move over serial, and min/max/trim calibration
  saved to flash (NVS). Requires the **ESP32Servo** library.
- Servo power is a separate ~6 V high-current rail with a common ground —
  never the ESP32 board. Details are in the sketch header.

Context: this arm is an exploration (bought used, arriving 2026-11-08) to
test whether a centre-deck arm can replace the separate head pan/tilt kit
and provide manipulation. It is **not** plan of record unless the bench
tests (especially holding a ~0.6 kg dummy load at working distance without
shoulder/base sag) pass.
