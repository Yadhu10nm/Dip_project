"""
ESP32 Laser Turret — Hardware Self-Test & Diagnostic Script
===========================================================
Tests USB Serial communication, SG90 servo motion, and laser firing.

Usage:
    python skills/turret_skill/examples/test_turret_hardware.py
    python skills/turret_skill/examples/test_turret_hardware.py --port COM3
"""

import sys
import os
import time
import argparse

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from skills.turret_skill.implementation import TurretSkill


def main():
    parser = argparse.ArgumentParser(description="Test ESP32 SG90 Laser Sentry Turret Hardware")
    parser.add_argument("--port", default=None, help="Serial COM port (default: auto-detect)")
    parser.add_argument("--baud", type=int, default=115200, help="Baudrate (default: 115200)")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  ESP32 DUAL-SG90 & LASER SENTRY TURRET — HARDWARE TEST")
    print("=" * 60)

    turret = TurretSkill(port=args.port, baudrate=args.baud, auto_connect=True)
    status = turret.get_status()

    print(f"[*] Port Selected: {status.get('port')}")
    print(f"[*] Hardware Status: {'CONNECTED' if status.get('connected') else 'SIMULATION / NOT DETECTED'}")

    if not status.get("connected"):
        print("\n[!] Notice: No physical ESP32 detected. If plugged in, check:")
        print("    1. USB data cable (ensure it supports data, not charging-only).")
        print("    2. CP210x / CH340 USB drivers installed on Windows.")
        print("    3. ESP32 firmware uploaded from hardware/esp32_laser_turret.ino")
        print("\nTesting simulation motion...")

    print("\n--- TEST 1: Centering Turret (90°, 90°) ---")
    turret.manual_move(90.0, 90.0, laser=False)
    time.sleep(1.0)
    print("-> Centered.")

    print("\n--- TEST 2: Pan Sweep (Horizontal Yaw) ---")
    print("  Moving Pan to 60°...")
    turret.manual_move(60.0, 90.0, laser=False)
    time.sleep(1.2)
    print("  Moving Pan to 120°...")
    turret.manual_move(120.0, 90.0, laser=False)
    time.sleep(1.2)
    print("  Returning Pan to 90°...")
    turret.manual_move(90.0, 90.0, laser=False)
    time.sleep(0.8)

    print("\n--- TEST 3: Tilt Sweep (Vertical Pitch) ---")
    print("  Moving Tilt to 70° (Up)...")
    turret.manual_move(90.0, 70.0, laser=False)
    time.sleep(1.2)
    print("  Moving Tilt to 110° (Down)...")
    turret.manual_move(90.0, 110.0, laser=False)
    time.sleep(1.2)
    print("  Returning Tilt to 90°...")
    turret.manual_move(90.0, 90.0, laser=False)
    time.sleep(0.8)

    print("\n--- TEST 4: Laser Diode Pulse ---")
    print("  [!] WARNING: Do NOT look directly into laser beam.")
    print("  Firing laser for 2 seconds...")
    turret.manual_move(90.0, 90.0, laser=True)
    time.sleep(2.0)
    turret.manual_move(90.0, 90.0, laser=False)
    print("-> Laser turned OFF.")

    turret.stop()
    print("\n" + "=" * 60)
    print("  [OK] TURRET HARDWARE SELF-TEST COMPLETE!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
