import time, subprocess, argparse
import numpy as np
import pyaudio
import RPi.GPIO as GPIO

from openwakeword.model import Model
import sys
sys.path.insert(0,"/home/jwood/mic_hat/interfaces")

# flash the LEDs depending on mode
from pixels import Pixels

pix = Pixels()
pix.wakeup()

p = argparse.ArgumentParser()
p.add_argument("--debug", action="store_true")
args = p.parse_args()

BUTTON = 17
THRESHOLD = 0.5
DEBOUNCE_S = 3.0
ACK = "/home/jwood/wally-audio/yesjim.wav"   # adjust if your home dir differs

model = Model()
KEY = next(k for k in model.models.keys() if "hey_jarvis" in k)

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=1280)

# use button to turn of or on leds
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON,GPIO.IN)
led_state = 1

print("Listening for 'hey Jarvis' (stand-in for Hey Wally)... Ctrl-C to stop")
last_trigger = 0.0
try:
    while True:

        #toggle state
        state = GPIO.input(BUTTON)
        if not state:
            if led_state:
                led_state = 0
                pix.off()
            else:
                led_state = 1

            #debounce
            time.sleep(1)

        
        if led_state:
            pix.listen()

        frame = np.frombuffer(stream.read(1280, exception_on_overflow=False),
                              dtype=np.int16)
        scores = model.predict(frame)
        if led_state:
            pix.think()

        score = scores[KEY]
        if args.debug:
            print(f"\r{KEY}: {score:.2f}", end="", flush=True)
        now = time.time()
        if score >= THRESHOLD and now - last_trigger > DEBOUNCE_S:
            last_trigger = now
            if led_state:
                pix.speak()

            print(f"\nWAKE WORD detected (score {score:.2f}) — playing acknowledgment")
            subprocess.run(["aplay", ACK])
            model.reset()
            time.sleep(2.5)   # let the room go quiet before listening again
except KeyboardInterrupt:
    print("\nStopped")
finally:
    stream.stop_stream(); stream.close(); audio.terminate()
    pix.off()

