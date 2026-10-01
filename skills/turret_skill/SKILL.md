---
name: turret_skill
description: "ESP32 Dual-SG90 Pan-Tilt Laser Sentry Turret & Interactive Calibration Skill."
version: "1.0.0"
category: "hardware_robotics"
---

# Turret Skill (ESP32 SG90 Laser Sentry)

## Overview
Coordinates an automated 2-axis (Pan/Tilt) robotic turret powered by an **ESP32 microcontroller**, two **SG90 9g micro-servos**, and a **red laser diode module**. Integrates directly with the AI CCTV surveillance engine:
- Filters incoming facial recognition candidate detections strictly for **unauthorized intruders** / unknown individuals.
- Computes target face centroid in camera pixel coordinates.
- Maps pixel coordinates to physical servo angles using calibrated Field-of-View (FOV) transformation.
- Automatically drives servos and **fires the laser** towards the unknown person.
- Extensively supports **interactive calibration**: center alignment, range bounding, axis inversion, and click-to-aim validation.

---

## Hardware Architecture
* **Controller**: ESP32 (WROOM-32 / DevKit V1)
* **Servos**: 2x TowerPro SG90 (Pan: GPIO 13, Tilt: GPIO 18)
* **Laser**: 5V/3.3V Diode (Signal: GPIO 16)

* **Baudrate**: 115200 bps
* **Power**: Dedicated 5V 2A power supply with common ground.

---

## Software Interfaces
- `TurretSkill`: Master class orchestrating controller, calibration, and tracking.
- `TurretCalibrationManager`: Manages camera-to-servo geometric calibration stored in `data/turret_calibration.json`.
- `TurretTracker`: Threat prioritization, exponential motion smoothing, deadband hysteresis, and automated laser triggering.
- `TurretController`: Thread-safe serial communicator with auto-discovery and graceful Mock/Simulation fallback.
