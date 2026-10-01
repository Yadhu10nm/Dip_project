# ESP32 Dual SG90 Laser Turret Hardware Setup Guide

## 1. Components
* **ESP32 Development Board** (NodeMCU-32S, ESP32-WROOM-32, or similar)
* **2x TowerPro SG90 9g Micro Servos**
  * Servo 1: **PAN** (Horizontal Yaw rotation)
  * Servo 2: **TILT** (Vertical Pitch rotation)
* **1x Laser Diode Module** (5V / 3.3V red dot laser module, e.g. KY-008)
* **5V Power Supply** (5V 2A USB power adapter or battery pack recommended)
* Jumper wires & mini breadboard

---

## 2. Wiring Connections

```text
+-------------------+--------------------+----------------------------+
| Component         | Wire / Pin         | ESP32 / Power Connection   |
+-------------------+--------------------+----------------------------+
| SG90 Pan Servo    | Brown / Black      | GND (Common Ground)        |
|                   | Red                | 5V (External PSU or VIN)   |
|                   | Orange / Yellow    | GPIO 13 (PWM)              |
+-------------------+--------------------+----------------------------+
| SG90 Tilt Servo   | Brown / Black      | GND (Common Ground)        |
|                   | Red                | 5V (External PSU or VIN)   |
|                   | Orange / Yellow    | GPIO 18 (PWM)              |
+-------------------+--------------------+----------------------------+
| Laser Module      | GND (-)            | ESP32 GND                  |
|                   | Signal (S) / VCC   | GPIO 16                    |
+-------------------+--------------------+----------------------------+
| External 5V PSU   | GND (-)            | ESP32 GND (MANDATORY!)     |
| (If using ext)    | 5V (+)             | Servo Red Wires Only       |
+-------------------+--------------------+----------------------------+
```

> **CRITICAL POWER WARNING**:
> SG90 servos can draw peak stall currents of 500mA–1A each. Powering them from the ESP32's **3.3V** pin will cause severe brownouts, ESP32 boot loops, and servo jitter.
> Always connect servo power to **5V (VIN or external 5V 2A)** and ensure **Common Ground (GND)** is connected between the ESP32, power supply, and servos!

---

## 3. Flashing Firmware to ESP32

1. Open **Arduino IDE**.
2. Go to **Tools -> Manage Libraries...**, search for **`ESP32Servo`** by *Kevin Harrington*, and click **Install**.
3. Under **Tools -> Board**, select **ESP32 Dev Module** (or your specific ESP32 board).
4. Under **Tools -> Port**, select the COM port of your plugged-in ESP32 (e.g. `COM3`, `COM4`, etc.).
5. Open `hardware/esp32_laser_turret.ino` and click **Upload** (Ctrl + U).
6. Once uploaded, open **Serial Monitor** at **115200 baud**. You will see:
   ```
   ESP32_TURRET_READY
   ```
7. Type `PING` and press Enter — it should respond with `PONG`.
8. Type `AIM,90,90,1` — the servos will center and the laser will turn on!
