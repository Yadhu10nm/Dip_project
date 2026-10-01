import time
import threading
from typing import Optional, List, Tuple
import serial
import serial.tools.list_ports
from skills.turret_skill.implementation.types import TurretStatus


class TurretController:
    """
    Hardware Controller communicating with ESP32 over USB Serial.
    Handles auto-discovery, thread-safe command sending, rate-limiting,
    and automatic fallback to Simulation/Mock mode if hardware is disconnected.
    """

    def __init__(self, port: str = "AUTO", baudrate: int = 115200, timeout: float = 0.5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self.ser: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_mock = True
        self._lock = threading.Lock()
        self._consecutive_write_errors = 0

        # Telemetry
        self.status = TurretStatus()
        self.last_sent_time = 0.0
        self.min_command_interval = 0.035  # ~28 Hz max rate to prevent serial saturation
        self._last_sent_cmd: Optional[str] = None

    def connect(self, target_port: Optional[str] = None) -> bool:
        """
        Attempts to connect to ESP32 on specified port or auto-discovers device.
        Falls back to Mock mode if unavailable.
        """
        with self._lock:
            if target_port:
                self.port = target_port

            # Close previous connection if any
            self._close_serial()
            self._consecutive_write_errors = 0

            resolved_port = self._resolve_port(self.port)

            if resolved_port:
                try:
                    self.ser = serial.Serial(
                        port=resolved_port,
                        baudrate=self.baudrate,
                        timeout=self.timeout,
                        write_timeout=2.0,
                    )
                    try:
                        self.ser.dtr = True
                        self.ser.rts = True
                    except Exception:
                        pass

                    time.sleep(0.8)  # Allow ESP32 bootloader / USB reset to settle
                    try:
                        self.ser.reset_input_buffer()
                        self.ser.reset_output_buffer()
                        self.ser.write(b"PING\n")
                    except Exception:
                        pass

                    self.is_connected = True
                    self.is_mock = False
                    self.status.connected = True
                    self.status.is_mock = False
                    self.status.port = resolved_port
                    self.status.last_error = None
                    print(f"[TurretController] Successfully connected to ESP32 on {resolved_port} @ {self.baudrate} baud.")
                    return True
                except Exception as e:
                    print(f"[TurretController] Failed to connect to {resolved_port}: {e}. Switching to SIMULATION.")


            # Fallback to Mock
            self.is_connected = False
            self.is_mock = True
            self.status.connected = False
            self.status.is_mock = True
            self.status.port = "SIMULATION (No Hardware)"
            self.status.last_error = "Hardware not detected on USB serial"
            print("[TurretController] Running in SIMULATION mode. Virtual servos active.")
            return False

    def _resolve_port(self, requested_port: str) -> Optional[str]:
        """Auto-discovers ESP32 COM port or returns requested port."""
        available_ports = list(serial.tools.list_ports.comports())
        if not available_ports:
            return None

        if requested_port and requested_port.upper() != "AUTO":
            # Check if requested port exists
            for p in available_ports:
                if p.device.upper() == requested_port.upper():
                    return p.device
            return requested_port

        # Auto-detect priority: Look for known ESP32 USB-UART chipsets
        # Silicon Labs CP210x, WCH CH340, FTDI, or devices with "ESP" or "Serial"
        for p in available_ports:
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").lower()
            if any(k in desc or k in hwid for k in ["303a", "espressif", "cp210", "ch340", "ch341", "ftdi", "uart", "esp32", "usb-serial", "usb serial"]):
                return p.device


        # If no specific match, try the first available COM port
        return available_ports[0].device

    def list_available_ports(self) -> List[dict]:
        """Lists all detected COM ports on system."""
        ports = []
        for p in serial.tools.list_ports.comports():
            ports.append({
                "device": p.device,
                "description": p.description,
                "hwid": p.hwid,
            })
        return ports

    def send_aim(self, pan: float, tilt: float, laser: bool) -> bool:
        """
        Sends AIM command to ESP32: AIM,<pan>,<tilt>,<laser>
        """
        pan = max(0.0, min(180.0, float(pan)))
        tilt = max(0.0, min(180.0, float(tilt)))
        laser_int = 1 if laser else 0

        cmd = f"AIM,{pan:.1f},{tilt:.1f},{laser_int}\n"

        # Rate-limiting: suppress identical rapid redundant commands
        now = time.time()
        if cmd == self._last_sent_cmd and (now - self.last_sent_time) < 0.2:
            return True

        if (now - self.last_sent_time) < self.min_command_interval:
            return False

        with self._lock:
            self.status.pan = pan
            self.status.tilt = tilt
            self.status.target_pan = pan
            self.status.target_tilt = tilt
            self.status.laser = laser
            self.status.last_command_time = now

            if not self.is_mock and self.ser and self.ser.is_open:
                try:
                    self.ser.write(cmd.encode("ascii"))
                    self.last_sent_time = now
                    self._last_sent_cmd = cmd
                    self._consecutive_write_errors = 0
                    return True
                except Exception as e:
                    self.status.last_error = str(e)
                    self._consecutive_write_errors += 1
                    if self._consecutive_write_errors >= 4:
                        self.is_connected = False
                        self.status.connected = False
                    return False
            else:
                # Mock mode updates virtual state
                self.last_sent_time = now
                self._last_sent_cmd = cmd
                return True

    def send_laser(self, laser_state: bool) -> bool:
        """Turns laser ON or OFF."""
        with self._lock:
            self.status.laser = laser_state
            cmd = f"LASER,{1 if laser_state else 0}\n"
            if not self.is_mock and self.ser and self.ser.is_open:
                try:
                    self.ser.write(cmd.encode("ascii"))
                    self._consecutive_write_errors = 0
                    return True
                except Exception as e:
                    self.status.last_error = str(e)
                    self._consecutive_write_errors += 1
                    if self._consecutive_write_errors >= 4:
                        self.is_connected = False
                        self.status.connected = False
                    return False
            return True

    def send_home(self) -> bool:
        """Returns servos to center 90, 90 and shuts off laser."""
        return self.send_aim(90.0, 90.0, False)

    def ping(self) -> bool:
        """Pings ESP32 to verify active handshake."""
        with self._lock:
            if not self.is_mock and self.ser and self.ser.is_open:
                try:
                    self.ser.write(b"PING\n")
                    time.sleep(0.05)
                    resp = self.ser.read_all().decode("utf-8", errors="ignore")
                    return "PONG" in resp
                except Exception:
                    return False
            return True

    def _close_serial(self):
        if self.ser:
            try:
                # Safety: turn off laser before disconnect
                try:
                    self.ser.write(b"AIM,90,90,0\n")
                    self.ser.write(b"LASER,0\n")
                except Exception:
                    pass
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def close(self):
        """Safely stops hardware and releases serial port."""
        with self._lock:
            self._close_serial()
            self.is_connected = False
            self.status.connected = False
            self.status.laser = False
