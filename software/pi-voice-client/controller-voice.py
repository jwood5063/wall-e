#!/usr/bin/env python3
import os, subprocess, sys, time
import evdev
from evdev import ecodes

WAV = os.path.expanduser("~/wally-audio/controller-connected.wav")
BUTTON = ecodes.BTN_SOUTH  # A button — remap to a non-driving button before teleop

def find_controller():
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        keys = dev.capabilities().get(ecodes.EV_KEY, [])
        if dev.name == "Xbox Wireless Controller" and ecodes.BTN_SOUTH in keys:
            return dev
    return None

dev = None
while dev is None:
    dev = find_controller()
    if dev is None:
        print("Controller not found, retrying in 2s...", flush=True)
        time.sleep(2)

print(f"Listening on {dev.name} ({dev.path})", flush=True)
try:
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY and event.code == BUTTON and event.value == 1:
            subprocess.run(["aplay", "-q", WAV])
except OSError:
    print("Controller disconnected.", flush=True)
    sys.exit(1)
