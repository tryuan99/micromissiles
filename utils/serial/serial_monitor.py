"""The serial monitor monitors a serial port and logs all data received by the
serial port.
"""

from absl import logging

from utils.serial.serial_interface import SerialInterface


class SerialMonitor:
    """Serial monitor to log data received by the serial port."""

    def __init__(self, port: str, baudrate: int) -> None:
        # Open the serial port.
        self.serial = SerialInterface(port, baudrate)

    def run(self) -> None:
        """Logs data received by the serial port."""
        while True:
            read_data = self.serial.read()
            try:
                logging.info(read_data.decode().strip())
            except:
                logging.info(read_data)
