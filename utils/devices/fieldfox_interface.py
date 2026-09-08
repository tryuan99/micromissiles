"""The FieldFox interface is an interface to the Keysight FieldFox N9918B vector
network analyzer.
"""

import socket
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO


class FieldFoxOutputFormat(StrEnum):
    """FieldFox output format enumeration."""
    CSV = "FDAT"
    SNP = "SNP"
    PNG = "IMAG"


class FieldFoxInterface:
    """Interface to the Keysight FieldFox N9918B VNA.

    The VNA's IP address defaults to 192.168.1.1, so the Ethernet port must be
    configured to 192.168.1.2 with a subnet of 255.255.0.0.

    Attributes:
        ip_address: IP address of the VNA.
        port: Socket port of the VNA.
    """

    # Default timeout in seconds. File creation and transfer can take long.
    DEFAULT_TIMEOUT = 30

    def __init__(self,
                 ip_address: str = "192.168.1.1",
                 port: int = 5025) -> None:
        self.ip_address = ip_address
        self.port = port

    def capture_csv(self, output_file: str | Path) -> None:
        """Captures the data to a CSV file.

        Args:
            output_file: Output file.
        """
        output_path = Path(output_file)
        payload = self._capture_data(FieldFoxOutputFormat.CSV, output_path.name)
        self._save_data(payload, output_path)

    def capture_sp(self, output_file: str | Path) -> None:
        """Captures the S-parameters to a Touchstone file.

        The suffix ".s1p" or ".s2p" of the output file determines the number of
        ports.

        Args:
            output_file: Output file.
        """
        output_path = Path(output_file)
        payload = self._capture_data(FieldFoxOutputFormat.SNP, output_path.name)
        self._save_data(payload, output_path)

    def capture_png(self, output_file: str | Path) -> None:
        """Captures the screen to a PNG file.

        Args:
            output_file: Output file.
        """
        output_path = Path(output_file)
        payload = self._capture_data(FieldFoxOutputFormat.PNG, output_path.name)
        self._save_data(payload, output_path)

    def _capture_data(
        self,
        output_format: FieldFoxOutputFormat,
        output_file: str | Path,
    ) -> bytes:
        """Captures the data.

        Args:
            output_format: Output format.
            output_file: Output file.
        """
        with socket.create_connection(
            (self.ip_address, self.port),
                timeout=self.DEFAULT_TIMEOUT,
        ) as connection:
            with connection.makefile("rb") as reader:
                self._send_command(connection, "*CLS")
                self._send_command(connection, ":FORM:DATA ASC")

                # Store the data and wait for the operation to complete.
                self._send_command(
                    connection,
                    f':MMEM:STOR:{output_format.value} "{output_file}"')
                if self._read_command(connection, reader, "*OPC?") != "1":
                    raise RuntimeError("FieldFox failed to save the data.")

                # Download the binary data.
                self._send_command(connection, f':MMEM:DATA? "{output_file}"')
                if self._read_data(reader, num_bytes=1) != b"#":
                    raise RuntimeError(
                        f"FieldFox returned an invalid binary block.")

                num_digits_str = self._read_data(reader, num_bytes=1)
                if not num_digits_str.isdigit() or num_digits_str == b"0":
                    raise RuntimeError(
                        "FieldFox returned an unsupported binary header.")
                num_digits = int(num_digits_str)

                payload_size = int(
                    self._read_data(reader,
                                    num_bytes=num_digits).decode("ascii"))
                payload = self._read_data(reader, payload_size)

                # The FieldFox terminates the response with LF or CRLF, so flush it.
                if self._read_data(reader, num_bytes=1) == b"\r":
                    self._read_data(reader, num_bytes=1)

                # Delete the temporary data file.
                self._send_command(connection, f':MMEM:DEL "{output_file}"')

                return payload

    @staticmethod
    def _save_data(payload: bytes, output_file: str | Path) -> None:
        """Saves the data.

        Args:
            payload: Binary payload.
            output_file: Output file.
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(payload)

    @staticmethod
    def _send_command(connection: socket.socket, command: str) -> None:
        """Sends the command through the socket.

        Args:
            connection: Socket.
            command: Command to send.
        """
        connection.sendall(f"{command}\n".encode("ascii"))

    @staticmethod
    def _read_command(connection: socket.socket, reader: BinaryIO,
                      command: str) -> str:
        """Reads the command from the socket.

        Args:
            connection: Socket.
            reader: Binary IO.
            command: Command to send.

        Returns:
            The decoded response as a string.
        """
        FieldFoxInterface._send_command(connection, command)
        response = reader.readline()
        if not response:
            raise ConnectionError(f"FieldFox did not respond to {command}.")
        return response.decode("ascii").strip()

    @staticmethod
    def _read_data(reader: BinaryIO, num_bytes: int) -> bytes:
        """Reads the specified number of bytes.

        Args:
            reader: Binary IO.
            num_bytes: Number of bytes to read.

        Returns:
            The read bytes.
        """
        data = bytearray()
        while len(data) < num_bytes:
            chunk = reader.read(num_bytes - len(data))
            if not chunk:
                raise ConnectionError(
                    "FieldFox closed the connection during a transfer.")
            data.extend(chunk)
        return bytes(data)
