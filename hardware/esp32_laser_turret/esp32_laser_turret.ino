/*
 * ESP32-S3 / ESP32 Pan-Tilt Dual-SG90 Laser Sentry Turret
 * ========================================================
 * Universal Hardware Controller (Zero External Library Dependencies)
 * Uses native ESP32 Hardware LEDC PWM — Guaranteed compatibility with
 * ESP32-S3, ESP32, ESP32-C3, and both Arduino Core 2.x and Core 3.x.
 * 
 * =========================================================================
 * CRITICAL ARDUINO IDE SETTINGS FOR ESP32-S3:
 * =========================================================================
 * 1. Board: "ESP32S3 Dev Module"
 * 2. Tools -> USB CDC On Boot: "Enabled"   <-- (MUST BE ENABLED!)
 *    (If this is "Disabled", Serial writes will time out and servos will NOT move!)
 * 3. Tools -> USB Mode: "Hardware CDC and JTAG"
 * 4. Tools -> Upload Mode: "UART0 / Hardware CDC"
 * 5. Tools -> Port: Select your ESP32 COM port (e.g. COM5)
 * =========================================================================
 * 
 * Pinout Configuration:
 * - Pan Servo (Horizontal Yaw)  -> GPIO 13 (PWM)
 * - Tilt Servo (Vertical Pitch) -> GPIO 18 (PWM)
 * - Laser Diode Module          -> GPIO 16 (Digital Output)
 * 
 * POWER REQUIREMENTS (CRITICAL):
 * - SG90 servos require 4.8V - 6V. Do NOT connect to 3.3V pin.
 * - Connect Servo Red (VCC) to 5V (VIN if USB power is >= 2A, or external 5V 2A).
 * - Connect Servo Brown/Black (GND) to ESP32 GND (Shared Common Ground).
 * - Connect Laser VCC/Signal to GPIO 16, and GND to ESP32 GND.
 * 
 * Startup Diagnostic (Power-On Self-Test):
 * - On boot or reset, the laser will blink 3 times, then the servos will
 *   perform a physical sweep (Pan: 60° -> 120° -> 90°, Tilt: 70° -> 110° -> 90°).
 * - This gives IMMEDIATE visual confirmation that wiring and power are working!
 */

#include <Arduino.h>

#if defined(ARDUINO_USB_CDC_ON_BOOT) && !ARDUINO_USB_CDC_ON_BOOT
#warning "CRITICAL FOR ESP32-S3: Please set Tools -> 'USB CDC On Boot' to 'Enabled' in Arduino IDE!"
#endif

// --- PIN ASSIGNMENTS ---
const int PIN_SERVO_PAN  = 13; // SG90 Pan (Horizontal)
const int PIN_SERVO_TILT = 18; // SG90 Tilt (Vertical)
const int PIN_LASER      = 16; // Laser Diode Signal

// --- PWM CHANNELS & SETTINGS ---
const int CHANNEL_PAN  = 0;
const int CHANNEL_TILT = 1;
const int PWM_FREQ     = 50;  // 50 Hz standard servo frequency (20ms period)
const int PWM_RES_BITS = 14;  // 14-bit resolution: 0 to 16383

// Standard SG90 pulse range (microseconds)
const float SERVO_MIN_US = 500.0f;  // ~0 degrees
const float SERVO_MAX_US = 2400.0f; // ~180 degrees

// --- MECHANICAL LIMITS ---
const float PAN_MIN  = 10.0f;
const float PAN_MAX  = 170.0f;
const float TILT_MIN = 20.0f;
const float TILT_MAX = 160.0f;

const float HOME_PAN  = 90.0f;
const float HOME_TILT = 90.0f;

// --- SAFETY FAILSAFE ---
const unsigned long FAILSAFE_TIMEOUT_MS = 2500; // Turn off laser if PC disconnects

// --- STATE VARIABLES ---
float currentPan   = 90.0f;
float currentTilt  = 90.0f;
float targetPan    = 90.0f;
float targetTilt   = 90.0f;
bool laserActive   = false;
unsigned long lastCommandTime = 0;
unsigned long lastInterpolationTime = 0;

String inputBuffer = "";

// Check Arduino ESP32 Core Version (Core 3.0+ vs Core 2.0)
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
  #define IS_ESP32_CORE_3 1
#else
  #define IS_ESP32_CORE_3 0
#endif

void writeServoPulseUs(int pin, int channel, float pulseUs) {
    // 50Hz = 20,000 microseconds period
    // 14-bit resolution = 16383 max duty
    uint32_t duty = (uint32_t)((pulseUs / 20000.0f) * 16383.0f);
#if IS_ESP32_CORE_3
    ledcWrite(pin, duty);
#else
    ledcWrite(channel, duty);
#endif
}

