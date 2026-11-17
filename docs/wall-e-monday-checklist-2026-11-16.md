# Wall-E — Ordered bench checklist, Monday Nov 16, 2026

_Sequenced so the battery goes on charge first and everything that doesn't need it
runs while it charges. Times are rough guides, not commitments. Check items off as
you go; record numbers where the sheet asks — measured state over assumed state._

## Step 0 — Arrivals (10 min)

- [ ] TalentCell YB12011000: unbox, confirm it's the 12/9/5V model (yellow DC5525
      9V port is the giveaway), rocker switch ON.
- [ ] **Weigh it** — record for the weight sheet (spec says ~500 g).
- [ ] Put it on its included charger and leave it charging through Steps 1–3.
- [ ] Quick check for the Pololu order (#2815 + SSR #5421, ordered Nov 5) in the
      mail pile — arrival was never confirmed.

## Step 1 — While the battery charges: clear the two oldest items (~45 min)

**1a. MDD10A unloaded bench test** (open since Nov 1; needs only the 12V adapter)
- [ ] Pico GND + PWM/DIR per channel to the driver, 12V adapter to VM, outputs unloaded.
- [ ] Power LED check → per-channel test buttons light the direction LEDs, no code needed.
- [ ] Pico PWM at low duty, DIR low then high; meter across each output tracks
      duty × supply and reverses polarity with DIR.
- Pass = both channels, both directions, LEDs match the meter.

**1b. faster-whisper smoke test** (open since Oct 31; Pi bench, isolated from the wake loop)
- [ ] In the voice venv: record 5 s at 16 kHz, transcribe with
      `WhisperModel("tiny.en", device="cpu", compute_type="int8", cpu_threads=4)`, VAD on.
- Pass = a spoken sentence prints back correctly. Report the output before integrating
  into the wake loop — integration is a separate step, only after this passes.

**1c. Two measurements while things run**
- [ ] Fascia height between the tracks (the 7-inch panel arriving Wednesday needs
      ~110 mm of vertical face — this number decides its mount).
- [ ] Weigh the unweighed: Pi 5 + ReSpeaker HAT, Pico, ESP32-S3, MDD10A, speaker + amp.
      Record all in the weight sheet.

## Step 2 — Pavv arm: rail proof, then sag test (~45 min)

**2a. Prove the 6.8 V servo rail first** (so droop numbers are trustworthy)
- [ ] Adjustable buck module fed from 12V, set to **6.8 V under load**, meter on output.
- [ ] One new servo: voltage at rest / hold / stall. Note the worst dip.
- [ ] Check the new servos' box label while you're at it — 6.8 V rail stands unless
      the box says HV / 5–7.4 V (and the stock MG996Rs cap at 7.2 V regardless).

**2b. Sag test — stock baseline first**
- [ ] Stock MG996Rs, separate servo rail, common ground with the ESP32-S3.
- [ ] ~100 g at full extension, hold pose, tip droop at 0 s / 30 s / 60 s. Record.
- [ ] Repeat at ~250 g. Record.

**2c. Servo swap, then re-run**
- [ ] Shoulder pitch first: centre the new servo (1500 µs) *before* fitting its horn.
- [ ] Re-run 2b at both loads. Then elbow pitch, same procedure, re-run.
- Read: if ~250 g holds acceptably at 60 s with the upgrades, the Gemini-2-on-tip
  layout is viable on this arm class. Big sag even upgraded → RoArm-M2-S path.

## Step 3 — Battery tests (once charged, ~30 min)

- [ ] Tray fit: pack in the tray (39 mm thick was the open question), rocker reachable.
- [ ] Resting voltage off the charger — record.
- [ ] **Combined stall test:** motors stalled + arm holding, all from the pack.
      Watch for protection trip or voltage sag — this settles whether the spec's
      6 A is peak-only (the same page also lists 3 A max continuous).
- [ ] Note how the pack behaves on recovery if it trips (auto-recover or rocker cycle).

## Step 4 — Quick leftovers (any order, ~20 min total)

- [ ] First Xbox pad retest with the Xbox console powered off (cold reconnect is
      the pass mark; pad #2 already works).
- [ ] Encoder voltage check: confirm encoder output level is 3.3 V-safe before it
      ever meets a Pico GPIO. Never 5 V into the Pico.
- [ ] Gemini 2 cable prep: tape a string along the arm, pose through full range,
      note slack consumed at shoulder / elbow / wrist.

## Step 5 — Stretch (only if the day has room)

- [ ] Odometry calibration: taped 1 m line, roll three times, log both encoders per roll.
- [ ] Cardboard dock funnel mock — approach angles against the 300 → 230 mm funnel.

## Record before you stop

- [ ] Droop numbers, rail-dip worst case, pack weight + stall-test result, fascia
      height, and the new part weights — into the weight sheet / plan notes, or
      just send them to Wally and he'll file them.

_Still open after today, by design: final arm direction (waits on Step 2 numbers),
sequencer v2 firmware, carrier redesign re-verification, Phase 2 buys (lidar pair,
Gemini 2, dock parts, thermal probes)._
