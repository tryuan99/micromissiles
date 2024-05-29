"""The serial interface is used to write data to and read data from a serial
port.

For a given baudrate, the packet size and the open timeout are dongle-
dependent. For an Anker USB-C dongle, the serial packet size cannot exceed 32
bytes, and a serial open timeout of 2 seconds is required. For an Apple USB-C
dongle, the serial packet size cannot exceed 96 bytes, and no serial open
timeout is needed.
"""

import time

import serial
from absl import logging

# The maximum size in bytes of each packet to be written to the serial port.
# This value is dongle-dependent.
SERIAL_PACKET_SIZE = 32

# The timeout between consecutive packet writes.
SERIAL_PACKET_WRITE_TIMEOUT = 0.005  # seconds

# The timeout in seconds after opening the serial port.
# This value is dongle-dependent.
SERIAL_OPEN_TIMEOUT = 2  # seconds

# The timeout in seconds for a read from the serial port.
SERIAL_READ_TIMEOUT = 5  # seconds

# The timeout in seconds for a write to the serial port.
SERIAL_WRITE_TIMEOUT = 2  # seconds


class SerialInterface:
    """Interface to a serial port.

    Attributes:
        port: Serial port.
        serial: Serial interface.
        verbose: If true, log verbose messages.
    """

    def __init__(
        self,
        port: str,
        baudrate: int,
        timeout: float = SERIAL_READ_TIMEOUT,
        write_timeout: float = SERIAL_WRITE_TIMEOUT,
        verbose: bool = False,
        **kwargs,
    ) -> None:
        # Open the serial port.
        self.port = port
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            write_timeout=write_timeout,
            **kwargs,
        )
        time.sleep(SERIAL_OPEN_TIMEOUT)

        self.verbose = verbose

    def write(self, data: bytes) -> None:
        """Writes the data to the serial port.

        Args:
            data: Data to be written to the serial port.
        """
        if len(data) <= 0:
            return
        num_bytes_written = 0
        while num_bytes_written < len(data):
            num_bytes_to_write = min(SERIAL_PACKET_SIZE,
                                     len(data) - num_bytes_written)
            num_bytes_sent = self.serial.write(
                data[num_bytes_written:num_bytes_written + num_bytes_to_write])
            if self.verbose:
                logging.info("Wrote %d bytes to %s.", num_bytes_sent, self.port)
            num_bytes_written += num_bytes_sent
            time.sleep(SERIAL_PACKET_WRITE_TIMEOUT)

    def read(self, num_bytes: int = None) -> bytes:
        """Reads the data from the serial port.

        Args:
            num_bytes: Number of bytes to read. If None, reads until the next newline.

        Returns:
            The data that has been read.
        """
        read_data = self.serial.read_until(size=num_bytes)
        if self.verbose:
            logging.info("Read %d bytes from %s.", len(read_data), self.port)
        return read_data
