# Wall-E bench checklist — return from Disneyland (Mon Nov 16, 2026)

Prepared Fri Nov 13, 2026 (America/Los_Angeles) for the first bench session back.
Jim is at Disneyland through Sun Nov 15; commute check resumes Mon Nov 16.

## 1. Pavv arm — rescoped sag test (decider for arm-tip sensor)
Update Sat Nov 14: Jim ordered higher-torque servos — Amazon order #113-8986300-3716223 (2 items,
$29.45), both delivered Fri Nov 13, left near the front door/porch in Seaside. Jim plans the load
test Sunday Nov 15. Suggested order: run the stock MG996R baseline first (same loads/pose), then
swap shoulder first (centre the new servo before fitting its horn), re-run, then elbow if needed.
Check the new servos' voltage rating on the box before choosing the rail. CORRECTION (2026-11-14):
the DS3218/DS3225 class is rated 4.8–6.8 V, NOT 7.4 V, and the stock MG996Rs top out at 7.2 V —
so do NOT run all servos at 7.4 V (and never a raw 2S LiPo, 8.4 V charged). Single-rail sweet
spot is a regulated 6.8 V: full rated torque from the new servos, inside MG996R spec.
- [ ] Separate high-current servo rail (voltage per the new servos' spec), common ground with ESP32-S3-WROOM; no Pi rail power to servos.
- [ ] Hang ~100 g at full extension, command a hold pose, measure tip droop at 0 s, 30 s, 60 s.
- [ ] Repeat at ~250 g (Gemini 2 is 98 g bare; fitted tip package will be heavier).
- [ ] Record: droop (mm or degrees) per load per time point in the weight sheet notes.
- Pass/fail read: if 250 g holds flat at 60 s, Gemini-2-on-tip is viable on stock MG996Rs (11 kg·cm stall at 6 V).
  If it sags materially, shoulder-first servo upgrade (20–25 kg·cm, ~$30–40 for two, on the regulated 6.8 V rail — check the box first; only an HV part rated 5–7.4 V would take 7.4 V, and the MG996Rs still wouldn't) or RoArm-M2-S path.

## 2. Gemini 2 USB-C cable run (do before head rides the arm)
Research done Fri Nov 13:
- Included cable: USB Type-C to Type-C data + power cable, 1 in the box (Orbbec datasheet packing list; Seeed part list).
- Included length: not specified by manufacturer in the datasheet/retail listings checked.
- Orbbec cable guide: use the included cable; if longer is needed, USB-certified power+data cable, 1–1.5 m recommended.
- Power: DC 5 V, ≥1.5 A (Gemini 2); typical <2.5 W, peak <7 W — host port/hub must cover peaks, not just average.
- Right-angle plug: must be USB 3.x data-rated (USB 3.2 Gen 1 / 5 Gbps class), not charge-only/USB 2.0 — a charge-only
  right-angle lead will carry power but not the depth stream. No specific right-angle lead is verified yet; verify
  data rating on any candidate before buying.
- [ ] Tape a string along the Pavv, pose through full range, measure slack each joint consumes (shoulder, elbow, wrist).
- [ ] Plan: right-angle plug at camera, service loop at shoulder, service loop at elbow, spiral wrap/short chain on segments.
- Note: Jim has not yet decided the Nov 10 arm-tip layout (Gemini 2 only recommended; GS body-fixed; Ring stationary).

## 3. Chassis measurements
- [ ] Measure front fascia height between tracks — 7-inch panel needs ~110 mm vertical face; reevaluate panel size from this number.
- [ ] Odometry calibration: taped 1 m line, roll three times, log both encoders each roll (from Nov 9 daily idea; still open).

## 4. Open bench leftovers
- [ ] First Xbox pad retest with the Xbox powered off (second pad works; first-pad cold reconnect was the open item).
- [ ] Pico carrier redesign around the motors' 6-pin JST connectors — netlist-verified pinouts govern; check before ordering.

## What this does not decide
- Final arm direction still waits on the sag-test numbers (Jim's call, Nov 6: build chassis + Pavv and see how it behaves).
- Gemini 2 purchase/integration timing remains open; GS camera still out of stock per the daily watch.
