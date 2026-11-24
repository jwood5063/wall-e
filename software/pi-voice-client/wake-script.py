import time, subprocess, argparse
import numpy as np
import pyaudio
import RPi.GPIO as GPIO
import random
from itertools import cycle
from pathlib import Path

import shlex
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

volumes = [1.0, 0.8, 0.5, 0.3, 0.1]
volume_cycle = cycle(volumes)
volume=next(volume_cycle)

BUTTON = 17
THRESHOLD = 0.5
DEBOUNCE_S = 3.0
ACK = "/home/jwood/wally-audio/yesjim.wav"   # adjust if your home dir differs

SQUAWK_RANDOM_DIR = "/home/jwood/wall-e/squawk/random"
SQUAWK_FOUND = "/home/jwood/wall-e/squawk/robot_found_something.wav"
SQUAWK_OK = "/home/jwood/wall-e/squawk/robot_ok.wav"

model = Model()
KEY = next(k for k in model.models.keys() if "hey_jarvis" in k)

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=1280)

# use button to turn of or on leds
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON,GPIO.IN)
led_state = 1

subprocess.run(["aplay", SQUAWK_FOUND])

print("Listening for 'hey Jarvis' (stand-in for Hey Wally)... Ctrl-C to stop")
last_trigger = 0.0
try:
    while True:
        # Generates a random integer from 1 to 1000 (inclusive)
        number = random.randint(1, 500)
        if number == 50:
            folder = Path(SQUAWK_RANDOM_DIR)
            files = [f for f in folder.iterdir() if f.is_file()]
            if files:
                random_file = random.choice(files)

                playcmd = ( f"ffmpeg -i {shlex.quote(str(random_file))} "
                    f"-af volume={volume} -f wav - 2>/dev/null | aplay -q"
                )
                subprocess.run(playcmd, shell=True)
                #playcmd = f"ffmpeg -i {random_file.name} -af volume={volume} -f wav - 2>/dev/null | aplay -q"
                #subprocess.run(playcmd, shell=True)


        #toggle state
        state = GPIO.input(BUTTON)
        if not state:
            #global volume
            volume = next(volume_cycle)
            print(f"volume {volume}")

            if led_state:
                led_state = 0
                pix.off()
            else:
                led_state = 1
             
            playcmd = f"ffmpeg -i {SQUAWK_OK} -af volume={volume} -f wav - 2>/dev/null | aplay -q"
            print(f"playcmd {playcmd}")
            subprocess.run(playcmd, shell=True)

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

