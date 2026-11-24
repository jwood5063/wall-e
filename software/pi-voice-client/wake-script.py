import time, subprocess, argparse
import numpy as np
import pyaudio
import RPi.GPIO as GPIO
import random
from itertools import cycle
from pathlib import Path
from queue import Empty, SimpleQueue

import shlex
from openwakeword.model import Model
import sys
sys.path.insert(0,"/home/jwood/mic_hat/interfaces")

# flash the LEDs depending on mode
from pixels import Pixels
pix = Pixels()
pix.wakeup()
# pix.think()

p = argparse.ArgumentParser()
p.add_argument("--debug", action="store_true")
args = p.parse_args()

# setup volume cycle so we can adjust volume with button
volumes = [1.0, 0.8, 0.5, 0.3, 0.1, 0.0]
volume_cycle = cycle(volumes)
volume=next(volume_cycle)

# wake model parameters
THRESHOLD = 0.5
DEBOUNCE_S = 3.0

# define some audio to use
ACK = "/home/jwood/wally-audio/yesjim.wav"   
SQUAWK_RANDOM_DIR = "/home/jwood/wall-e/squawk/random"
SQUAWK_FOUND = "/home/jwood/wall-e/squawk/robot_found_something.wav"
SQUAWK_OK = "/home/jwood/wall-e/squawk/robot_ok.wav"

# load our wake word model and find the key for the "hey_jarvis" model
# list the models so we can see what is available
model = Model()
KEY = next(k for k in model.models.keys() if "hey_jarvis" in k)
for k in model.models.keys():
    print(f"Model: {k}")

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=1280)

# use button to turn of or on leds
# setup callback for button press
BUTTON = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON,GPIO.IN)
button_queue = SimpleQueue()
def button_callback(channel):
    button_queue.put(channel)
GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Number 5 is alive!
subprocess.run(["aplay", SQUAWK_FOUND])

print("Listening for 'hey Jarvis' (stand-in for Hey Wally)... Ctrl-C to stop")
last_trigger = 0.0
try:
    while True:
        ##############################################################
        # Check for button press to adjust volume and toggle LEDs
        try:
            button_queue.get_nowait()
        except Empty:
            pass
        else:
            # Adjust volume to next level in the cycle
            volume = next(volume_cycle)
            print(f"volume {volume}")

            playcmd = f"ffmpeg -i {SQUAWK_OK} -af volume={volume} -f wav - 2>/dev/null | aplay -q"
            print(f"playcmd {playcmd}")
            subprocess.run(playcmd, shell=True)


        #######################################################################
        # Generate a random number to occasionally play a random squawk sound
        number = random.randint(1, 500)
        if number == 50:
            pix.speak()
            folder = Path(SQUAWK_RANDOM_DIR)
            files = [f for f in folder.iterdir() if f.is_file()]
            if files:
                random_file = random.choice(files)
                print(f"squawk random file {random_file}")

                playcmd = ( f"ffmpeg -i {shlex.quote(str(random_file))} "
                    f"-af volume={volume} -f wav - 2>/dev/null | aplay -q"
                )
                subprocess.run(playcmd, shell=True)


        ########################################################################
        # Read audio from the microphone and run the wake word model
        frame = np.frombuffer(stream.read(1280, exception_on_overflow=False),
                              dtype=np.int16)
        pix.think()
        scores = model.predict(frame)

        score = scores[KEY]
        if args.debug:
            print(f"\r{KEY}: {score:.2f}", end="", flush=True)
        now = time.time()
        if score >= THRESHOLD and now - last_trigger > DEBOUNCE_S:
            last_trigger = now

            print(f"\nWAKE WORD detected (score {score:.2f}) — playing acknowledgment")
            subprocess.run(["aplay", ACK])
            model.reset()
            time.sleep(2.5)   # let the room go quiet before listening again

        # if nothing else is happening, just keep the LEDs on and listening for the wake word
        pix.listen()
        
except KeyboardInterrupt:
    print("\nStopped")
finally:
    stream.stop_stream(); stream.close(); audio.terminate()
    pix.off()

