# Wall-E Voice Client — Pi Parts Spec

Step one of the Wall-E build: a Raspberry Pi voice client — the ears and mouth Wally talks through. Slow build; shell parts will be 3D printed later.

## Already on hand (Jim)
- Raspberry Pi 5 (spare)
- Official 27W USB-C power supply
- microSD card

## To buy

| Part | Role | Price | Source |
|---|---|---|---|
| Seeed Studio ReSpeaker 2-Mics Pi HAT V2.0 | Dual-mic array (ears), onboard audio codec, JST speaker out, user button, RGB LEDs | $12.90 | seeedstudio.com (official store, in stock; also listed ~$15.52 via catalog) |
| Adafruit Mono Enclosed Speaker — 3W 4 Ohm (#3351) | Voice output; JST-PH cable matches the ReSpeaker HAT's speaker connector, enclosed so it drops into a printed mount | $3.95 | adafruit.com, in stock |
| Adafruit I2S 3W Class D Amp Breakout — MAX98357A (#3006) | Optional but recommended: dedicated amp path if driving the speaker from the Pi directly / for cleaner, louder output in the robot body | $5.95 | adafruit.com, in stock |

**Buy total: ~$22.80 + shipping** (HAT + speaker; ~$28.75 with the amp board).

Note: the ReSpeaker HAT can drive the speaker on its own, so the MAX98357A is a flexibility buy — worth it since the head/body layout isn't final and I2S audio routing may change when the chassis arrives.

## Software stack (all free, all local except Wally)
- Raspberry Pi OS Lite (64-bit) on the Pi 5
- ReSpeaker drivers (Seeed voicecard) for the HAT
- **Wake word:** openWakeWord or Porcupine, running locally — "Hey Wally"
- **Speech-to-text:** Whisper (faster-whisper, small/base model runs fine on a Pi 5) or cloud STT for speed
- **Wally:** over the home network — the client sends text, plays back the reply
- **Text-to-speech:** Piper (local, fast, decent voices) as the everyday voice; Wally's cloud voice-note voice as the "real" voice option

## Bench milestones
1. Pi OS up, HAT recognized, record/playback test with the speaker.
2. Wake word → beep → records a sentence → transcript printed.
3. Full loop: wake word → question → Wally answers out loud.
4. Only then: into a printed head/body shell, and on to the chassis phase.

Prices checked 2026-10-22.
