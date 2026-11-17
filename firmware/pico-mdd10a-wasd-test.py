# pico-mdd10a-wasd-test.py
# MicroPython bench test for the Cytron MDD10A, driven by the Pico over USB serial.
#
# Keys (in the serial terminal / REPL):
#   w = both motors forward      s = both motors reverse
#   a = pivot left  (L rev, R fwd)   d = pivot right (L fwd, R rev)
#   x or SPACE = stop
#   + / - = speed up / slow down (10% steps, applies to the next command)
#   h = help
#
# Wiring (Pico carrier J2 assignment, verified 2026-11-05):
#   PWM_L = GP12, DIR_L = GP2, PWM_R = GP13, DIR_R = GP3, common GND.
# Sign-magnitude drive per the MDD10A truth table: DIR low = forward
# (output A high), DIR high = reverse; speed = PWM duty. PWM at 20 kHz,
# the MDD10A's rated maximum. Duty ramps so the motors (or the meter, in
# the unloaded test) never see a step change.
#
# Note: with a straight cable to the MDD10A today, these "left" signals land
# on the driver's channel 2 and "right" on channel 1 (the board's input order
# is PWM2/DIR2 before PWM1/DIR1). Irrelevant for this test; the carrier J2
# re-pin to match is a recorded relayout to-do (2026-11-16).

import sys
import select
import time
from machine import Pin, PWM

PWM_FREQ = 20000
RAMP_STEP = 0.05          # duty change per tick (~0.4 s from stop to full)
TICK_MS = 20

pwm_l = PWM(Pin(12))
pwm_l.freq(PWM_FREQ)
dir_l = Pin(2, Pin.OUT, value=0)
pwm_r = PWM(Pin(13))
pwm_r.freq(PWM_FREQ)
dir_r = Pin(3, Pin.OUT, value=0)


def drive(pwm, dir_pin, value):
    """value: -1.0..1.0, sign = direction, magnitude = duty."""
    dir_pin.value(0 if value >= 0 else 1)
    pwm.duty_u16(int(abs(value) * 65535))


def stop_all():
    drive(pwm_l, dir_l, 0)
    drive(pwm_r, dir_r, 0)


speed = 0.4               # commanded duty for w/a/s/d, adjustable with +/-
cur_l = cur_r = 0.0       # ramped (actual) outputs
tgt_l = tgt_r = 0.0       # commanded targets

COMMANDS = {
    "w": lambda s: (s, s),
    "s": lambda s: (-s, -s),
    "a": lambda s: (-s, s),   # pivot left: left track back, right track forward
    "d": lambda s: (s, -s),   # pivot right
}

HELP = __doc__

print("MDD10A WASD test — PWM_L GP12, DIR_L GP2, PWM_R GP13, DIR_R GP3")
print("w/a/s/d drive, x or space stops, +/- speed, h help. Speed starts at 40%.")

poller = select.poll()
poller.register(sys.stdin, select.POLLIN)
stdin = sys.stdin.buffer if hasattr(sys.stdin, "buffer") else sys.stdin

try:
    while True:
        if poller.poll(0):
            ch = stdin.read(1).decode().lower()
            if ch in COMMANDS:
                tgt_l, tgt_r = COMMANDS[ch](speed)
                print("cmd", ch, "-> L {:+.0f}%  R {:+.0f}%".format(tgt_l * 100, tgt_r * 100))
            elif ch in ("x", " "):
                tgt_l = tgt_r = 0.0
                print("stop")
            elif ch in ("+", "="):
                speed = min(1.0, speed + 0.1)
                print("speed {:.0f}% (applies to next w/a/s/d)".format(speed * 100))
            elif ch == "-":
                speed = max(0.1, speed - 0.1)
                print("speed {:.0f}% (applies to next w/a/s/d)".format(speed * 100))
            elif ch == "h":
                print(HELP)
            # anything else (incl. \r, \n) is ignored

        # Ramp actual outputs toward targets, then apply.
        for name in ("l", "r"):
            cur = cur_l if name == "l" else cur_r
            tgt = tgt_l if name == "l" else tgt_r
            if cur < tgt:
                cur = min(tgt, cur + RAMP_STEP)
            elif cur > tgt:
                cur = max(tgt, cur - RAMP_STEP)
            if name == "l":
                cur_l = cur
            else:
                cur_r = cur
        drive(pwm_l, dir_l, cur_l)
        drive(pwm_r, dir_r, cur_r)

        time.sleep_ms(TICK_MS)
except KeyboardInterrupt:
    pass
finally:
    stop_all()
    pwm_l.deinit()
    pwm_r.deinit()
    print("stopped, PWM off")
