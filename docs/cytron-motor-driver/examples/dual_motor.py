"""PWM_PWM: BCM17/18 -> channel 1 A/B; BCM22/23 -> channel 2 A/B."""
from time import sleep
from cytron_motor_driver import CytronMD, PWM_PWM


def main():
    with CytronMD(PWM_PWM, 17, 18) as left, CytronMD(PWM_PWM, 22, 23) as right:
        left.set_speed(128)
        right.set_speed(128)
        sleep(2)
        left.stop()
        right.stop()
        sleep(1)
        left.set_speed(-128)
        right.set_speed(-128)
        sleep(2)


if __name__ == "__main__":
    main()
