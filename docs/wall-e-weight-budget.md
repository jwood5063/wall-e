# Wall-E weight budget — 5 kg chassis rating

Created 2026-11-05 from the locked plan (`wall-e-robot-plan.md`) and manufacturer specs.
Rule from the plan: weigh parts as they arrive on a kitchen scale — measured beats spec.
Fill the **Measured (g)** column; the sheet totals the measured column when a row has one,
otherwise it falls back to the spec/estimate figure so the running total is never silently low.

## The two ways to read the 5 kg limit — flag this before locking the budget

- Hiwonder specs the chassis as **Weight: 1.2 kg, Maximum load: 5 kg**. A "maximum load"
  normally means payload carried *on top of* the chassis, not total robot weight.
- The plan's build estimate (~4–4.5 kg) has been talked about as if the 5 kg rating is the
  total budget. Those two readings give very different headroom — see the totals below.
- **Do not lock the budget until Jim confirms which reading he wants:** total ≤ 5,000 g,
  or payload (total − 1,200 g chassis) ≤ 5,000 g. The sheet shows both.

## Spec-known parts (from the plan or manufacturer spec)

| Part | Status | Spec / est (g) | Measured (g) | Source / note |
|---|---|---|---|---|
| Hiwonder Tank Car Chassis Kit, encoder variant | Out for delivery 2026-11-06, ETA 2026-11-07 | 1200 | | Hiwonder spec: weight 1.2 kg, max load 5 kg |
| TalentCell 12V 6000 mAh pack (motor rail) | Research pick, not ordered | 380 | | Plan: ~380 g |
| Anker Laptop Power Bank 25K, 165W A1695 (Pi rail) | Research pick, not ordered; sale watch ≤ $105 | 595 | | Anker spec: 21.0 oz (595 g) |
| Slamtec RPLIDAR C1 | Chosen, not ordered | 110 | | Plan: ~110 g sealed puck |
| Benewake TF-Luna | Chosen, not ordered | 5 | | Plan: C1 + TF-Luna ≈ 115 g, so TF-Luna ≈ 5 g |
| Orbbec Gemini 2 depth camera | Planned, not ordered; integration timing open | 98 | | Plan: 98 g, <2.5 W, built-in IMU |
| Ring Indoor Cam, 1st Gen (eye) | On hand | 100 | | Plan: "~100 g class" — estimate, weigh it |
| **Spec-known subtotal** | | **2488** | | |

## To weigh — on hand now (kitchen scale, tonight-sized)

| Part | Status | Spec / est (g) | Measured (g) | Source / note |
|---|---|---|---|---|
| Raspberry Pi 5 (voice/nav) | On hand | — | | Weigh bare board, then with ReSpeaker HAT fitted |
| ReSpeaker 2-Mics Pi HAT V2.0 | On hand, bring-up verified | — | | |
| Raspberry Pi Pico (sequencer) | On hand | — | | |
| Raspberry Pi Pico 2 W | On hand, unassigned utility | — | | Only count if it rides on the robot |
| ESP32-S3-WROOM (head hub) | On hand | — | | |
| Cytron MDD10A motor driver | Delivered 2026-10-31 | — | | |
| Adafruit speaker #3351 + MAX98357A amp | Delivered 2026-10-29; amp fitted 2026-11-05 | — | | Weigh speaker + amp together; count both in the robot total |
| e-con See3CAM_CU30_CHL_TC_BX | On hand | — | | **Bench only — do NOT count in robot total** |
| Xbox Wireless Controller | On hand | — | | Handheld, not onboard — do NOT count |

## To weigh / confirm later — not ordered yet

| Part | Status | Spec / est (g) | Measured (g) | Source / note |
|---|---|---|---|---|
| Raspberry Pi Global Shutter Camera + 6 mm CS lens (eye) | Out of stock; stock watch running | — | | Weigh when it lands; lens is a separate line if weighed separately |
| Hiwonder 2 DoF Pan Tilt Kit (brackets + 2× LD-1501MG) | Picked, not ordered ($83.99) | — | | Head is ~0.5–0.8 kg per plan; kit weight decides servo margin |
| 7-inch chest display + dedicated display Pi | Display Pi: second Pi, kiosk mode | — | | Waveshare 7" panel + Pi + mount; weigh as one assembly |
| Thermal sensors: 6× DS18B20 + MCP9808 + SHT41 | Specified, not ordered | — | | Small; weigh as one bag, then fitted |
| Dock charge connector, robot side (Adafruit magnetic, 4-pin) | Phase 2 buy | — | | |
| Wiring, cables, fasteners, power distribution | — | — | | Weigh the harness as built; this is where estimates usually leak |
| Printed shell / body | Jim's own design, Phase 3 | — | | Weigh the cardboard/foam mockup first, then prints as they land |
| Printed head pods + lidar pedestal | Design locked (portrait pods, tall rear pedestal) | — | | Pods ~250 mm span; pedestal must keep scan plane above head |

## Running totals (spec-known only — everything above marked "—" is still $0 g$ in the total)

- Spec-known onboard parts: **2,488 g**
- Headroom if the limit is **total ≤ 5,000 g**: **2,512 g** left for Pi 5, HAT, Pico, ESP32-S3,
  driver, display + display Pi, pan/tilt kit, GS camera, shell, head, pedestal, wiring, sensors.
- Headroom if the limit is **payload ≤ 5,000 g** (total ≤ 6,200 g): **3,712 g** left for the same list.
- The Anker bank alone is 595 g — the heaviest single add-on after the chassis, and the
  first place to look if the total-weight reading is the one that binds.

## How to use it

1. Weigh each on-hand part tonight and fill Measured (g). A kitchen scale in grams is fine;
   weigh small boards together in a bag and note the bag weight if the scale won't register them alone.
2. When a part arrives, weigh before fitting — fitted weight is what the chassis carries.
3. Re-total after every arrival. If the running total (measured where known, spec otherwise)
   crosses 4,500 g under the total-weight reading, that is the moment to lighten the shell/head
   design, not after the print finishes.
4. Keep the See3CAM and the Xbox controller out of the robot total — bench and handheld only.

## Sources

- Plan: `wall-e-robot-plan.md` in this goal's files (chassis 5 kg rating, battery picks,
  sensor weights, head/display/dock decisions, all as of 2026-11-03/04).
- Chassis weight 1.2 kg / max load 5 kg: Hiwonder Tank Car Chassis spec, via ozrobotics listing.
- Anker A1695 weight 595 g: Anker official spec page, checked 2026-11-05.
- All other spec figures are the plan's own numbers; anything marked "—" has no verified
  spec weight in the plan and must be measured, not guessed.
