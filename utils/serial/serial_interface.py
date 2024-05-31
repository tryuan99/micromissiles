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
        read_terminator: bytes = b"\n",
        write_terminator: bytes = b"",
        read_timeout: float = SERIAL_READ_TIMEOUT,
        write_timeout: float = SERIAL_WRITE_TIMEOUT,
        verbose: bool = False,
        **kwargs,
    ) -> None:
        # Open the serial port.
        self.port = port
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=read_timeout,
            write_timeout=write_timeout,
            **kwargs,
        )
        time.sleep(SERIAL_OPEN_TIMEOUT)

        self.read_terminator = read_terminator
        self.write_terminator = write_terminator
        self.verbose = verbose

    @property
    def num_bytes_in_waiting(self) -> int:
        """Returns the number of bytes in the input buffer."""
        return self.serial.in_waiting

    @property
    def num_bytes_out_waiting(self) -> int:
        """Returns the number of bytes in the output buffer."""
        return self.serial.out_waiting

    def write(self, data: bytes) -> None:
        """Writes the data to the serial port.

        Args:
            data: Data to be written to the serial port.
        """
        if len(data) <= 0:
            return
        write_data = data + self.write_terminator
        num_bytes_written = 0
        while num_bytes_written < len(write_data):
            num_bytes_to_write = min(SERIAL_PACKET_SIZE,
                                     len(write_data) - num_bytes_written)
            num_bytes_sent = self.serial.write(
                write_data[num_bytes_written:num_bytes_written +
                           num_bytes_to_write])
            if self.verbose:
                logging.info("Wrote %d bytes to %s.", num_bytes_sent, self.port)
            num_bytes_written += num_bytes_sent
            time.sleep(SERIAL_PACKET_WRITE_TIMEOUT)

    def read(self, num_bytes: int = None, terminator: str = None) -> bytes:
        """Reads the data from the serial port until the read terminator, the
        number of bytes has been read, or timeout occurs.

        Args:
            num_bytes: Maximum number of bytes to read.
            terminator: Read terminator override.

        Returns:
            The data that has been read.
        """
        if terminator is None:
            terminator = self.read_terminator
        read_data = self.serial.read_until(expected=terminator, size=num_bytes)
        if self.verbose:
            logging.info("Read %d bytes from %s.", len(read_data), self.port)
        return read_data

    def read_all(self) -> bytes:
        """Reads all data from the serial port."""
        return self.serial.read_all()
