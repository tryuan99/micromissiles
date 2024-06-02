"""The TI radar data handler defines the interface for handling data received
from the radar.
"""

from abc import ABC, abstractmethod


class TiRadarDataHandler(ABC):
    """Interface for a radar data handler.

    The radar data handler handles data received from the config port or from
    the data port.
    """

    @abstractmethod
    def receive_data(self, data: bytes) -> None:
        """Receives data from the radar.

        Args:
            data: Received data. The data is guaranteed to have a non-zero
              length.
        """