void writeServoAngle(int pin, int channel, float angle) {
    angle = constrain(angle, 0.0f, 180.0f);
    float pulseUs = SERVO_MIN_US + (angle / 180.0f) * (SERVO_MAX_US - SERVO_MIN_US);
    writeServoPulseUs(pin, channel, pulseUs);
}

void setLaser(bool state) {
    laserActive = state;
    digitalWrite(PIN_LASER, laserActive ? HIGH : LOW);
}

void initHardwarePWM() {
    // Initialize Laser
    pinMode(PIN_LASER, OUTPUT);
    setLaser(false);

    // Initialize Servo PWM
#if IS_ESP32_CORE_3
    ledcAttach(PIN_SERVO_PAN, PWM_FREQ, PWM_RES_BITS);
    ledcAttach(PIN_SERVO_TILT, PWM_FREQ, PWM_RES_BITS);
#else
    ledcSetup(CHANNEL_PAN, PWM_FREQ, PWM_RES_BITS);
    ledcAttachPin(PIN_SERVO_PAN, CHANNEL_PAN);

    ledcSetup(CHANNEL_TILT, PWM_FREQ, PWM_RES_BITS);
    ledcAttachPin(PIN_SERVO_TILT, CHANNEL_TILT);
#endif

    // Move to 90 degrees center
    writeServoAngle(PIN_SERVO_PAN, CHANNEL_PAN, HOME_PAN);
    writeServoAngle(PIN_SERVO_TILT, CHANNEL_TILT, HOME_TILT);
}

void powerOnSelfTest() {
    // 1. Blink laser 3 times
    for (int i = 0; i < 3; i++) {
        setLaser(true);
        delay(120);
        setLaser(false);
        delay(120);
    }

    // 2. Physical Pan Sweep (Horizontal Yaw)
    writeServoAngle(PIN_SERVO_PAN, CHANNEL_PAN, 60.0f);
    delay(400);
    writeServoAngle(PIN_SERVO_PAN, CHANNEL_PAN, 120.0f);
    delay(400);
    writeServoAngle(PIN_SERVO_PAN, CHANNEL_PAN, HOME_PAN);
    delay(300);

    // 3. Physical Tilt Sweep (Vertical Pitch)
    writeServoAngle(PIN_SERVO_TILT, CHANNEL_TILT, 70.0f);
    delay(400);
    writeServoAngle(PIN_SERVO_TILT, CHANNEL_TILT, 110.0f);
    delay(400);
    writeServoAngle(PIN_SERVO_TILT, CHANNEL_TILT, HOME_TILT);
    delay(300);
}

void setup() {
    Serial.begin(115200);

    // Allow native USB CDC enumeration on ESP32-S3
    unsigned long cdcStart = millis();
    while (!Serial && (millis() - cdcStart < 1000)) {
        delay(10);
    }

    initHardwarePWM();

    // Run Startup Self-Test Sweep so user can immediately verify servos physically move
    powerOnSelfTest();

    currentPan  = HOME_PAN;
    currentTilt = HOME_TILT;
    targetPan   = HOME_PAN;
    targetTilt  = HOME_TILT;

    lastCommandTime = millis();
    inputBuffer.reserve(64);

    Serial.println("ESP32_TURRET_READY");
}

