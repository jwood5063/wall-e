# faster-whisper-smoke-test.py
# One-shot STT smoke test for the Wall-E voice bench (Pi 5 + ReSpeaker HAT).
# Deliberately isolated from the wake-word loop: run it, read the result,
# integrate only if it passes.
#
# Usage:  python3 faster-whisper-smoke-test.py [audio.wav]
# Expects a 16 kHz mono 16-bit WAV (what the arecord step produces). The WAV
# is decoded with the stdlib and handed to the model as an array, which keeps
# PyAV out of the path entirely — the venv's PyAV build rejects the
# metadata_errors argument faster-whisper passes it (hit 2026-11-16).
#
# Pass = the spoken sentence prints back correctly. Also note the transcribe
# time — on a Pi 5, tiny.en/int8 should come back in a few seconds for a
# 5-second clip. First run downloads the model (~75 MB), one time only.

import sys
import time
import wave

import numpy as np
from faster_whisper import WhisperModel

path = sys.argv[1] if len(sys.argv) > 1 else "test.wav"

with wave.open(path, "rb") as w:
    assert w.getframerate() == 16000, "need 16 kHz audio"
    assert w.getnchannels() == 1, "need mono audio"
    assert w.getsampwidth() == 2, "need 16-bit audio"
    frames = w.readframes(w.getnframes())
audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
print("audio: {:.1f}s".format(len(audio) / 16000))

t0 = time.time()
model = WhisperModel("tiny.en", device="cpu", compute_type="int8", cpu_threads=4)
print("model loaded in {:.1f}s".format(time.time() - t0))

t0 = time.time()
segments, info = model.transcribe(audio, vad_filter=True)
text = "".join(seg.text for seg in segments).strip()
print("transcribed in {:.1f}s".format(time.time() - t0))
print("HEARD:", text)
