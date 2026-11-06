"""The CATR interface is an interface to the Keysight CATR positioner, which is
controlled through the SCPI interface of the OTA Chamber Control Software
(PAVE). The software must be running with the positioner already selected under
Setup -> Equipment Selection.
"""

import time

import pyvisa


class CatrInterface:
    """Interface to the Keysight CATR roll-over-azimuth positioner.

    The SCPI move commands are non-blocking, so this class polls the operation
    status register to determine when a move has completed.
    """

    # Default timeout in milliseconds.
    DEFAULT_TIMEOUT_MS = 200000

    # Maximum time in seconds to wait for a move to complete.
    MOVE_TIMEOUT = 300

    # Interval in seconds between polls of the status register.
    POLL_INTERVAL = 0.25

    # Bit of STATus:OPERation:CONDition? that is set while the positioner moves.
    MOVING_BITMASK = 4

    def __init__(
        self,
        visa_address: str = "TCPIP0::127.0.0.1::hislip200::INSTR",
    ) -> None:
        self._instrument = pyvisa.ResourceManager().open_resource(
            visa_address,
            timeout=self.DEFAULT_TIMEOUT_MS,
            write_termination="\n",
            read_termination="\n",
        )

    def move_to(self, azimuth: float, roll: float) -> None:
        """Moves the positioner to the azimuth and roll and waits for the move.

        The angles are relative to the zero position.

        Args:
            azimuth: Azimuth angle in degrees.
            roll: Roll angle in degrees.

        Raises:
            TimeoutError: If the move does not complete in time.
            RuntimeError: If the control software reports an error.
        """
        self._instrument.write(f"POS:MOVE:AZIM {azimuth};ROLL {roll}")
        self._instrument.write("POS:MOVE:INIT")

        deadline = time.monotonic() + self.MOVE_TIMEOUT
        time.sleep(self.POLL_INTERVAL)
        while self._is_moving():
            if time.monotonic() > deadline:
                raise TimeoutError("CATR positioner did not stop moving.")
            time.sleep(self.POLL_INTERVAL)
        self._check_errors()

    def set_zero(self) -> None:
        """Sets the current position as the zero position.

        Raises:
            RuntimeError: If the control software reports an error.
        """
        self._instrument.write("POS:ZERO:RES")
        self._check_errors()

    def _is_moving(self) -> bool:
        """Returns whether the positioner is moving.

        Returns:
            Whether the positioner is moving.
        """
        status = int(self._instrument.query("STAT:OPER:COND?"))
        return bool(status & self.MOVING_BITMASK)

    def _check_errors(self) -> None:
        """Raises if the SCPI error queue contains an error.

        Raises:
            RuntimeError: If the control software reports an error.
        """
        error = self._instrument.query("SYST:ERR?")
        if not error.startswith("0,"):
            raise RuntimeError(f"CATR reported an error: {error}")
