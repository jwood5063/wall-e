from PicoBreadboard import LED,BUZZER,BUTTON
import time

from machine import Pin, I2C
from mcp9808 import MCP9808

# Initialize I2C on MicroPython (I2C id 1, SCL=GP3, SDA=GP2 - change pins if needed)
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)

# Initialize the driver
sensor = MCP9808(i2c)

#create object for various class
LED1 = LED(0) #create object for LED class, LED connected at GP0
LED2 = LED(1)
LED3 = LED(6)

BT1 = BUTTON(4) # Button connected at GP4
BT2 = BUTTON(5)
LED1.off()
LED2.off()
LED3.off()

class State():
    IDLE = 1
    START_5V = 2
    START_12V = 3
    STOP_12V = 4
    STOP_5V = 5

buzzer = BUZZER(8) # Buzzer connected at GP8
state = State.IDLE

while True:
    temp_c = sensor.temperature
    temp_f = temp_c * 9 / 5 + 32
    print(f"Temperature: {temp_c:.2f} °C / {temp_f:.2f} °F")
    

    if state == State.IDLE:
        if BT1.read() == 1: #button pressed
           LED1.on()   #led 1 on
           print("5V ON")
           state = State.START_5V
       
    if state == State.START_5V:
        if BT2.read() == 1:  #power up motors
            state = State.START_12V
            LED2.on()
            print("motor power up")
            
    if state == State.START_12V:
        if BT2.read() == 0:
            state = State.STOP_12V
            LED3.on()
            print("motor off")
               
    time.sleep(0.5) # delay 500ms
   
