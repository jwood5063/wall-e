# Pico power sequencer / motor firmware

**Placeholder.** Jim's sequencer firmware currently lives on the Pico on
the bench; this folder is its home when it's copied off the board.

What the one Pico firmware does (design in `docs/wall-e-robot-plan.md`):

- **Power sequencing:** battery -> Pico -> 5 V Pi rail -> wait for the
  Pi's heartbeat over USB serial -> only then enable the 12 V motor rail.
  Shutdown/fault reverses the order; a latched fault clears only by Pico
  reset. v1 is proven working on the bench; the v2 spec uses a pulse
  heartbeat (`HB <counter>` every 250 ms, 1000 ms watchdog, 60 s boot
  wait that is *not* a fault, `SHUTDOWN` handshake).
- **Motor/encoder control:** PWM + DIR to the Cytron MDD10A, PIO encoder
  counting. Connector pinouts are on the carrier schematic in
  `hardware/pico-carrier/`.
- **Thermal monitoring:** MCP9808 (I2C) is live in the sequencer today;
  a DS18B20 1-Wire bus (battery, driver, motor cans, power distribution,
  charge connector) and an SHT41 are planned. Policy: a hot reading kills
  the rail its sensor guards; bay/body air sensors warn only.
  Caution: DS18B20 conversions take up to 750 ms — always split
  convert/read so the bus can never stall the heartbeat watchdog.

Rail switching: motor rail via the Pololu Big MOSFET Slide Switch HP
(#2815, GPIO14), charge path via the Pololu Isolated SSR (#5421, GPIO15) —
both plain logic outputs from this board.
