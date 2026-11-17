# Wall-E — System Block Diagram

_Created 2026-11-15 (Wally) as Jim's working reference for the full electrical/system
design. Sources: the build plan (`wall-e-robot-plan.md`), the power control PCB notes
(`power-control-pcb-notes.md`), the charging dock build page (`charging-dock-build.md`),
and the carrier netlist verified 2026-11-05. Where a decision is still open, the block
says TBD — nothing here invents a decision._

**How to read:** solid arrows `──►` are power flow. Dashed arrows `┄►` are signal/data.
Diagrams are Mermaid — they render in GitHub, Obsidian, and most Markdown viewers, and
the text stays editable as the design changes.

---

## 1. Whole-system overview

```mermaid
flowchart TB
    subgraph CLOUD["Cloud"]
        WALLY["Wally / Muse<br/>conversation, personality,<br/>high-level decisions"]
    end

    subgraph HOME["Home (off-robot)"]
        HA["Home Assistant (Pi 5, home)<br/>dashboards, automations,<br/>Life360, Ring (ring-mqtt)"]
        XBOX["Xbox Wireless Controller<br/>teleop"]
    end

    subgraph DOCK["Charging dock (power + geometry only)"]
        PSU24["24V DC supply"]
        CHG["SparkFun PRT-18722<br/>12.6V CC/CV charger, ~2A class"]
        DOCKCON["Magnetic connector, dock half<br/>Adafruit #5358<br/>pins 1+2 = +12.6V, 3+4 = GND"]
        TAG["AprilTag (tag36h11)<br/>final-approach target"]
        PSU24 --> CHG --> DOCKCON
    end

    subgraph ROBOT["Wall-E robot"]
        subgraph PWR["Power (see diagram 2)"]
            PACK["TalentCell YB12011000<br/>12V pack, switch ON permanently"]
            ANKER["Anker A1695<br/>5V Pi rail, pass-through charge"]
            PCB["Power control PCB<br/>distribution + regulators (scope TBD)"]
            SEQ["Pico — sequencer + motor control<br/>+ thermal monitor (one firmware)"]
            PACK --> PCB
            PCB --> SEQ
        end

        PI5["Raspberry Pi 5 (main)<br/>ROS 2 + Nav2, wake word, STT/TTS,<br/>publishes status/telemetry topics, HA link"]
        DISPPI["Display Pi = second Raspberry Pi 5<br/>(on hand, Jim 2026-11-15)<br/>ROS 2 subscriber node + local web<br/>server + kiosk browser (decided 2026-11-16)"]
        PANEL["Waveshare 7inch DSI LCD (E) 1280x800<br/>ORDERED 2026-11-15, arriving Wed Nov 18<br/>mounts on tray front fascia (fit gated<br/>on fascia height, ~110mm needed)"]
        ESP["ESP32-S3-WROOM<br/>ESPHome sensor/servo hub"]
        ARM["6DOF arm (Pavv mule now)<br/>6x servos, head rides the arm"]
        MDD["Cytron MDD10A<br/>dual motor driver"]
        MOT["2x JGB37-520 gear motors<br/>+ encoders (tracked chassis)"]
        LIDAR["RPLIDAR C1<br/>rear pedestal, tallest point"]
        TFL["TF-Luna<br/>cliff / dock ranging, front low"]
        GEM["Orbbec Gemini 2 (planned)<br/>depth camera + IMU, arm tip"]
        GSCAM["Pi Global Shutter Camera<br/>onboard eye (out of stock)"]
        RING["Ring Indoor Cam Gen 1<br/>other eye, report-back / sentry"]
        MIC["ReSpeaker 2-Mic HAT V2.0<br/>on Pi 5"]
        AMP["MAX98357A amp + 3W speaker"]
        THERM["Thermal: 6x DS18B20 + MCP9808<br/>+ SHT41 (on Pico buses)"]

        SEQ -.->|"USB serial: HB, commands,<br/>state, rail + temp read-backs"| PI5
        SEQ -.->|"PWM/DIR via carrier J2"| MDD
        MDD --> MOT
        MOT -.->|"encoder A/B via carrier J10/J11"| SEQ
        PI5 -.->|"WiFi"| WALLY
        PI5 -.->|"WiFi (HA bridge; MQTT ok here,<br/>bridge may run on either Pi)"| HA
        XBOX -.->|"Bluetooth"| PI5
        PI5 -.->|"wired Ethernet: ROS 2 topics<br/>(status / telemetry)"| DISPPI
        DISPPI -.->|"DSI"| PANEL
        ESP -.->|"6x PWM servo signals"| ARM
        PCB -->|"6.8V servo rail (power only)"| ARM
        PI5 -.->|"USB/UART (sllidar_ros2)"| LIDAR
        PI5 -.->|"UART/I2C"| TFL
        PI5 -.->|"USB-C (power + data)"| GEM
        PI5 -.->|"CSI ribbon, CAM port"| GSCAM
        PCB -->|"5V accessory rail"| RING
        PI5 -.->|"WiFi (Ring cloud)"| RING
        MIC -.->|"I2S + I2C on Pi header"| PI5
        PI5 -.->|"I2S (shared bus)"| AMP
        THERM -.->|"1-Wire GP6 / I2C GP4-5"| SEQ
        DOCKCON -->|"12.6V when docked"| PCB
        GEM -.->|"views dock AprilTag"| TAG
    end
```

