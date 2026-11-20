"""PWM_DIR: BCM18 -> PWM, BCM23 -> DIR, Pi GND -> driver GND."""
from time import sleep
from cytron_motor_driver import CytronMD, PWM_DIR


def main():
    with CytronMD(PWM_DIR, 18, 23) as motor:
        motor.setSpeed(128)
        sleep(2)
        motor.stop()
        sleep(1)
        motor.setSpeed(-128)
        sleep(2)


if __name__ == "__main__":
    main()
