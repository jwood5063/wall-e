```bash
mkdir -p ~/wally-audio

echo "Controller connected." | ~/piper/piper \
  --model ~/piper/voices/en_US-lessac-medium.onnx \
  --output_file /tmp/controller_raw.wav

ffmpeg -y -i /tmp/controller_raw.wav -af "rubberband=pitch=1.1,tremolo=f=30:d=0.5,acrusher=bits=6:mix=0.4,highpass=f=400,lowpass=f=4200,acompressor=threshold=-20dB:ratio=9:attack=5:release=120:makeup=6,aecho=0.8:0.7:15:0.25,volume=1.4,alimiter=limit=0.9" \
  ~/wally-audio/controller_connected.wav

aplay ~/wally-audio/controller_connected.wav
```

```
cat > ~/.config/systemd/user/wake-listen.service << 'EOF'
[Unit]
Description=Wall-E wake word listener
After=default.target

[Service]
WorkingDirectory=%h
ExecStart=%h/voice-venv/bin/python %h/wake_listen.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now wake-listen.service
systemctl --user status wake-listen.service --no-pager

systemctl --user start wake-listen.service
systemctl --user stop wake-listen.service


```