**Reading notes**
- The Pico is the safety root: it owns motor power and the watchdog. No Pi, network,
  or cloud failure can leave the robot driving.
- The dock has **no intelligence** — every charge decision is made on the robot,
  by the sequencer.
- Arm-tip camera is the current recommendation (Gemini 2 on the tip, GS camera
  body-fixed when it arrives, Ring stationary) — Jim's arm-tip proposal is still
  formally undecided; the head-pods layout in the plan is the fallback shape.
- **Display data (decided 2026-11-16):** the display Pi runs ROS 2 (Jazzy) as a
  subscriber-only node on a **wired Ethernet** link to the main Pi — wired, so DDS
  discovery never depends on WiFi multicast. It hosts its own web server and kiosk
  locally and bridges topics to the browser. If topics go silent, the display shows
  link-loss as its own state instead of a frozen page. **MQTT scope (Jim,
  2026-11-16):** not used for the inter-Pi display path — but MQTT is fine for the
  **Home Assistant bridge**, which may run on either Pi. So the Nov 14 room-sensor
  idea stands: current room reaches HA via the MQTT bridge (MQTT discovery).

---

## 2. Power architecture (detail)

```mermaid
flowchart LR
    subgraph DOCKP["Dock"]
        DCHG["SparkFun PRT-18722<br/>12.6V CC/CV, ~2A class<br/>(fed by 24V supply)"]
        DFUSE["3A fuse (dock side)"]
        DCON["Magnetic connector #5358<br/>dock half"]
        DCHG --> DFUSE --> DCON
    end

    subgraph ROBOTP["Robot"]
        RCON["Magnetic connector #5358<br/>robot half"]
        RFUSE["3A fuse (robot side)"]
        SSR["Pololu Isolated SSR #5421<br/>charge enable<br/>EN from Pico GPIO15 (carrier J7)"]
        HARD["Physical hard disconnect<br/>(part TBD — the real safety cutoff)"]
        PACK2["TalentCell YB12011000<br/>122Wh class, 12V/6A max<br/>DC5521 port, rocker ON permanently<br/>(rocker = manual master-off)"]
        MAIN["Power control PCB<br/>main fuse, reverse-polarity prot.,<br/>distribution, regulators (scope TBD)"]
        SW2815["Pololu Big MOSFET Switch HP #2815<br/>motor rail switch<br/>ON from Pico GPIO14 (carrier J8)<br/>16A cont / 90A max"]
        MDD2["Cytron MDD10A<br/>5-30V in, 10A cont/ch"]
        MOT2["Drive motors L/R<br/>~2.4A stall each"]
        BUCK68["Adjustable buck<br/>SERVO RAIL 6.8V<br/>~6A cont / 10A peak, Pico EN"]
        ARM2["Arm servos x6<br/>power/ground only from this board;<br/>signals from ESP32-S3"]
        BUCK5["Adjustable buck<br/>5V ACCESSORY rail, ~3A class"]
        RING2["Ring Indoor Cam Gen 1 (5V USB)"]
        TFL2["TF-Luna (5V)"]
        PICO2["Pico (always-on)<br/>fed first, before all rails"]
        VSENSE["VSense taps after each switch/regulator<br/>to Pico ADC via carrier dividers<br/>(39K/10K 12V rails, 10K/10K VSYS)"]

        RCON --> RFUSE --> SSR --> PACK2
        PACK2 --> HARD --> MAIN
        MAIN --> PICO2
        MAIN --> SW2815 --> MDD2 --> MOT2
        MAIN --> BUCK68 --> ARM2
        MAIN --> BUCK5 --> RING2
        BUCK5 --> TFL2
        MAIN -.-> VSENSE
    end

    subgraph PIRAIL["Pi rail (separate, off the power PCB by default)"]
        ANKER2["Anker A1695 power bank<br/>USB-C PD, pass-through charging"]
        PI52["Raspberry Pi 5 + ReSpeaker HAT<br/>(+ MAX98357A amp off 5V header pins)"]
        DISPPI2["Display Pi + fascia panel<br/>(power route TBD)"]
        ANKER2 --> PI52
        ANKER2 -.->|"TBD"| DISPPI2
    end

    DCON -->|"mates when docked"| RCON
```

