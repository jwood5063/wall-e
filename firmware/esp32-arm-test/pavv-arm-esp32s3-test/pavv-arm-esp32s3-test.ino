/*
 * pavv-arm-esp32s3-test.ino
 *
 * Bench test sketch for the Pavv 6DOF robot arm (6 standard PWM hobby
 * servos + claw) driven directly by the spare ESP32-S3-WROOM.
 * No controller board needed.
 *
 * Library: "ESP32Servo" (Library Manager -> search ESP32Servo, install).
 * Board:   ESP32S3 Dev Module (Arduino-ESP32 core).
 * Serial:  115200 baud, newline line endings.
 *
 * ---------------------------------------------------------------------------
 * POWER — READ BEFORE WIRING
 * - Servos get power from a SEPARATE ~6 V supply rated for several amps.
 *   NEVER power servos from the ESP32 board's 5 V / 3.3 V pins.
 * - Servo supply GND and ESP32 GND MUST be tied together (common ground),
 *   but servo current must not flow through the ESP32 board.
 * - ESP32 stays on its own clean USB power.
 * - Power the servo rail up BEFORE running sweeps; a stalled servo of
 *   this class can pull 2-3 A, so a weak rail = brownouts and jitter
 *   that look exactly like bad code.
 * ---------------------------------------------------------------------------
 *
 * WIRING (signal wires only — one GPIO per servo)
 *   Servo 1  Base yaw      -> GPIO 4
 *   Servo 2  Shoulder      -> GPIO 5
 *   Servo 3  Elbow         -> GPIO 6
 *   Servo 4  Wrist pitch   -> GPIO 7
 *   Servo 5  Wrist roll    -> GPIO 15
 *   Servo 6  Gripper claw  -> GPIO 16
 * (Pins avoid the S3 strapping pins, the USB pins 19/20, and 26-32.)
 * If the arm's joint order differs when it arrives, only the names in
 * the table below change — the wiring and test flow stay the same.
 *
 * FIRST RUN
 * 1. Wire ONE servo at a time, unloaded, horn off if it comes off.
 *    Select it (type its number), sweep it, confirm it moves smoothly
 *    both ways with no buzzing at the ends of travel.
 * 2. Repeat for all six. Only then assemble the arm.
 * 3. The gripper is usually the weakest servo — keep it between
 *    60 and 120 degrees until you know its real travel.
 *
 * SERIAL COMMANDS
 *   1 .. 6        select a servo
 *   +  /  -       nudge selected servo +/- 5 degrees
 *   m <deg>       move selected servo to <deg> (0-180, smooth ramp)
 *   sweep         sweep the selected servo 45 -> 135 -> 90, slowly
 *   sweepall      sweep each servo in turn (the headline bench test)
 *   center        move all servos to 90, staggered so they don't all
 *                 pull current at once
 *   min <us>      set selected servo's minimum pulse (default 1000)
 *   max <us>      set selected servo's maximum pulse (default 2000)
 *   trim <deg>    set selected servo's centre trim (-20..+20 deg)
 *   save          save min/max/trim for all servos to flash (NVS)
 *   reset         clear saved calibration, restore defaults
 *   off / on      detach all servos (free movement) / re-attach
 *   info  (or ?)  print the servo table / this help
 *
 * Calibration workflow: with the servo selected, use min/max to widen
 * the pulse range in small steps until the joint just reaches its
 * mechanical ends without buzzing, use trim so 90 = true centre,
 * then `save`. Saved values load automatically at boot.
 */

#include <ESP32Servo.h>
#include <Preferences.h>

struct ServoCfg {
  const char *name;
  int pin;
  int minUs;
  int maxUs;
  int trim;   // degrees, added to every commanded angle
  int angle;  // last commanded angle (before trim)
};

static const int NUM_SERVOS = 6;
static const int DEFAULT_MIN_US = 1000;
static const int DEFAULT_MAX_US = 2000;

