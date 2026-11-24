# Cytron motor driver for Raspberry Pi

Python port of [CytronMotorDriver](https://github.com/CytronTechnologies/CytronMotorDriver), using [GPIO Zero](https://gpiozero.readthedocs.io/en/stable/). Supports Python 3.9+ and Raspberry Pi GPIO backends, including lgpio for Pi 5. Hardware operation has not been tested here.

## Install on Raspberry Pi OS

From this directory:

```sh
sudo apt update
sudo apt install python3-gpiozero python3-lgpio python3-venv
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
python -m pip install .
```

Use `GPIOZERO_PIN_FACTORY=lgpio python examples/single_motor.py` to explicitly select lgpio. GPIO Zero determines the GPIO chip; if your OS needs a different chip, pass `pin_factory=LGPIOFactory(chip=N)` to each motor and close that shared factory after closing the motors. Run with a user that has GPIO access.

## Wiring and modes

All pin arguments use **BCM GPIO numbers**, not physical header pin numbers. Use distinct, available GPIOs for each channel. Each instance controls one motor; instantiate twice for a dual driver.

| Mode | pin1 | pin2 | Positive speed | Negative speed | Zero |
| --- | --- | --- | --- | --- | --- |
| `PWM_DIR` | PWM | DIR | PWM = speed / 255, DIR low | PWM = abs(speed) / 255, DIR high | Both low |
| `PWM_PWM` | Forward input A | Reverse input B | A = speed / 255, B low | A low, B = abs(speed) / 255 | Both low |

For the single-motor example, connect BCM18 (header pin 12) to PWM, BCM23 (header pin 16) to DIR, and Pi GND to driver signal GND. Supply the motor through the motor driver's appropriate external supply, not a Pi GPIO. Check your specific driver's voltage requirements and 3.3 V input compatibility before wiring; Pi GPIO is not 5 V tolerant. Smart series drivers require Sign-Magnitude PWM Input mode, as described in the upstream README.

The upstream examples use `PWM_DIR` for drivers such as MD10C, MD13S, MD30C and MDD10A, and `PWM_PWM` for MAKER-DRIVE and MDD3A. Check your board manual and configuration. Stop behavior (brake or coast) depends on the board's input truth table.

## Use

```python
from time import sleep
from cytron_motor_driver import CytronMD, PWM_DIR, PWM_PWM

with CytronMD(PWM_DIR, 18, 23) as motor:
    motor.setSpeed(128)    # forward, about 50% duty
    sleep(2)
    motor.stop()
    sleep(1)
    motor.set_speed(-128) # reverse, Python-style alias
    sleep(2)
# Stops and releases this motor's pins, including on exceptions/Ctrl+C.
```

Run `examples/dual_motor.py` for two PWM/PWM channels. Two PWM/DIR channels work the same way: create two `CytronMD(PWM_DIR, pwm_pin, dir_pin)` instances with four different GPIOs.

## API and behavior

- `CytronMD(mode, pin1, pin2, *, frequency=1000, pin_factory=None)` starts both outputs low. `MODE.PWM_DIR` and `MODE.PWM_PWM` are also exported.
- `setSpeed(speed)` / `set_speed(speed)` takes an integer and clamps it to −255…255, matching Arduino. Floats and booleans are rejected.
- `speed` reports the last successfully applied command. `stop()` commands zero.
- `close()` stops then releases this channel's pins; repeated calls do nothing. Further speed commands raise `RuntimeError`.
- A context manager handles cleanup. It cannot guarantee stopping after power loss, SIGKILL, an OS crash, or a GPIO/backend failure; use hardware shutdown provisions where needed.
- Before changing DIR, PWM is disabled. In PWM/PWM mode the opposite input is disabled first. There is no timed reversal delay or acceleration ramp; add a stop and suitable delay if required by your motor/load.
- Frequency is configurable in Hz; 1000 Hz is a conservative starting point, not a reproduction of Arduino's board-dependent PWM frequency. Check your driver's allowed range. GPIO Zero PWM is backend dependent, not guaranteed hardware PWM or real-time control.

## Tests without hardware

Install GPIO Zero, then run from this directory:

```sh
python -m unittest discover -s tests -v
```

Tests use GPIO Zero's `MockFactory` and `MockPWMPin`, covering both modes over the speed range, clamping, reversal ordering, initialization, validation, cleanup and independent channels. These verify software behavior, not electrical timing or actual motor operation.

MIT license; upstream copyright preserved in LICENSE and the module.