**Sequence (Pico-owned, binding on every board):**
battery → Pico live → Pi rail on → Pi heartbeat `HB <counter>` every 250 ms over USB
serial → only then motor rail on. Watchdog 1000 ms; 60 s boot wait is not a fault;
`SHUTDOWN` reverses the order cleanly. Thermal policy: battery/charge-connector hot →
charge path opens; driver/motors/power-distribution hot → motor rail off; bay/body
air hot → warn only.

**Known caveats carried in the design:**
- Pack spec lists both 12V/6A max and 3A max continuous — treat 6A as peak until the
  motors+arm stall test (after delivery) proves otherwise.
- Servo rail is **6.8V, not 7.4V** (MG996R max 7.2V; DS3218/DS3225-class max 6.8V).
- Charge only flows with the pack rocker ON — it stays ON permanently by decision
  (locked 2026-11-15); the SSR, not the rocker, gates charging.


---

## 3. Compute, control and data paths (detail)

```mermaid
flowchart TB
    PI5["Raspberry Pi 5 — ROS 2 / Nav2<br/>velocity commands, nav goals,<br/>wake word, faster-whisper STT,<br/>Piper TTS via locked voice chain"]
    PICO["Pico (on carrier PCB 'Wall-E Monitor')<br/>PIO encoder counting, PWM gen,<br/>sequencer, watchdog, thermal"]
    ESP["ESP32-S3-WROOM — ESPHome hub<br/>servo PWM, head/sensor extras"]
    CLOUD2["Wally / Muse (cloud, via WiFi)<br/>conversation + high-level decisions"]
    HA2["Home Assistant (home Pi 5)<br/>state mirror, automations, 'go look'"]

    PI5 -.->|"USB serial: HB 250ms, velocity cmds,<br/>SHUTDOWN; Pico announces STATE,<br/>rail voltages, temps"| PICO
    PICO -.->|"carrier J2 (5-pin 2510):<br/>PWM_L GP12, DIR_L GP2,<br/>PWM_R GP13, DIR_R GP3"| MDD3["Cytron MDD10A"]
    MDD3 -->|"M+/M- via carrier 6-pin JST<br/>GND, A, B, VCC, M+, M-"| MOT3["Motors + encoders"]
    MOT3 -.->|"encoders: carrier J10/J11 (JST PH 4-pin)<br/>1=GND 2=+3.3V 3=A 4=B<br/>ENC_L GP8/9, ENC_R GP10/11"| PICO
    ESP -.->|"PWM: base GP4, shoulder GP5, elbow GP6,<br/>wrist pitch GP7, wrist roll GP15, gripper GP16<br/>(Pavv bench test wiring)"| ARM3["Arm servos x6"]
    PI5 -.->|"WiFi"| CLOUD2
    PI5 -.->|"WiFi"| HA2
    PI5 -.->|"wired Ethernet: ROS 2 topics"| DISP2["Display Pi 5 — ROS 2 subscriber node<br/>local web server + kiosk browser<br/>link-loss shown as its own state"]
    PI5 -.->|"ESPHome API (WiFi)"| ESP
    PI5 -.->|"I2S: ReSpeaker HAT (TLV320AIC3104, card 2)<br/>mics in, audio out"| AMP3["MAX98357A amp (I2S tap: BCLK pin12,<br/>LRCLK pin35, DOUT pin40, 5V pin2, GND pin6)<br/>bridge-tied out to 3W 4-ohm speaker"]
    PI5 -.->|"CSI: GS camera (eye) / USB: See3CAM bench cam,<br/>Gemini 2 / UART: RPLIDAR C1, TF-Luna"| SENS["Sensor set (see overview)"]
```