ServoCfg cfg[NUM_SERVOS] = {
  // name,          pin, minUs,         maxUs,         trim, angle
  { "Base yaw",      4,  DEFAULT_MIN_US, DEFAULT_MAX_US, 0,   90 },
  { "Shoulder",      5,  DEFAULT_MIN_US, DEFAULT_MAX_US, 0,   90 },
  { "Elbow",         6,  DEFAULT_MIN_US, DEFAULT_MAX_US, 0,   90 },
  { "Wrist pitch",   7,  DEFAULT_MIN_US, DEFAULT_MAX_US, 0,   90 },
  { "Wrist roll",   15,  DEFAULT_MIN_US, DEFAULT_MAX_US, 0,   90 },
  { "Gripper claw", 16,  DEFAULT_MIN_US, DEFAULT_MAX_US, 0,   90 },
};

Servo servos[NUM_SERVOS];
Preferences prefs;
int selected = 0;          // index of the currently selected servo
bool attached = false;

static int clampAngle(int a) { return a < 0 ? 0 : (a > 180 ? 180 : a); }

// Smoothly ramp a servo from its current angle to the target, ~1 deg / 15 ms.
void moveServo(int idx, int target) {
  target = clampAngle(target);
  int from = cfg[idx].angle;
  int step = (target >= from) ? 1 : -1;
  for (int a = from; ; a += step) {
    servos[idx].write(clampAngle(a + cfg[idx].trim));
    if (a == target) break;
    delay(15);
  }
  cfg[idx].angle = target;
}

void attachOne(int idx) {
  servos[idx].setPeriodHertz(50);
  servos[idx].attach(cfg[idx].pin, cfg[idx].minUs, cfg[idx].maxUs);
  servos[idx].write(clampAngle(cfg[idx].angle + cfg[idx].trim));
}

void attachAllStaggered() {
  for (int i = 0; i < NUM_SERVOS; i++) {
    attachOne(i);
    delay(300);  // one servo starts at a time — keeps inrush current sane
  }
  attached = true;
}

void detachAll() {
  for (int i = 0; i < NUM_SERVOS; i++) servos[i].detach();
  attached = false;
}

void sweepServo(int idx) {
  Serial.printf("Sweeping servo %d (%s)...\n", idx + 1, cfg[idx].name);
  moveServo(idx, 45);
  delay(300);
  moveServo(idx, 135);
  delay(300);
  moveServo(idx, 90);
  Serial.println("  done.");
}

void centerAll() {
  for (int i = 0; i < NUM_SERVOS; i++) {
    moveServo(i, 90);
    delay(250);
  }
}

void printInfo() {
  Serial.println(" idx  name           pin   minUs  maxUs  trim  angle");
  for (int i = 0; i < NUM_SERVOS; i++) {
    Serial.printf("  %d   %-14s %-5d %-6d %-6d %-5d %d%s\n",
                  i + 1, cfg[i].name, cfg[i].pin, cfg[i].minUs,
                  cfg[i].maxUs, cfg[i].trim, cfg[i].angle,
                  (i == selected) ? "   <- selected" : "");
  }
}

void printHelp() {
  Serial.println("Commands: 1-6 select | + / - nudge 5 deg | m <deg> move");
  Serial.println("  sweep | sweepall | center | min <us> | max <us>");
  Serial.println("  trim <deg> | save | reset | off | on | info");
}

void loadCalibration() {
  prefs.begin("armcal", true);
  for (int i = 0; i < NUM_SERVOS; i++) {
    char key[12];
    snprintf(key, sizeof(key), "mn%d", i);
    cfg[i].minUs = prefs.getInt(key, cfg[i].minUs);
    snprintf(key, sizeof(key), "mx%d", i);
    cfg[i].maxUs = prefs.getInt(key, cfg[i].maxUs);
    snprintf(key, sizeof(key), "tr%d", i);
    cfg[i].trim = prefs.getInt(key, cfg[i].trim);
  }
  prefs.end();
}

