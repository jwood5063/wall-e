# Pi voice client

**Placeholder.** The live scripts run on the robot's Raspberry Pi 5
(hostname `wall-e`); this folder is their home when they're copied off
the Pi.

What runs there today:

- `wake_listen.py` — openWakeWord wake-word loop (*hey_jarvis* stand-in,
  threshold 0.5) that answers "Yes, Jim?" through the locked Wall-E voice
  chain on the speaker. Runs as the systemd user service
  `wake-listen.service`.
- `controller_voice.py` — evdev listener that plays the pre-rendered
  "Controller connected." when the Xbox pad's A button (BTN_SOUTH) is
  pressed. Runs as `controller-voice.service`. (Bench proof only — the
  button gets remapped before real teleop.)
- The voice chain (Piper `en_US-lessac-medium` + the locked ffmpeg
  processing chain) and its tuning record are in Appendix B of
  `docs/wall-e-robot-plan.md`; rendered clips live in `~/wally-audio/` on
  the Pi and are deliberately not in git (see `.gitignore`).

Next up: the faster-whisper speech-to-text smoke test (tiny.en, CPU/int8,
isolated from the wake loop — integrate only after it passes).