**Display data contract (decided 2026-11-16)** — topics the main Pi publishes and
the display Pi subscribes to over the wired Ethernet link:
sequencer state + rail voltages (Pico telemetry, bridged by the main Pi) ·
battery percent, charging/docked state, charge current ·
temperatures (DS18B20 set + MCP9808 + SHT41) ·
nav goal + status, current room/waypoint ·
faults (heartbeat loss, thermal rail shutdowns) — latched on the display until cleared.
MQTT is reserved for the Home Assistant bridge only (either Pi may host it) —
never the inter-Pi display path (Jim, 2026-11-16).

**Pico carrier (Jim's KiCad 'manager' board) — verified netlist pinouts, 2026-11-05**
(the redesign around the motors' 6-pin JST connectors is in progress; these are the
last verified values — re-verify from the new file when it lands)

| Connector | Pins | Carries |
|---|---|---|
| J2 Motor_Driver (5-pin 2510) | 1 GND, 2 PWM_L GP12, 3 DIR_L GP2, 4 PWM_R GP13, 5 DIR_R GP3 | Pico → MDD10A logic (no motor current) |
| Motors (6-pin JST, new) | GND, A, B, VCC, M+, M− | MDD10A outputs in via screw terminals, out to motors; encoders return on A/B |
| J10 / J11 Encoders (JST PH 4-pin) | 1 GND, 2 +3.3V, 3 A, 4 B | ENC_L GP8/9, ENC_R GP10/11 (older separate-connector scheme) |
| J7 Charge_en (JST PH 4-pin) | 1 GND, 2 +3.3V, 3 enable GP15, 4 NC | → SSR #5421 (VIN=pin2, EN=pin3, GND=pin1) |
| J8 Motor_en (JST PH 4-pin) | 1 GND, 2 +3.3V, 3 enable GP14, 4 NC | → #2815 ON pin (uses pins 3+1 only) |
| J4 / J5 I2C (JST PH 4-pin) | 1 GND, 2 +3.3V, 3 SDA GP4, 4 SCL GP5 | MCP9808 (bay), SHT41 (body ambient); 4.7K pull-ups on board |
| J14–J19 Temp (3-pin) | 1 GND, 2 +3.3V, 3 DQ GP6 | 6× DS18B20: battery, MDD10A, motor L, motor R, power distribution, charge connector; 4.7K pull-up at Pico end |
| VSense (J12) | batt_rail, motor_rail (+ VSYS) | Dividers 39K/10K (12V rails), 10K/10K (VSYS), 100nF node caps → Pico ADC |
| J1 Spare IO | GP7, GP16–22, 3.3V, GND | Expansion |

Pico power on the carrier: datasheet-style 5V OR-ing into VSYS (Q1 DMP2035U P-FET);
status LEDs on GP0/1 mirror *measured* state.

---

## 4. Interface list (every wire that crosses a block boundary)

| # | From → To | Type | Connector / medium | Key values |
|---|---|---|---|---|
| 1 | TalentCell → power PCB | Power | DC5521 barrel, centre + | 9–12.6V, 6A max (3A cont caveat) |
| 2 | Power PCB → #2815 → MDD10A | Power | 5mm terminal blocks | Raw battery, motor rail |
| 3 | MDD10A → motors | Power | Carrier screw terminals → 6-pin JST | M+/M− per channel, 10A cont capable |
| 4 | Power PCB → arm servos | Power | 3-pin 2.54mm headers ×6 | 6.8V + GND only (no signals) |
| 5 | Power PCB → Ring cam, TF-Luna | Power | USB-A / pigtail (TBD at layout) | 5V accessory rail, ~3A class |
| 6 | Anker → Pi 5 | Power | USB-C PD | 5V (PD profile; 5A appetite caveat, Witty Pi 5 open) |
| 7 | Dock charger → dock connector | Power | Wire + 3A fuse | 12.6V, ~2A class |
| 8 | Dock ↔ robot connector | Power | Adafruit #5358 magnetic pair | 1+2 = +12.6V, 3+4 = GND, fused both sides |
| 9 | Robot connector → SSR → pack | Power | Wire + 3A fuse | Charge path, Pico-gated |
| 10 | Pico → Pi 5 | Data | USB serial | HB/cmds/state/rail+temp telemetry |
| 11 | Pico → MDD10A | Signal | Carrier J2 | PWM/DIR ×2, 3.3V logic |
| 12 | Encoders → Pico | Signal | 6-pin JST A/B (or J10/J11) | 3.3V only into Pico GPIO |
| 13 | Pico → #2815 / SSR | Signal | Carrier J8 / J7 (JST PH 4-pin) | GP14 / GP15 enables |
| 14 | Pico → DS18B20 bus | Signal | Carrier J14–J19 | 1-Wire DQ GP6, 4.7K pull-up |
| 15 | Pico → MCP9808 / SHT41 | Data | Carrier J4/J5 | I2C GP4/GP5 |
| 16 | ESP32-S3 → arm servos | Signal | GPIO header wiring | 6× PWM (pins in diagram 3) |
| 17 | ESP32-S3 ↔ Pi 5 / HA | Data | WiFi (ESPHome) | Servo cmds, sensor states |
| 18 | Pi 5 → RPLIDAR C1 | Data | USB/UART | sllidar_ros2, 360° scan |
| 19 | Pi 5 → TF-Luna | Data | UART/I2C | 1D range, cliff/dock |
| 20 | Pi 5 → Gemini 2 | Data+power | USB-C | Depth + IMU; 2.5W typ / 7W peak, budget 5V ≥1.5A |
| 21 | Pi 5 → GS camera | Data | CSI ribbon (CAM port) | Service loop through head/arm joint — wear point |
| 22 | Pi 5 → ReSpeaker HAT | Audio | 40-pin header, I2S + I2C | Card 2, TLV320AIC3104 |
| 23 | Pi header → MAX98357A | Audio | I2S tap (pins 12/35/40/2/6) | Bridge-tied speaker out, neither lead is GND |
| 24 | Pi 5 → display Pi | Data | Wired Ethernet (decided 2026-11-16) | ROS 2 topics: sequencer state, rail voltages, temps, battery/dock, nav status, faults; display Pi serves the kiosk UI locally |
| 25 | Display Pi → panel | Video | DSI | 1280×800 (if 7-inch panel; fascia TBD) |
| 26 | Xbox controller → Pi 5 | Data | Bluetooth (xpadneo) | Teleop; A button = voice trigger (remap pending) |
| 27 | Pi 5 ↔ Wally / HA / Ring | Data | WiFi | Cloud brain, HA link, Ring cloud/report-back |

---

## 5. Open / TBD — deliberately not drawn as decided

- **Power PCB rail scope** — which candidate rails live on the board (Jim, 2026-11-14:
  "lets see where it all lands"). Servo rail is the headline; Pi rail stays off-board
  by default.
- **Hard disconnect part** — TBD; this board is its natural home.
- **#2815 mounting** — on the power PCB or off-board, TBD at layout.
- **Battery jack style** on the power PCB — panel DC5521 jack vs cut lead into screw
  terminals, TBD.
- **Servo-rail enable authority** — Pico recommended (one fault authority); not locked.
- **Regulator implementation** — XL4016-class modules vs designed-in converters, rev 1 TBD.
- **Display** — fascia height still unmeasured; the ordered 7-inch panel's fit
  re-opens after that measurement. Display Pi is resolved (second Pi 5, on hand);
  its power route in the robot is still unassigned. Data architecture is DECIDED
  (2026-11-16): ROS 2 subscriber node on wired Ethernet; MQTT reserved for the
  Home Assistant bridge only (either Pi may host it).
- **Witty Pi 5 HAT+** — candidate for true 5V/5A Pi power + managed scheduling; duty
  split with the Pico sequencer open.
- **Dock connector face** — rear/back-in (current lean) vs front/nose-in; decide before
  printing the robot-side mount. Anker dock top-up physical connection also open.
- **Arm, keeper choice** — Pavv is the test mule; RoArm-M2-S is the leading keeper if
  the two-pod head returns; xArm 1S is out for head duty. Arm-tip camera proposal
  (Gemini 2 on tip) undecided.
- **GS camera** — chosen but out of stock everywhere (daily watch running).
- **INA219 (#904)** — optional, only if Pico ADC charge-current read-back isn't clean
  enough for the DOCKED test (voltage + >100 mA for 2 s).

_Sync note: this diagram reflects decisions through 2026-11-16. When a TBD locks,
update the block here and the source note it came from in the same pass._