void processCommand(String cmd) {
    cmd.trim();
    if (cmd.length() == 0) return;

    lastCommandTime = millis(); // Refresh failsafe heartbeat

    if (cmd.equalsIgnoreCase("PING")) {
        Serial.println("PONG");
    }
    else if (cmd.equalsIgnoreCase("TEST")) {
        powerOnSelfTest();
        Serial.println("OK:TEST");
    }
    else if (cmd.equalsIgnoreCase("HOME")) {
        targetPan = HOME_PAN;
        targetTilt = HOME_TILT;
        setLaser(false);
        Serial.println("OK:HOME");
    }
    else if (cmd.startsWith("LASER,") || cmd.startsWith("LASER:")) {
        int state = cmd.substring(6).toInt();
        setLaser(state > 0);
        Serial.print("OK:LASER,");
        Serial.println(laserActive ? "1" : "0");
    }
    else if (cmd.startsWith("MOVE,") || cmd.startsWith("MOVE:")) {
        // Format: MOVE,pan,tilt or MOVE:pan,tilt
        char sep = cmd.charAt(4);
        int c1 = 4;
        int c2 = cmd.indexOf(',', c1 + 1);
        if (c2 < 0) c2 = cmd.indexOf(':', c1 + 1);
        if (c2 > 0) {
            float p = cmd.substring(c1 + 1, c2).toFloat();
            float t = cmd.substring(c2 + 1).toFloat();
            targetPan = constrain(p, PAN_MIN, PAN_MAX);
            targetTilt = constrain(t, TILT_MIN, TILT_MAX);
            Serial.print("OK:MOVE,");
            Serial.print(targetPan, 1);
            Serial.print(",");
            Serial.println(targetTilt, 1);
        }
    }
    else if (cmd.startsWith("AIM,") || cmd.startsWith("AIM:") || cmd.startsWith("SET:") || cmd.startsWith("SET,")) {
        // Format: AIM,pan,tilt,laser or SET:pan,tilt,laser
        int prefixLen = (cmd.startsWith("SET") ? 4 : 4);
        int c1 = prefixLen - 1;
        int c2 = cmd.indexOf(',', c1 + 1);
        if (c2 < 0) c2 = cmd.indexOf(':', c1 + 1);
        int c3 = (c2 > 0) ? cmd.indexOf(',', c2 + 1) : -1;
        if (c3 < 0 && c2 > 0) c3 = cmd.indexOf(':', c2 + 1);

        if (c2 > 0) {
            float p = cmd.substring(c1 + 1, c2).toFloat();
            float t = (c3 > 0) ? cmd.substring(c2 + 1, c3).toFloat() : cmd.substring(c2 + 1).toFloat();
            int l = (c3 > 0) ? cmd.substring(c3 + 1).toInt() : (laserActive ? 1 : 0);

            targetPan = constrain(p, PAN_MIN, PAN_MAX);
            targetTilt = constrain(t, TILT_MIN, TILT_MAX);
            setLaser(l > 0);

            Serial.print("OK:AIM,");
            Serial.print(targetPan, 1);
            Serial.print(",");
            Serial.print(targetTilt, 1);
            Serial.print(",");
            Serial.println(laserActive ? "1" : "0");
        }
    }
    else if (cmd.equalsIgnoreCase("STATUS")) {
        Serial.print("{\"pan\":");
        Serial.print(currentPan, 1);
        Serial.print(",\"tilt\":");
        Serial.print(currentTilt, 1);
        Serial.print(",\"laser\":");
        Serial.print(laserActive ? "true" : "false");
        Serial.print(",\"targetPan\":");
        Serial.print(targetPan, 1);
        Serial.print(",\"targetTilt\":");
        Serial.print(targetTilt, 1);
        Serial.println("}");
    }
    else {
        Serial.println("ERR:UNKNOWN_COMMAND");
    }
}

void loop() {
    // 1. Read Serial Commands from USB
    while (Serial.available() > 0) {
        char c = (char)Serial.read();
        if (c == '\n' || c == '\r') {
            if (inputBuffer.length() > 0) {
                processCommand(inputBuffer);
                inputBuffer = "";
            }
        } else {
            if (inputBuffer.length() < 64) {
                inputBuffer += c;
            }
        }
    }

    // 2. Hardware Failsafe (Eye Safety)
    if (laserActive && (millis() - lastCommandTime > FAILSAFE_TIMEOUT_MS)) {
        setLaser(false);
        Serial.println("WARN:FAILSAFE_LASER_OFF");
    }

    // 3. Smooth Motion Interpolation (Damps sudden servo jerks)
    unsigned long now = millis();
    if (now - lastInterpolationTime >= 15) { // 66 Hz step
        lastInterpolationTime = now;

        float panDiff = targetPan - currentPan;
        float tiltDiff = targetTilt - currentTilt;

        const float MAX_STEP = 3.0f; // Max degrees per 15ms

        if (abs(panDiff) > 0.2f) {
            float step = constrain(panDiff * 0.40f, -MAX_STEP, MAX_STEP);
            currentPan += step;
            writeServoAngle(PIN_SERVO_PAN, CHANNEL_PAN, currentPan);
        } else {
            currentPan = targetPan;
            writeServoAngle(PIN_SERVO_PAN, CHANNEL_PAN, currentPan);
        }

        if (abs(tiltDiff) > 0.2f) {
            float step = constrain(tiltDiff * 0.40f, -MAX_STEP, MAX_STEP);
            currentTilt += step;
            writeServoAngle(PIN_SERVO_TILT, CHANNEL_TILT, currentTilt);
        } else {
            currentTilt = targetTilt;
            writeServoAngle(PIN_SERVO_TILT, CHANNEL_TILT, currentTilt);
        }
    }
}
