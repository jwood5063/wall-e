"""Cytron PWM motor control for Raspberry Pi using GPIO Zero.

Adapted from https://github.com/CytronTechnologies/CytronMotorDriver
Copyright (c) 2019 CytronTechnologies. MIT license; see LICENSE.
"""
from enum import IntEnum
from math import isfinite
from numbers import Integral, Real
from threading import RLock

from gpiozero import DigitalOutputDevice, PWMOutputDevice


class MODE(IntEnum):
    PWM_DIR = 0
    PWM_PWM = 1


PWM_DIR = MODE.PWM_DIR
PWM_PWM = MODE.PWM_PWM


class CytronMD:
    """One motor channel. Pins are BCM numbers, speed is -255..255.

    PWM_DIR: pin1=PWM, pin2=DIR (LOW forward, HIGH reverse).
    PWM_PWM: pin1=forward PWM, pin2=reverse PWM.
    Use one instance per channel on dual/multi-channel drivers.
    """

    def __init__(self, mode, pin1, pin2, *, frequency=1000, pin_factory=None):
        if isinstance(mode, bool):
            raise ValueError("mode must be PWM_DIR or PWM_PWM")
        self.mode = MODE(mode)
        for pin in (pin1, pin2):
            if isinstance(pin, bool) or not isinstance(pin, Integral) or not 0 <= pin <= 27:
                raise ValueError("pins must be BCM GPIO integers from 0 to 27")
        if pin1 == pin2:
            raise ValueError("pin1 and pin2 must be different")
        if (isinstance(frequency, bool) or not isinstance(frequency, Real)
                or not isfinite(frequency) or frequency <= 0):
            raise ValueError("frequency must be a positive finite number in Hz")
        self._lock = RLock()
        self._closed = False
        self._speed = 0
        self._pin1 = PWMOutputDevice(
            pin1, initial_value=0, frequency=frequency, pin_factory=pin_factory)
        try:
            if self.mode == PWM_DIR:
                self._pin2 = DigitalOutputDevice(
                    pin2, initial_value=False, pin_factory=pin_factory)
            else:
                self._pin2 = PWMOutputDevice(
                    pin2, initial_value=0, frequency=frequency, pin_factory=pin_factory)
        except BaseException:
            self._pin1.close()
            raise

    @property
    def speed(self):
        """Last successfully commanded speed after clamping."""
        return self._speed

    @property
    def closed(self):
        return self._closed

    def set_speed(self, speed):
        """Set integer speed, clamped to -255..255, like Arduino setSpeed."""
        if isinstance(speed, bool) or not isinstance(speed, Integral):
            raise TypeError("speed must be an integer")
        speed = max(-255, min(255, int(speed)))
        with self._lock:
            if self._closed:
                raise RuntimeError("motor driver is closed")
            duty = abs(speed) / 255.0
            if self.mode == PWM_DIR:
                # Remove drive before changing DIR, including reverse -> stop.
                if bool(self._pin2.value) != (speed < 0):
                    self._pin1.value = 0
                self._pin2.value = speed < 0
                self._pin1.value = duty
            elif speed >= 0:
                # Always disable the opposite input first.
                self._pin2.value = 0
                self._pin1.value = duty
            else:
                self._pin1.value = 0
                self._pin2.value = duty
            self._speed = speed

    setSpeed = set_speed

    def stop(self):
        """Command zero speed; braking/coasting depends on the driver."""
        self.set_speed(0)

    def close(self):
        """Stop and release only this channel's GPIO resources. Idempotent."""
        with self._lock:
            if self._closed:
                return
            try:
                self.stop()
            finally:
                try:
                    self._pin1.close()
                finally:
                    try:
                        self._pin2.close()
                    finally:
                        self._closed = True

    def __enter__(self):
        if self.closed:
            raise RuntimeError("motor driver is closed")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
