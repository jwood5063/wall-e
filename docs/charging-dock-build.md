# Wall-E Charging Dock — Build & Wiring Guide

_Companion page to the Wall-E robot plan. The design decisions live in the plan's "Dock and charging (decided 2026-11-03)" section; this page is the how-to: parts, mechanical build, wiring, and the test sequence. Status: design only — parts chosen, not ordered; the dock itself is a Phase 2 (navigation) build._

## How it works, in one paragraph

The charger lives in the dock, not on the robot. The dock holds a 12.6V CC/CV supply whose output reaches a 4-pin magnetic pogo connector on the dock's back plate. The robot drives in (Nav2 to the neighborhood, AprilTag for the precise final approach, magnet snap for the last centimeter), its mating connector half meets the dock half, and 12.6V flows through the Pico sequencer's charge relay into the 12V pack. The sequencer measures the charge current — current flowing is the physical proof of docking, and it fires the Home Assistant "I'm home" event and enables dock sentry mode (5V rail held, motor rail off).

## Bill of materials

| Part | Role | Price / source | Status |
|---|---|---|---|
| Adafruit DIY Magnetic Connector — Right Angle Four Contact Pins (#5358) | Dock + robot contact pair | $6.50, Adafruit | Chosen, not ordered |
| SparkFun Constant Current Power Supply — 12.6V 10A (COM-18335) | Dock charger (3S Li-ion, CC/CV) | $43.50, SparkFun | Chosen, not ordered |
| DC wall supply, 24V / ≥3A, barrel or screw terminals | Feeds the SparkFun board (it takes 8–36V DC in; it is a board, not a wall wart) | ~$15 generic | To source with the Phase 2 buy |
| Adafruit INA219 breakout (#904) — optional | Precise charge-current sensing on I2C, if the Pico ADC read-back isn't clean enough | $9.95, Adafruit | Optional |
| Inline fuse holders + fuses, 3A | One in the dock output line, one on the robot charge input | ~$5 | Consumable |
| 18 AWG silicone wire, red/black | Charge path both sides (short runs, ~2A class) | On hand / consumable | — |
| Small relay for the charge path | Sequencer-controlled charge enable on the robot (see Wiring) | From the sequencer parts | Already in the power design |
| Dock status LED + 1kΩ resistor | "Dock live" indicator on the dock | Consumable | — |
| AprilTag print (tag36h11 family) | Final-approach target on the dock face | Printed at home | Phase 2 |
| Dock body material | Plywood/MDF offcuts for the mock, printed panels in the shell phase | — | Mock first |

Not needed: any dock-side intelligence. The dock is power and geometry only; every decision happens on the robot, in the sequencer.

## Mechanical build

Dimensions come from the chassis (Hiwonder tank kit, 306 × 230 mm footprint) and the approach diagram page.

1. **Base plate.** Flat plate ~340 mm wide × ~400 mm deep, 6–12 mm plywood/MDF for the mock. No ramp — the robot drives onto a flat plate; bevel or chamfer the leading edge so the tracks don't catch. Rubber feet or a non-slip mat underneath: the dock must not skate when the robot noses in.
2. **Funnel guide rails.** Two rails on the base, angled from a ~300 mm mouth at the front converging to just over the robot's 230 mm track width at the back plate. Height 40–60 mm: high enough to catch the track sides and steer, low enough to clear the body and the TF-Luna. Round the mouth ends. The rails do the coarse alignment; the AprilTag does the fine alignment; the magnets forgive what's left.
3. **Back plate.** Vertical plate at the rear of the base, rigidly braced — it takes the docking push. The magnetic connector's dock half mounts on it, centered on the robot's centerline.
4. **Connector height is set from the robot, not from this page.** Once the chassis exists and the robot-side connector half is mounted (see below), measure its center height off the floor and mount the dock half at exactly that height. Shim the dock mount ±5 mm of adjustment if you can; it's the fiddliest dimension in the build.
5. **AprilTag.** One tag36h11 tag, printed ~120–150 mm square, mounted flat on the back plate above the connector, centered. Print size must be entered in the AprilTag detector config exactly as printed — pose accuracy depends on it. Matte paper or a matte laminate; glare kills detection.
6. **Robot-side connector mount.** Low on the robot, centered. Rear mounting with back-in docking keeps the front TF-Luna and bumper area clear and is the current lean; nose-in is simpler to drive. Either works electrically — the wiring below is identical — but decide before printing the mount, and keep the connector clear of the tracks' travel and the TF-Luna's field if front-mounted.

## Wiring

### Pin assignment (both halves)

The connector has 4 pins. Run the charge current across two pins per side — the product page states no per-pin rating, so no single pin carries the full current.

| Pin | Assignment |
|---|---|
| 1 | +12.6V charge |
| 2 | +12.6V charge (parallel with pin 1) |
| 3 | Ground (parallel with pin 4) |
| 4 | Ground |

The magnetic pair is polarized by its magnet orientation — it only mates one way — but verify polarity with a meter at first assembly anyway (see Tests). Mark + on both halves with a paint pen once verified.

### Dock side

```
24V wall supply ──► SparkFun 12.6V supply (input)
                         │ output, set/verified at 12.6V
                         ├──► 3A fuse ──► connector pins 1+2 (+)
                         └──► connector pins 3+4 (−)
                         └──► LED + 1kΩ across output ("dock live")
```

- Before the connector is wired to anything, power the SparkFun board and measure its output at the connector pins: 12.6V, correct polarity. Only then connect the robot side.
- Set the board's charge current to the pack's rated charge current (≈1.5A class for a 6 Ah TalentCell-style pack — confirm against the actual pack's spec when it's bought; the board can deliver far more than the pack wants).
- Fuse sits in the + line, before the connector. If a robot-side fault shorts the contacts, the dock fuse is what opens.

### Robot side

```
Connector half ──► 3A fuse ──► charge relay (Pico-controlled) ──► 12V pack charge input (+)
Connector half ─────────────────────────────────────────────────► pack ground (−)
```

- The relay is the sequencer's charge enable — the low-current relay role already reserved in the plan's power design. **Part chosen 2026-11-05: Pololu Isolated Solid State Relay/Switch, SPST, 30V, 11A (#5421)** — transistor-based (back-to-back MOSFETs, 10 mΩ), opto-isolated control input (2.7–40 V) driven directly by the Pico's charge_en GPIO; no coil, no flyback, nothing charges unless the sequencer turns it on. Ordered 2026-11-05 with the motor-rail switch (Pololu salesorder 1J604693).
- Keep the charge leads short, twisted together, and strain-relieved at the connector mount; the connector is a mechanical joint and will flex.
- Optional but recommended: a series ideal-diode (P-channel MOSFET) or Schottky diode in the + line as reverse-polarity insurance. Costs a little voltage; saves a pack if anything is ever wired backwards.
- Ground is common with the robot's power ground — the charge path shares the pack's negative with the motor rail, as the sequencer design already assumes.

### Sequencer sensing and docked logic

- The Pico reads the charge path two ways (either is enough; both is better): the existing ADC read-back on the charge line voltage, and charge current — from a small shunt into an ADC channel, or the optional INA219 on I2C if cleaner numbers are wanted.
- **Docked = charge voltage present at the connector AND charge current above threshold (≈100 mA) sustained ~2 s.** That combination can't happen by accident: voltage alone could be a partial touch, current alone can't happen at all.
- On DOCKED: sequencer announces `STATE DOCKED` on serial → Pi forwards it → Home Assistant "I'm home" event fires, sentry mode becomes available (5V rail held, motor rail off). On current dropping to ~0 with the pack full, that's charge-complete, still docked — distinguish "docked, charging" from "docked, full" by current level, and report both states to HA.
- If the relay is open (sequencer hasn't enabled charging) there is no current even when mechanically docked — that's correct behavior, not a fault: the robot decides when to accept charge.

## Build and test sequence

Do these in order; each step is a gate for the next.

1. **Bench the charger alone.** Power the SparkFun board from the 24V supply. Meter the output: 12.6V. Set/confirm the charge current limit for the pack.
2. **Bench the connector pair.** Wire the dock half to the charger output through the fuse, the robot half to a bench load (the pack itself on the bench is fine, supervised). Mate and unmate the magnets a dozen times: check the connection is solid, polarity is right at the robot half every time, and the pair doesn't get warm at charge current.
3. **Build the dock body** (base, rails, back plate) and mount the dock half at the measured robot-connector height. Wire the dock per the diagram; meter at the pins again in place.
4. **Wire the robot side** with the relay held open. Meter the connector half: voltage present only when docked, relay open = no path to the pack.
5. **Sequencer integration test.** Close the relay from the Pico; confirm charge current flows, the Pico's read-back sees it, and the DOCKED logic triggers (2 s sustained). Open the relay; current stops. Pull the robot off the dock mid-charge; current stops, no arcing drama, no fault latched on the power rails (undocking is normal, not a fault).
6. **First supervised docking.** Drive in by hand (teleop), slow. Watch the funnel rails steer, the magnets snap, current start. Repeat from a few approach angles and offsets — the point of the funnel + AprilTag + magnet stack is that sloppy approaches still dock.
7. **Only after all of the above:** unattended charging, and autonomous return-to-dock under Nav2/AprilTag.

## Safety notes

- Li-ion charging is the one place this robot can hurt itself. Fuses on **both** sides of the connector, correct polarity verified twice, charge current matched to the pack, and no unattended charging until charge termination behavior with the actual pack is confirmed (see the plan's caveat on the SparkFun supply).
- The dock output is live whenever the dock is powered (the LED says so). The contacts are small and recessed in the connector, but don't leave the dock powered and exposed around loose metal on the bench.
- If anything in the charge path gets warm at charge current — connector, wire, relay — stop and upsize that element. Warm is the fuse you didn't install.
