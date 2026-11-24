# Wall-E — Power Control PCB notes

Started 2026-11-14 (Jim): a small dedicated power-control PCB that hooks up to the Pico
sequencer, the batteries, and the charger, with adjustable regulators on board.
Separate from the Pico carrier (manager) board — carrier does logic/motors/sensing,
this board does power distribution and regulation.

## Requirements (consolidated 2026-11-14)

### Interfaces and connectors — part numbers as known

| Interface | Connector / part | Notes |
|---|---|---|
| 12V battery in/out | **DC5521 barrel (5.5 × 2.1 mm), centre positive** — the TalentCell YB12011000's native port | Pack output 12V (12.6–9 V range) / 6A max; the same port style takes its 12.6V charge input. Board side: panel/chassis DC5521 jack or a cut DC5521 lead into screw terminals — decide at layout; strain-relieve it, it's the main power entry. |
| Battery hard disconnect | Part TBD | Sequencer design requires one physical hard disconnect in the battery/motor line (the Pololu switch is explicitly not an e-stop). This board is its natural home. |
| Motor rail out | Via **Pololu Big MOSFET Slide Switch HP, #2815** — its included **5 mm terminal blocks** for VIN/VOUT | Raw battery voltage to the MDD10A's own screw terminals. Board provides the battery-side feed and the sense tap; the #2815 may live on or off this PCB (mounting TBD). |
| Charge path in | Robot half of **Adafruit DIY Magnetic Connector, #5358** (right-angle four-contact) | Pins **1+2 = +12.6V (paralleled), 3+4 = ground**. No per-pin rating is published — never run charge current on a single pin. Dock half + charger live in the dock. |
| Dock charger (off-board, feeds this board) | **SparkFun Constant Current Power Supply 12.6V 10A, PRT-18722**, fed by a 24V / ≥3A DC supply | Charge-current setpoint moves to the **~2A class** for the 11 Ah pack (was ~1.5A class for 6 Ah); termination behaviour with the actual pack must be confirmed before unattended charging (dock build page gates). |
| Charge enable | **Pololu Isolated Solid State Relay/Switch SPST 30V/11A, #5421** | Wired 3-wire: VIN ← +3.3V permanently, GND common, EN ← Pico GPIO15. Low/floating = open (boot-safe). |
| Sequencer control in (enables) | **JST PH 4-pin**, matching the carrier's verified house convention (carrier J7/J8) | Pinout: **1 = GND, 2 = +3.3V, 3 = enable signal, 4 = NC**; shell tabs to GND. J8 carries motor_en (GPIO14 → #2815 ON pin), J7 carries charge_en (GPIO15 → #5421 EN). Any new regulator EN lines on this board should follow the same 4-pin convention so cables are interchangeable. |
| Sequencer sensing out | Sense taps compatible with the carrier's VSense inputs (carrier dividers: 39K/10K on 12V-class rails, 10K/10K on VSYS) | One tap per rail, taken **after** its switch/regulator. Coordinate with the carrier so no rail gets two dividers or none; batt_rail and motor_rail taps already exist in the carrier design — this board adds servo rail (and 5V accessory, if it lands here). |
| Servo power out | **Standard 3-pin servo headers (2.54 mm, JR/Futaba pattern) × 6** | This board supplies the 6.8V rail + ground on the power pins. Servo **signals do not originate here** — they come from the ESP32-S3 hub; keep signal routing off the power board, only power/ground distribute from it. |
| 5V accessory out | USB-A or screw terminal, TBD at layout | Loads: Ring Indoor Cam Gen 1 (5V, its supplied USB power cable), TF-Luna (5V, its supplied pigtail). ~3A class total. |
| Pi 5V rail | **USB-C PD** — Anker A1695's native interface | Off this board by default (Anker pass-through handles dock top-up). Only lands here if the rail scope decision changes. |
| Temp guard input | DS18B20 probe (Adafruit #381) at the power-distribution point | Lands on a carrier temp connector (carrier J14–J19, 3-pin: 1 = GND, 2 = +3.3V, 3 = DQ/GPIO6). This board just needs a probe mounting point that reads real board/copper temperature. |
| Optional charge-current sense | **Adafruit INA219 breakout, #904** (I2C) | Only if Pico ADC read-back on the charge path isn't clean enough for the DOCKED = voltage + >100 mA for 2 s test. |
| Cross-reference (not on this board) | Motors: 6-pin JST on the carrier, pin order GND, A, B, VCC, M+, M−. MDD10A logic: carrier J2, 5-pin **2510 (KF2510)** — 1 = GND, 2 = PWM_L, 3 = DIR_L, 4 = PWM_R, 5 = DIR_R | Listed so the power board's harness plan doesn't collide with the carrier's. Motor current never crosses either logic board. |

### Electrical requirements

- **Input:** TalentCell YB12011000 (DECIDED 2026-11-14; BOUGHT by Jim 2026-11-15 on
  Amazon, $64.99, delivery expected Mon Nov 16) — 11.1V
  nominal, 12.6–9V over discharge, 6A max output, ~122 Wh, 39 × 80 × 138 mm, ~500 g.
  **Pack switch must be ON for charging** (per the Amazon product details Jim checked
  2026-11-15: switch at the "I" position or it will not charge) — so the pack switch
  stays on permanently in the robot; charge enable is the dock SSR's job, not the pack's.
  Design every input-side part for 6A and for the combined-peak case (~5–7A transient
  at motor stall + arm motion) — see open question 2 for the 3A-continuous caveat on
  the pack's PCM spec and the #2815's 6A continuous rating.
- **Servo rail:** regulated **6.8V**, ~6A continuous / 10A peak design target
  (six servos, ~2.5A stall each, never all stalled at once in practice — fuse below
  the regulator's limit, above realistic peaks).
- **Motor rail:** unregulated raw battery, switched, fused; MDD10A accepts 5–30V.
- **Charge path:** 12.6V in, ~2A class, **3A fuses on both sides** of the magnetic
  connector (dock output and robot input, per the dock build page).
- **Sequencing/faults (from the sequencer design, binding on this board):** rails come
  up battery → Pi rail → heartbeat OK → motor rail; shutdown/fault reverses it. Every
  regulated rail must be killable by the Pico (EN pin). Thermal policy: this board's
  DS18B20 point is a **motor-side guard** — a hot power-distribution reading drops the
  motor rail; battery/charge-connector heat opens the charge path.
- **Docked detection support:** charge line must expose voltage + current to the Pico
  well enough to run DOCKED = voltage present AND >100 mA sustained ~2 s, and to
  distinguish charging vs full by current level.

### Mechanical / layout requirements

- Fits the low tray alongside the batteries (pack footprint above; board outline TBD
  once rail scope settles — rail scope is deliberately undecided, Jim 2026-11-14).
- High-current paths in pours/wide traces, 2 oz copper preferred, screw terminals
  rated for the current; no high current through signal headers.
- Test point per rail + a status LED per rail that mirrors the *measured* state.
- Regulator heat spread on copper/heatsink, kept away from the MCP9808 bay-air sensor.

## Rails — candidate list (Jim to confirm which live on this board)

| Rail | Source | Regulation | Target | Load / sizing notes |
|---|---|---|---|---|
| Servo rail | 12V battery | Adjustable buck | **6.8 V fixed after trim** | DS3218/DS3225-class max 6.8 V; stock MG996R max 7.2 V — 6.8 V is the shared sweet spot (corrected 2026-11-14, NOT 7.4 V). Stall ~2.5 A per servo; size regulator 10 A peak / ~6 A continuous, fuse to suit. **Distribution moved off this board 2026-11-18:** this board's role ends at the J5 VBAT tap feeding the buck; the buck's output lands on the new **servo hub board** (see below), which carries the servo connectors, ESP32, and rail current sense. |
| Motor rail | 12V battery | **None — raw battery** | 9–12.6 V as battery gives | Stays switched by the Pololu Big MOSFET HP #2815 (sequencer GPIO14). Do not regulate: MDD10A takes 5–30 V and motor torque wants raw voltage. |
| 5V accessory rail | 12V battery | AP63205WU fixed 5 V (U5) | 5.0 V | **LANDED on this board (decided 2026-11-18):** net V5-ACC, fused F6 2 A; Ring Indoor Cam via J13 screw terminal, TF-Luna via J14 JST PH (power only). Always-on by default (Ring dock sentry); power_en pin 5 becomes acc_en for Pico gating. |
| Pi 5V rail | 12V battery via this board | Witty Pi 5 HAT+ on each Pi (its own DC/DC) | 5 V / 5 A at the Pi | **DECIDED 2026-11-18 (supersedes the Anker scheme):** this board feeds both hats' VIN (6–30 V) from V12-BUS via fused screw terminals **J11 (F4 3 A) / J12 (F5 3 A)**. The Anker is retired from the robot (travel duty) and the PD top-up branch is reverted. The Pico toggles each hat's SWITCH via carrier 2N7002s (J21/J22); hats run schedule = WAIT. Detail: `wall-e-witty-pi-integration-checklist.md`. |
| Charge path | Dock charger (12.6 V supply) | None | 12.6 V in | Via Pololu Isolated SSR #5421 (sequencer GPIO15), fused both sides per dock page. This board is the natural home for the charger-side connector/fuse. |
| 3.3 V / sensors | — | Fixed regulator | 3.3 V | Low current; may stay on the carrier instead. Decide once, don't duplicate silently. |

## Servo hub board — third board (decided 2026-11-18)

The servo distribution and the ESP32-S3 live on their own board now (Jim's call,
2026-11-18 — the arm postdated the power/carrier split). What it means for THIS
board: the servo rail's only footprint here is the **J5 VBAT tap** to the buck.
The hub board itself: ESP32-S3 dev board **socketed**; single 6.8 V screw-terminal
input (6 A cont / 10 A peak, bulk cap at input); 6× 3-pin servo connectors with
signal + power together; ESP32 logic from its **own AP63205WU 5 V regulator** off
the rail input (never from the servo side); **INA219 servo current sense in the
same circuit as this board's INA219s** (Kelvin shunt + straps, on the ESP32's I2C
bus, 0x40); **EN input from the controller board** (Pico spare GPIO, pulled down —
the Pico owns servo-rail authority; the enable-authority open question is closed).
Full IO spec in the build plan's "Servo hub board" section.

## Design rules carried over from the carrier work

- **Enable pins, not always-on:** pick buck regulators/modules with an EN pin so the Pico
  sequencer can switch each regulated rail in sequence, same pattern as GPIO14/GPIO15
  for motor/charge. A regulator the sequencer can't kill is a fault-path hole.
- **Sense after the regulator:** each rail gets a voltage tap for Pico ADC read-back
  (measured state beats assumed state), divider scaled for that rail's max, plus a test point.
- **High current = pours, not traces:** servo rail output in copper pours / wide traces
  (same lesson as the carrier M+/M− rule), 2 oz copper if the fab allows, screw terminals
  rated for the current — no servo current through signal headers.
- **Trim pots:** multi-turn cermet; set the voltage *under load*, measure at the output
  terminals, then lock/mark the pot. Vibration + a single-turn pot = a rail that drifts.
  Once a rail's voltage is final (6.8 V servo), consider replacing the divider with fixed
  resistors in a later rev.
- **Protection per input/rail:** main fuse on battery in, per-rail fuse or polyfuse,
  reverse-polarity protection on battery and charger inputs (they will be plugged in
  tired, in the dark, eventually).
- **Thermal:** buck regulators at servo-rail currents need copper area / heatsinking and
  airflow thought; keep regulator heat away from the MCP9808 bay-air sensor or its
  readings become fiction. The DS18B20 "power-distribution area" probe from the thermal
  plan belongs on/near this board.
- **Grounding:** one common ground with sequencer/carrier/ESP32 hub, star back to the
  battery negative; no servo or motor current through logic ground paths.

## Open questions / risks

1. **Which rails are actually on this board?** Deliberately undecided (Jim, 2026-11-14 —
   "lets see where it all lands"). Keep all candidate rails in these notes until the
   build settles; decide at layout time.
2. **Battery current budget — REEVALUATED 2026-11-14 (Jim asked):** the original pick,
   TalentCell YB1206000, caps its 12V output at 3 A. Load math now: drive motors ~0.65 A
   rated each, ~2.4 A stall each (pair ~4.8 A transient); servo rail through the buck
   adds ~1–2 A at the 12V side when the arm moves/holds. Realistic combined peaks
   ~5–7 A — over the 3 A cap (protection trip / sag risk). Leading successor:
   **TalentCell YB12011000** — same family, same DC5521 connector, same 12.6 V charging
   (dock design untouched), internal PCM protection, 12V/6A max output, 11000 mAh
   (~122 Wh vs 66.6 Wh), ~500 g (+120 g vs 380 g; weight headroom covers it).
   Rejected: raw 3S LiPo (5000 mAh, ~355 g, current to spare) — no protection/BMS,
   needs balance charging, breaks the dock's simple 12.6 V CC/CV + unattended-charge
   safety model for *less* capacity. DECIDED (Jim, 2026-11-14): YB12011000, via the
   documented eBay listing at $104.35 (item 389832765568, 30-day returns); Jim buys
   Sun Nov 15. (The $35.50 eBay outlier was passed over — below even the 6000's
   price, no returns.)
   Verification 2026-11-14 (Wally, specs checked, price NOT verified): YB12011000-USB
   (ASIN B016BJCRUO) — 12V output DC5521 12V (12.6–9 V) / 6A max, 11000 mAh,
   122 Wh, 500 g, 39×80×138 mm (vs YB1206000 28×85×145 mm, 380 g — footprint
   slightly smaller, 11 mm thicker), input 12.6 V / 2 A per YABO spec, 5V/2A +
   9V/1A outputs, Li-ion with PCM. Live Amazon price/stock could NOT be verified
   2026-11-14 ~14:29 PT — Amazon refused the AI-agent check; catalog search also
   returned no YB12011000 listing (only the 6000 mAh at $39.99). Historical $65
   figure (2018 forum) is stale — do not quote as current. Two caveats the
   6A headline does not settle: (a) YABO's own spec table lists "Max continuous
   charge/discharge current 3A (adjustable)" alongside "12V / 6A Max" — unclear
   whether 6A is peak or continuous; if continuous is 3A, sustained >3A draw
   could still trip. Clarify with TalentCell/manual before ordering.
   RE-VERIFIED 2026-11-14 ~17:45 PT (Wally, YABO spec page): both figures
   still stand as listed — 12V / 6A Max and max continuous 3A (adjustable).
   Jim was NOT told this caveat before approving the $104.35 buy on Nov 14,
   so flag it before Sunday's purchase; it does not change the pick (still
   double the peak headroom and capacity of the 6000, same dock), but expect
   6A to be peak-only and stall-test motors + arm together after it arrives.
   (b) The
   Pololu Big MOSFET HP #2815 is rated 6A continuous at 12V — with a 6A pack
   the 5–7A combined peaks now sit at/above that rating instead of well inside
   it (the old 3A cap was the margin). Check its peak rating / airflow before
   relying on it at stall. RESOLVED 2026-11-14 ~17:45 PT (Wally, Pololu page
   re-checked): 6A is only the current heating the FETs to 55°C in still air;
   Pololu rates the HP #2815 at 16A continuous at 12V without exceeding 150°C,
   maximum current 90A — 5–7A peaks are well inside it, not a limiter. Dock knock-on: SparkFun 12.6V supply can feed it,
   but the dock charge-current setpoint must move from ~1.5A class (6 Ah) to
   ~2A class for 11 Ah; 3A dock fuses still cover that. Included AC charger is
   1.5A / ~10h per Amazon (YABO: ~5h at 2A in) — dock top-up will be slower
   than the 6 Ah pack; fine overnight, not a fast turnaround.
3. Servo rail enable: sequencer (Pico) or ESP32-S3 hub? Sequencer fits the fault model
   (thermal policy already cuts guarded rails from the Pico), hub is closer to the arm.
   Recommendation: Pico, for one fault authority.
4. Adjustable modules soldered onto the PCB vs converter ICs designed in? Modules
   (XL4016-class etc.) are faster for rev 1; designed-in is smaller/cleaner later.
5. **Pack switch — DECIDED (Jim, 2026-11-15): the rocker just stays ON, and the
   design accounts for it.** Jim floated replacing it with a relay so the Pico
   could switch the pack itself, then settled on leaving it on. Design
   consequences: the pack's DC5521 port is always live; all switching happens
   downstream on this board / the sequencer (motor-rail #2815, charge-path SSR,
   regulator EN pins); the physical hard disconnect downstream is therefore
   load-bearing for safety, since the pack itself is never off in service.
   Bonus: the rocker doubles as a manual master-off for storage, transport, and
   bench work — so the tray layout should keep it reachable. Relay-mod
   constraints (latching type only, Pico fed pre-switch, never bypass the PCM)
   are parked here in case it ever returns; not pursued.
