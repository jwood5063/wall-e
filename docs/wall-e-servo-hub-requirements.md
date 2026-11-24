# Servo Hub Board — Requirements

Third custom PCB (after the power board and the manager/carrier board).
Requirements compiled from the decisions of 2026-11-18; this document
2026-11-19. **Status: not yet designed in KiCad.** §9 and §10 hold the
two things still open — buck placement, and the candidate additions
awaiting Jim's picks.

## 1. Purpose and placement

The ESP32-S3 and the arm's servo connectors get their own board. The arm
pivot postdated the power/carrier two-board split, so servo distribution
and ESP32 power were homeless until this board was decided (2026-11-18
connectivity audit).

- Sits in the low tray near the arm base.
- **Harness to the rest of the robot is exactly two cables:** 6.8 V power
  in, and the EN line from the manager board. Data stays WiFi (ESPHome
  API) — no data harness.
- One common ground with the other boards.

## 2. Locked decisions (Jim, 2026-11-18)

- **ESP32-S3 dev board SOCKETED** in female headers, not soldered —
  pullable for bench work. Its USB-C stays at the board edge, exposed,
  for programming/serial debug (same philosophy as the Pico's USB on the
  carrier).
- **Servo-rail current sense is an INA219 in the same circuit as the
  power board's** (Kelvin shunt + address straps).
- **The EN input comes from the manager (controller) board** — the Pico
  owns servo-rail authority, same as it owns the motor rail.

## 3. Power input and distribution

- **PWR_IN — 2-pin screw terminal: 6.8 V + GND**, fed from the servo
  buck's output. The buck itself is fed from the power board's **J11
  'arm-servo-pwr'** tap (V12-BUS). (Buck placement is the open decision
  in §8 — if it moves on-board, PWR_IN becomes 12 V.)
- Distribution sized to the rail: **6 A continuous / 10 A peak**, wide
  pours / Power-class tracks.
- **470–1000 µF bulk capacitor** at the input against servo-stall dips.
- **Grounding:** logic-regulator return routed to the input terminal
  (star) so servo return currents stay out of the ESP32's ground path.

## 4. Servo channels

Six connectors, **standard 3-pin 2.54 mm (signal, 6.8 V, GND)** — the
servos' JR-style leads plug straight in. (JST PH is 2.00 mm and is not
the servo plug; the board uses 2.54 mm unless Jim directs otherwise.)

| Channel | ESP32 pin | Joint |
|---|---|---|
| 1 | GP4 | Base yaw |
| 2 | GP5 | Shoulder pitch |
| 3 | GP6 | Elbow pitch |
| 4 | GP7 | Wrist pitch |
| 5 | GP15 | Wrist roll |
| 6 | GP16 | Gripper |

(Pin assignments are the bench-verified ESP32 test pins. Note the
2026-11-16 arm-role change: in the final robot the claw comes off and
the tip carries the See3CAM_CU30 inspection camera, so channel 6 is a
spare / future tip actuator unless the gripper returns.)

- **10k pull-downs on all six PWM lines** so the servos can't twitch
  while the ESP32 boots.
- Servo upgrade note: shoulder pitch and elbow pitch are the two
  DS3218/DS3225-class high-torque servos; all six channels share the
  single **6.8 V** rail (final — the new servos' max is 6.8 V, the stock
  MG996Rs' max is 7.2 V).

## 5. ESP32 logic power

- Its **own regulator on this board: AP63205WU** (the sequencer rail's
  part — fixed 5.0 V, 2 A, wide input range) off the 6.8 V input,
  feeding the dev board's 5 V pin.
- The ESP32 is never powered from the servo side of the rail, so a
  stalled servo can't brown it out.

## 6. Current sense

- Bare **INA219BxD** + **4-terminal Kelvin 0.1 Ω shunt** in the PWR_IN
  path, 100 nF bypass, fit-one-of-two address strap pairs — the same
  circuit as the power board's charge sense.
- Sits on the **ESP32's own I2C bus**, so it doesn't clash with the
  power board's INA219; default address **0x40**.
- Purpose: stall/load detection. ESPHome reports servo current to the
  Pi/HA; a stalled joint shows as a current plateau.
- (If the buck is designed in per §9, revisit: put the shunt on the
  6.8 V output side so it measures true servo current, not buck input.)

## 7. Enable input

- **EN — 2-pin header, 3.3 V logic, pulled down** (rail off by
  default), driven from a spare Pico GPIO off the manager board's
  **J7 'spare IO'** header (GPIO16/19/20/21/22 are free there — pick
  one and record it here).
- The Pico's thermal/fault policy can kill the arm with the motor rail.
- A **bypass jumper** beside the header allows always-on for bench work.

## 8. Other IO

- **I2C expansion header** — 1 GND, 2 +3.3 V, 3 SDA, 4 SCL (the
  manager board's convention; suggested ESP32 pins GP8/GP9) for future
  arm sensors. The INA219 shares this bus.
- **UART debug header** (TX/RX/GND).
- **Rail status LED.**

## 9. Open decision — where the buck lives

Current spec: the 6.8 V buck is a **separate wired module between the
power board (J11) and this board**. It can move on-board two ways:

| Option | What changes | Cost |
|---|---|---|
| **A. Off-board module (current spec)** | Nothing — PWR_IN stays 6.8 V | A loose module to mount in the tray; extra wiring. Module stays swappable when the rail gets its proof test |
| **B. Module footprint on this board** | Board carries a chosen buck module | Blocked until a module is picked (no buck part has been chosen yet); honest 6 A modules are chunky and every pinout differs |
| **C. Designed-in buck** | PWR_IN becomes 12 V from power J11; the board makes its own 6.8 V; INA219 moves to the output side (§6) | The hardest circuit on any of the three boards: 6 A cont / 10 A peak needs a real synchronous buck (the AP63205 is a 2 A part), a serious inductor, and ~4 W of heat to shed in an enclosed tray |

Wally's recommendation: **A** — distribution is this board's job, and a
wired module stays replaceable. C is the clean-harness option if Jim
wants the design project. **No buck part has been chosen yet in any
case** — the 6.8 V rail proof test still waits on that pick.

## 10. Candidate additions (proposed 2026-11-19, awaiting Jim's picks)

- **Hardware rail switch under EN** — a high-side MOSFET/load switch on
  the 6.8 V distribution, so EN cuts servo power unconditionally. As
  specced in §7, EN is a logic input the ESP32 firmware honors; a rail
  switch makes the Pico's kill authority physical, matching the motor
  rail.
- **Tip LED driver** — one GPIO, a small MOSFET, and a 2-pin output
  for the arm-tip inspection camera's LED (open item from the
  2026-11-16 arm-role change: a small tip LED for dark rooms). This
  board is the natural home for it.
- **Two spare servo channels** — connectors + pull-downs on free GPIOs,
  for a future head tilt or second gripper. Cheap now, expensive later.
- **Polyfuse on PWR_IN** and **test points** on the rail (6.8 V, GND,
  one PWM).

## 11. Conventions carried over from the other boards

- **M3 mounting holes** — KiCad `MountingHole:MountingHole_3.2mm_M3`,
  hole centres ≥ ~4 mm from the board edge (Jim's convention,
  2026-11-18).
- JLC 2-layer design-rule floors and the Power netclasses, same as the
  power and manager boards (apply when the project is created).
- Record the board's weight in the weight budget once it's fabbed.
