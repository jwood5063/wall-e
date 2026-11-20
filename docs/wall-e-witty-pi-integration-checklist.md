# Wall-E — Witty Pi 5 Integration Checklist

_Created 2026-11-18 (Wally) from Jim's decisions of 2026-11-18: a Witty Pi 5 HAT+
on **each** Pi 5 (main + display), both fed from the 12 V bus via new power-board
terminals; two MOSFETs added to the Pico sequencer (carrier board) so the Pico can
toggle each hat's SWITCH line; power connectors added for the TF-Luna and the Ring
camera (which brings the 5 V accessory rail onto the power board)._

Verified hat facts (UUGear Witty Pi 5 manual rev 1.04): MCU is an RP2350; the
unpopulated **P2 extension header** exposes **SWITCH** (RP2350 GPIO3, pulled high,
active low — the onboard button's signal). The manual's prescribed electronic
trigger is an **N-MOSFET pulling SWITCH to GND**, driven by a positive pulse;
one pulse = one button tap = **toggle** (on when off, off when on). Schedule
scripts support **WAIT** in the OFF state, handing wake entirely to the external
trigger. VIN screw terminal (KF350-2P) accepts **6–30 V DC**; the hat delivers
5 V / 5 A to the Pi (Mode 1 Power HAT+). Pi↔hat communication is I2C only.

---

## 0. Decision first — the Anker and the PD branch

Feeding both hats from the 12 V bus unloads the Anker completely. One of these
has to be picked before the power board edit, because it changes the schematic:

- [x] **Option A — DECIDED by Jim 2026-11-18: retire the Anker from the robot.**
  (It stays Jim's travel bank — a good buy regardless.) The TalentCell becomes
  the single energy source. Consequences: the PD top-up branch drawn 2026-11-18
  (F3, R7, U4, K2, U3) comes off the power board; **power_en pin 5 (pd_en) is
  freed** and can be reassigned to `acc_en` to gate the new 5 V accessory rail
  (item 1.4); the Anker (591 g) leaves the weight budget.
- [—] **Option B — rejected.** The Witty Pi 5 has dual inputs (VIN + USB-C) with
  automatic switchover, so the Anker could have stayed as the hats' UPS backup
  with the PD branch keeping it charged — not taken.

Everything below works under either option except items marked **[A]** / **[B]**.

## 1. Power board changes (KiCad `wall-e-power`)

- [ ] **1.1 J11 `PI_MAIN_PWR`** — new 2-pin screw terminal: pin 1 = V12-BUS via
  **F4 (3 A)**, pin 2 = GND. Feeds Witty Pi #1 (main Pi) VIN.
- [ ] **1.2 J12 `PI_DISP_PWR`** — same: pin 1 = V12-BUS via **F5 (3 A)**, pin 2 =
  GND. Feeds Witty Pi #2 (display Pi) VIN. (Display Pi power — audit item (5) —
  is closed by this terminal.)
- [ ] **1.3 U5 — 5 V accessory rail.** Clone the U1 AP63205WU circuit (fixed
  5.0 V, 2 A; C/L values copied from the sequencer rail), input from V12-BUS via
  **F6 (2 A)**, output net **`V5-ACC`**. Loads: Ring (~1 A class with IR on) +
  TF-Luna (~0.2 A peak) — inside the 2 A part with margin. This lands the
  long-candidate accessory rail on this board; audit item (3) closes.
- [ ] **1.4 Accessory rail enable.** Default: EN tied to IN (always-on, like
  Vconst — the Ring's dock sentry mode needs 5 V while the robot sleeps).
  **[A]** If pin 5 is freed, reassign power_en pin 5 to `acc_en` and drive U5's
  EN from it instead; sentry mode then = Pico holds acc_en on at the dock.
- [ ] **1.5 J13 `RING_PWR`** — 2-pin screw terminal: pin 1 = V5-ACC, pin 2 = GND.
  Camera side is a cut micro-USB pigtail (bare ends screw down — no crimping).
- [ ] **1.6 J14 `TFLUNA_PWR`** — JST PH 2-pin (the carrier's house connector):
  pin 1 = V5-ACC, pin 2 = GND. Power only — TF-Luna data stays on its own cable
  to the main Pi (UART/I2C), unchanged.
- [ ] **1.7** Delete the PD branch (F3, R7, U4, K2, U3 + J7 `5v-charge-sense`)
  and rename power_en pin 5 net pd_en → acc_en on J8. (Revert confirmed by Jim
  2026-11-18: one TalentCell powers the system, the Anker charging circuit goes.)
- [ ] **1.8** Re-run ERC; expect clean. Then place/route the new parts and
  re-run DRC (J9/J10 routing from the last edit is also still outstanding).

### New power-board connectors — spec

| Desig. | Label | Type | Pin 1 | Pin 2 | Feeds |
|---|---|---|---|---|---|
| J11 | PI_MAIN_PWR | Screw terminal 2-pin, KF350-3.5 mm class | V12-BUS (F4 3 A) | GND | Witty Pi #1 VIN (KF350-2P on hat) |
| J12 | PI_DISP_PWR | Screw terminal 2-pin, KF350-3.5 mm class | V12-BUS (F5 3 A) | GND | Witty Pi #2 VIN |
| J13 | RING_PWR | Screw terminal 2-pin, KF350-3.5 mm class | V5-ACC | GND | Ring cam via micro-USB pigtail |
| J14 | TFLUNA_PWR | JST PH 2-pin | V5-ACC | GND | TF-Luna 5 V in |

One terminal part number (KF350-2P class) covers J11–J13 and matches the hat's
own VIN terminal — one spare fits all. Harness wire: 20 AWG pair for the Pi
feeds, 22–24 AWG for the accessory pair.

## 2. Carrier / sequencer changes (KiCad `manager`)

- [ ] **2.1 Q2, Q3 — 2N7002 (SOT-23)** open-drain toggles, one per hat: drain →
  connector, source → GND, gate ← Pico GPIO via 100 Ω with a **100 kΩ pull-down**
  (lines must idle OFF through Pico boot/reset — a floating gate here is a
  phantom button press on a Pi).
- [ ] **2.2 GPIOs (proposal, from the J1 spare pool):** GPIO17 → `WITTY_MAIN`
  (Q2), GPIO18 → `WITTY_DISP` (Q3). (GPIO16 is the standing proposal for pd_en /
  acc_en on power_en pin 5 — assign all three in the same edit.)
- [ ] **2.3 J21 `WITTY_MAIN`, J22 `WITTY_DISP`** — JST PH 2-pin each: pin 1 =
  SWITCH (Q drain), pin 2 = GND.
- [ ] **2.4** Fold into the already-pending manager edit (combined 5-pin
  power_en + INA219 sense landing) so the board is verified once, not three times.

### New carrier connectors — spec

| Desig. | Label | Type | Pin 1 | Pin 2 | Other end |
|---|---|---|---|---|---|
| J21 | WITTY_MAIN | JST PH 2-pin | SWITCH (open-drain) | GND | Witty Pi #1 P2: SWITCH + GND |
| J22 | WITTY_DISP | JST PH 2-pin | SWITCH (open-drain) | GND | Witty Pi #2 P2: SWITCH + GND |

Hat side: solder pins at the SWITCH and GND positions of each hat's P2 header
(or the full 7-pin header). Cable: 2-wire twisted pair, any light gauge.

## 3. Witty Pi setup (×2, one per Pi)

- [ ] **3.1** Order 2× Witty Pi 5 HAT+ ($59.95 ea per the 2026-10-28 check).
  Weigh on arrival for the weight sheet.
- [ ] **3.2** Stack: Pi 5 → Witty Pi 5 → (main Pi only) ReSpeaker HAT, using a
  stacking header + standoffs. The hat uses only I2C on the 40-pin header, so
  the ReSpeaker's I2S/I2C pass through; check stack height against tray/deck
  clearance before final mounting.
- [ ] **3.3** Power the Pi **only** through the hat (USB-C on the Pi itself stays
  empty — power direct to the Pi bypasses the hat's control). **[B]** Anker, if
  kept, plugs into the *hat's* USB-C, never the Pi's.
- [ ] **3.4** Install the Witty Pi software on each Pi; enable I2C.
- [ ] **3.5** Set each hat's schedule to **WAIT** in the OFF state (no RTC
  wake/shutdown times at all — the Pico is the only wake authority). Disable any
  temperature/voltage auto-actions that could fight the sequencer; voltage
  monitoring may stay read-only.

## 4. Sequencer firmware changes

- [ ] **4.1 Pulse = tap:** drive the GPIO high ~400 ms (button-tap emulation),
  then low. Never hold the line — a held SWITCH is a held button.
- [ ] **4.2 Toggle discipline:** SWITCH is a *toggle*, not an enable. The Pico
  must only pulse on a wanted transition. Main Pi state is known (heartbeat);
  display Pi state is tracked by command echo (the Pico records what it pulsed)
  — after any Pico reset, assume both Pis' states are *unknown* and reconcile
  before pulsing (main: heartbeat present? display: ask the main Pi over serial
  whether the display topics are live).
- [ ] **4.3 Boot order:** pulse main Pi → wait for heartbeat (existing 60 s boot
  wait) → pulse display Pi → then motor rail per the existing sequence.
- [ ] **4.4 Shutdown:** main Pi via the existing SHUTDOWN serial handshake (its
  Witty Pi cuts power after the OS is down); display Pi is told to shut down by
  the main Pi over Ethernet first, and only pulsed if it must be forced.
  A pulse sent to a *running* Pi starts its shutdown — never pulse blind.

## 5. Verification (bench, before it all goes in the tray)

- [ ] **5.1** One hat on the bench: 12 V bench supply → VIN; Pico (or a button +
  2N7002 on a breadboard) pulses SWITCH → Pi boots. Pulse again → Pi shuts down.
  Confirm WAIT means it then *stays* off indefinitely.
- [ ] **5.2** Confirm the hat holds the Pi fully off (no standby drain surprise)
  and that the Pico's pulse works with the Pico on a *separate* supply sharing
  only ground — that's the in-robot ground arrangement.
- [ ] **5.3 Combined load test (updated):** with both Pis on the 12 V bus, re-run
  the motors + arm stall test watching the pack. The bus now carries motors
  (~4.8 A stall) + servo buck (~1–2 A) + two Pis (~2.3 A each at a full 25 W,
  ~1 A each typical) + accessory (~0.6 A peak). Check F2 (7.5 A) headroom under
  coincident peaks and watch for the pack's 3 A-continuous caveat biting —
  this test now decides whether the single-pack design holds.
- [ ] **5.4 Sentry check:** robot docked, Pis asleep, motors off — Ring still
  powered from V5-ACC and visible in Home Assistant.
- [ ] **5.5** Runtime sanity: combined Pi draw measured ~12 W class → estimate
  TalentCell runtime for the full robot and note it in the plan.

## 6. Doc updates after the hardware lands

- [ ] Plan (Pi-rail section + architecture table), system block diagram (the
  off-board Pi-rail subgraph goes away; hats + toggles + accessory rail drawn),
  power notes, parts checklist (§1 hats, §5 new parts), weight sheet (+2 hats,
  **[A]** −591 g Anker).