void saveCalibration() {
  prefs.begin("armcal", false);
  for (int i = 0; i < NUM_SERVOS; i++) {
    char key[12];
    snprintf(key, sizeof(key), "mn%d", i);
    prefs.putInt(key, cfg[i].minUs);
    snprintf(key, sizeof(key), "mx%d", i);
    prefs.putInt(key, cfg[i].maxUs);
    snprintf(key, sizeof(key), "tr%d", i);
    prefs.putInt(key, cfg[i].trim);
  }
  prefs.end();
  Serial.println("Calibration saved to flash.");
}

void resetCalibration() {
  prefs.begin("armcal", false);
  prefs.clear();
  prefs.end();
  for (int i = 0; i < NUM_SERVOS; i++) {
    cfg[i].minUs = DEFAULT_MIN_US;
    cfg[i].maxUs = DEFAULT_MAX_US;
    cfg[i].trim = 0;
    attachOne(i);
    moveServo(i, cfg[i].angle);
  }
  Serial.println("Calibration cleared; defaults restored (1000-2000 us, trim 0).");
}

// Re-attach the selected servo after a min/max change so it takes effect.
void reattachSelected() {
  servos[selected].detach();
  attachOne(selected);
}

void handleCommand(String line) {
  line.trim();
  line.toLowerCase();
  if (line.length() == 0) return;

  if (line == "?" || line == "info") { printInfo(); printHelp(); return; }
  if (line == "sweep")    { sweepServo(selected); return; }
  if (line == "sweepall") { for (int i = 0; i < NUM_SERVOS; i++) sweepServo(i); return; }
  if (line == "center")   { centerAll(); return; }
  if (line == "save")     { saveCalibration(); return; }
  if (line == "reset")    { resetCalibration(); return; }
  if (line == "off")      { detachAll(); Serial.println("Servos detached."); return; }
  if (line == "on")       { attachAllStaggered(); Serial.println("Servos attached."); return; }
  if (line == "+")        { moveServo(selected, cfg[selected].angle + 5); return; }
  if (line == "-")        { moveServo(selected, cfg[selected].angle - 5); return; }

  if (line.length() == 1 && line[0] >= '1' && line[0] <= '6') {
    selected = line[0] - '1';
    Serial.printf("Selected servo %d (%s), angle %d.\n",
                  selected + 1, cfg[selected].name, cfg[selected].angle);
    return;
  }

  // Commands with a numeric argument: "m 120", "min 600", "max 2400", "trim -5"
  int sp = line.indexOf(' ');
  if (sp > 0) {
    String cmd = line.substring(0, sp);
    int val = line.substring(sp + 1).toInt();
    if (cmd == "m") {
      moveServo(selected, val);
      Serial.printf("Servo %d -> %d deg.\n", selected + 1, cfg[selected].angle);
      return;
    }
    if (cmd == "min" && val >= 400 && val < cfg[selected].maxUs) {
      cfg[selected].minUs = val;
      reattachSelected();
      Serial.printf("Servo %d min pulse = %d us (save to keep).\n", selected + 1, val);
      return;
    }
    if (cmd == "max" && val <= 2600 && val > cfg[selected].minUs) {
      cfg[selected].maxUs = val;
      reattachSelected();
      Serial.printf("Servo %d max pulse = %d us (save to keep).\n", selected + 1, val);
      return;
    }
    if (cmd == "trim" && val >= -20 && val <= 20) {
      cfg[selected].trim = val;
      moveServo(selected, cfg[selected].angle);
      Serial.printf("Servo %d trim = %d deg (save to keep).\n", selected + 1, val);
      return;
    }
  }

  Serial.println("Unknown command — type ? for help.");
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== Pavv 6DOF arm — ESP32-S3 bench test ===");
  Serial.println("Servo power must be a SEPARATE ~6 V high-current rail,");
  Serial.println("common ground with the ESP32. Never power servos from");
  Serial.println("the ESP32 board. Test each servo unloaded, one at a time.");
  Serial.println();

  // ESP32Servo needs timers allocated before attaching.
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  loadCalibration();
  attachAllStaggered();
  Serial.println("All servos attached and centred, one at a time.");
  printInfo();
  printHelp();
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    handleCommand(line);
  }
}
