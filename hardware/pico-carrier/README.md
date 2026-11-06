# Pico carrier board — "Wall-E Monitor"

Jim's own KiCad design: the carrier for the Raspberry Pi Pico that runs
the power sequencer, thermal monitoring, and motor/encoder control.

- `manager-3.kicad_sch` — the latest schematic revision (2026-11-05).
  The PCB layout is in progress in the same project on Jim's machine;
  only the schematic is in the repo so far.

Verified from the file (these pinouts govern — firmware and cables
follow them):

- **J2 Motor_Driver (5-pin):** 1=GND, 2=PWM_L (GPIO12), 3=DIR_L (GPIO2),
  4=PWM_R (GPIO13), 5=DIR_R (GPIO3)
- **J7 Charge_en / J8 Motor_en (JST PH 4-pin):** 1=GND, 2=+3.3V,
  3=enable signal (GPIO15 charge / GPIO14 motor), 4=NC
- **J4/J5 I2C (JST PH 4-pin):** 1=GND, 2=+3.3V, 3=SDA (GPIO4), 4=SCL (GPIO5)
- **J10/J11 encoders (4-pin, house convention):** 1=GND, 2=+3.3V, 3=A, 4=B
  (ENC_L GPIO8/9, ENC_R GPIO10/11)
- **J14-J19 temperature probes (3-pin):** 1=GND, 2=+3.3V, 3=DQ (GPIO6,
  4.7 kΩ pull-up at the Pico end)
- **J12 VSense (4-pin):** 1=NC, 2=GND, 3=batt_rail, 4=motor_rail
- ADC dividers on board: batt_rail and motor_rail 39K/10K, VSYS 10K/10K,
  100 nF per node. ADC_VREF (pin 35) goes to test point TP2 only — the
  Pico generates its reference on-board; do not tie it to carrier +3.3V.
- Q1 (DMP2035U, SOT-23) OR-ing on the 5V input lets the Pico be
  programmed over USB while installed, with no back-feed.
