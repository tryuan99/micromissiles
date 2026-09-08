"""The S-parameter viewer visualizes the S-parameters of an N-port network."""

import numpy as np
import skrf as rf


class SParamViewer:
    """S-parameter viewer."""

    def __init__(self, file: str) -> None:
        self.network = rf.Network(file)

    def frequency(self) -> np.ndarray:
        """Frequency axis in Hz."""
        return self.network.f

    def s(self, i: int, j: int) -> np.ndarray:
        """Sij parameters."""
        return self.network.s[:, self._port_to_index(i), self._port_to_index(j)]

    def y(self, i: int, j: int) -> np.ndarray:
        """Sij parameters."""
        return self.network.y[:, self._port_to_index(i), self._port_to_index(j)]

    def z(self, i: int, j: int) -> np.ndarray:
        """Zij parameters."""
        return self.network.z[:, self._port_to_index(i), self._port_to_index(j)]

    @staticmethod
    def _port_to_index(port: int) -> int:
        """Converts the port to the index."""
        return port - 1
