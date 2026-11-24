import unittest
from unittest.mock import patch

from gpiozero.pins.mock import MockFactory, MockPWMPin
from cytron_motor_driver import CytronMD, PWM_DIR, PWM_PWM


class MotorTests(unittest.TestCase):
    def setUp(self):
        self.factory = MockFactory(pin_class=MockPWMPin)
        self.addCleanup(self.factory.close)

    def motor(self, mode=PWM_DIR, pins=(18, 23)):
        motor = CytronMD(mode, *pins, pin_factory=self.factory)
        self.addCleanup(motor.close)
        return motor

    def values(self, pins=(18, 23)):
        return tuple(self.factory.pin(pin).state for pin in pins)

    def test_all_speeds_and_clamping(self):
        for mode in (PWM_DIR, PWM_PWM):
            with self.subTest(mode=mode), self.motor(mode) as motor:
                self.assertEqual(self.values(), (0, 0))
                for requested in range(-300, 301):
                    motor.setSpeed(requested)
                    speed = max(-255, min(255, requested))
                    duty = abs(speed) / 255
                    expected = ((duty, speed < 0) if mode == PWM_DIR else
                                ((duty, 0) if speed >= 0 else (0, duty)))
                    for actual, value in zip(self.values(), expected):
                        self.assertAlmostEqual(actual, value)
                    self.assertEqual(motor.speed, speed)
                motor.stop()
                self.assertEqual(self.values(), (0, 0))

    def test_transitions_never_drive_both_pwm_inputs(self):
        motor = self.motor(PWM_PWM)
        observations = []
        for pin in (18, 23):
            gpio = self.factory.pin(pin)
            original = gpio._set_state
            def record(value, original=original):
                original(value)
                observations.append(self.values())
            patcher = patch.object(gpio, '_set_state', side_effect=record)
            patcher.start()
            self.addCleanup(patcher.stop)
        for speed in (255, -255, 128, -128, 0):
            motor.set_speed(speed)
        self.assertTrue(observations)
        self.assertTrue(all(not (a and b) for a, b in observations))

    def test_direction_changes_with_pwm_off(self):
        motor = self.motor()
        direction = self.factory.pin(23)
        original = direction._set_state
        def record(value):
            if bool(direction.state) != bool(value):
                self.assertEqual(self.factory.pin(18).state, 0)
            original(value)
        with patch.object(direction, '_set_state', side_effect=record):
            for speed in (255, -255, 255, -128, 0):
                motor.set_speed(speed)

    def test_close_and_exception_cleanup(self):
        motor = self.motor()
        with self.assertRaisesRegex(RuntimeError, 'example'):
            with motor:
                motor.set_speed(255)
                raise RuntimeError('example')
        self.assertTrue(motor.closed)
        self.assertEqual(motor.speed, 0)
        motor.close()
        with self.assertRaises(RuntimeError):
            motor.set_speed(1)
        # Closing released the reservations.
        self.motor()

    def test_dual_channels_are_independent(self):
        left = self.motor(PWM_PWM)
        right = self.motor(PWM_PWM, (17, 22))
        left.set_speed(255)
        right.set_speed(-128)
        left.close()
        self.assertEqual(right.speed, -128)
        self.assertAlmostEqual(self.factory.pin(22).state, 128 / 255)

    def test_validation_and_partial_construction_cleanup(self):
        for kwargs in ({'mode': 2}, {'mode': True}, {'pin1': 23},
                       {'pin1': -1}, {'pin2': True}, {'frequency': 0},
                       {'frequency': float('nan')}):
            params = dict(mode=PWM_DIR, pin1=18, pin2=23, pin_factory=self.factory)
            params.update(kwargs)
            with self.assertRaises((ValueError, TypeError)):
                CytronMD(**params)
        motor = self.motor()
        for speed in (1.5, True, '100', None):
            with self.assertRaises(TypeError):
                motor.set_speed(speed)
        with self.assertRaises(Exception):
            CytronMD(PWM_DIR, 17, 23, pin_factory=self.factory)
        # pin 17 must be released after the second pin failed to initialize.
        self.motor(PWM_DIR, (17, 22))


if __name__ == '__main__':
    unittest.main()
