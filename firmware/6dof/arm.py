import machine
import time
import math

class RobotArm6DoF:
    def __init__(self, pins, min_us=500, max_us=2500, freq=50):
        """
        Initializes the 6DoF Robot Arm.
        pins: List of 6 GPIO pin numbers [Base, Shoulder, Elbow, WristPitch, WristRoll, Gripper]
        """
        self.min_us = min_us
        self.max_us = max_us
        self.freq = freq
        
        # Initialize 6 PWM channels
        self.joints = []
        for pin in pins:
            pwm = machine.PWM(machine.Pin(pin))
            pwm.freq(self.freq)
            self.joints.append(pwm)
            
        # Track the current angles of all 6 joints (initialized to 90 degrees/midpoint)
        self.current_angles = [90.0] * 6
        self.move_to_angles(self.current_angles)

    def _angle_to_duty(self, angle):
        """Converts an angle (0-180) to a 16-bit PWM duty cycle (0-65535)"""
        # Clamp angle between 0 and 180
        angle = max(0, min(180, angle))
        # Map angle to pulse width in microseconds
        us = self.min_us + (angle / 180.0) * (self.max_us - self.min_us)
        # Map microseconds to 16-bit duty cycle (Period for 50Hz is 20000us)
        duty = int((us / 20000.0) * 65535)
        return duty

    def move_joint(self, joint_idx, angle):
        """Instantly moves a single joint (0-5) to a specific angle"""
        if 0 <= joint_idx < 6:
            duty = self._angle_to_duty(angle)
            self.joints[joint_idx].duty_u16(duty)
            self.current_angles[joint_idx] = angle

    def move_to_angles(self, target_angles):
        """Instantly moves all 6 joints to a target list of angles"""
        for i in range(6):
            self.move_joint(i, target_angles[i])

    def move_smooth(self, target_angles, speed_deg_per_sec=45):
        """
        Smoothly interpolates all 6 joints to a target position simultaneously.
        Non-blocking to the mechanical structure (moves all joints in small steps).
        """
        step_time = 0.02  # 20ms steps (matches 50Hz update rate)
        max_diff = 0
        
        # Calculate the maximum angular distance any single joint needs to travel
        for i in range(6):
            diff = abs(target_angles[i] - self.current_angles[i])
            if diff > max_diff:
                max_diff = diff
                
        if max_diff == 0:
            return

        # Calculate total duration and total steps needed for the movement
        duration = max_diff / speed_deg_per_sec
        steps = int(duration / step_time)
        if steps < 1: steps = 1

        # Calculate step increments for each joint
        increments = [(target_angles[i] - self.current_angles[i]) / steps for i in range(6)]

        # Interpolation loop
        for step in range(steps):
            for i in range(6):
                next_angle = self.current_angles[i] + increments[i]
                self.move_joint(i, next_angle)
            time.sleep(step_time)

        # Final alignment to eliminate floating point rounding errors
        self.move_to_angles(target_angles)

# ==========================================
# EXAMPLE EXECUTION
# ==========================================

# 1. Define the 6 GPIO pins connected to your robot arm servos.
# Adjust these numbers based on how your Pico is physically wired.
# Order: [Base, Shoulder, Elbow, Wrist Pitch, Wrist Roll, Gripper]
PICO_PINS = [0, 1, 2, 3, 4, 5]

print("Initializing 6DoF Robot Arm...")
arm = RobotArm6DoF(pins=PICO_PINS)
time.sleep(1)

# Define a couple of poses [Base, Shoulder, Elbow, WPitch, WRoll, Gripper]
home_pose  = [90, 90, 90, 90, 90, 90]
reach_pose = [45, 120, 60, 45, 90, 150]
pick_pose  = [45, 120, 60, 45, 90, 30]  # Gripper pin closed down

try:
    while True:
        print("Moving to Home Pose smoothly...")
        arm.move_smooth(home_pose, speed_deg_per_sec=30)
        time.sleep(2)
        
        print("Reaching for object...")
        arm.move_smooth(reach_pose, speed_deg_per_sec=45)
        time.sleep(1)
        
        print("Closing gripper...")
        arm.move_smooth(pick_pose, speed_deg_per_sec=60)
        time.sleep(2)

except KeyboardInterrupt:
    print("Program stopped. Disabling PWM signals.")
    # Deinitialize/turn off duty cycles for safety
    for joint in arm.joints:
        joint.duty_u16(0)

