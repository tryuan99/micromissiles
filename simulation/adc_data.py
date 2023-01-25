"""The ADC data class represents the ADC samples of the IF signal received by a
radar's RX antennas corresponding to a single radar target reflecting a chirp
from all transmitting TX antennas.
"""

import numpy as np

from simulation.radar import Radar
from simulation.samples import Samples
from simulation.target import Target
from utils import constants


class AdcData(Samples):
    """Represents the ADC samples of the IF signal received at all RX antennas."""

    def __init__(self, radar: Radar, target: Target):
        super().__init__(self.generate_adc_data_3d(radar, target))

    @staticmethod
    def generate_adc_data_3d(radar: Radar, target: Target) -> np.ndarray:
        """Generates the ADC samples for all RX antennas.

        Args:
            radar: Radar.
            target: Target.

        Returns:
            3-dimensional ADC samples for all RX antennas with dimensions
            (number of RX antennas) x (number of chirps) x (number of ADC
            samples).
        """
        # TODO(titan): Add MIMO.
        return np.array([
            np.sum(
                [
                    AdcData.generate_adc_data_2d(radar, target, tx_antenna,
                                                 rx_antenna)
                    for tx_antenna in range(radar.N_tx)
                ],
                axis=0,
            )
            for rx_antenna in range(radar.N_rx)
        ])

    @staticmethod
    def generate_adc_data_2d(radar: Radar, target: Target, tx_antenna: int,
                             rx_antenna: int) -> np.ndarray:
        """Generates the ADC samples for the given TX and RX antennas.

        Args:
            radar: Radar.
            target: Target.
            tx_antenna: TX antenna index.
            rx_antenna: RX antenna index.

        Returns:
            2-dimensional ADC samples for the given TX and RX antennas with
            dimensions (number of chirps) x (number of ADC samples).
        """
        x, y, z = target.get_position_over_time(radar.t_axis)
        d_tx = np.sqrt((x - radar.d_tx_hor[tx_antenna] * radar.lambdac / 2)**2 +
                       (y - radar.d_tx_ver[tx_antenna] * radar.lambdac / 2)**2 +
                       z**2)  # Distance to the TX antenna at each sample in m.
        d_rx = np.sqrt((x - radar.d_rx_hor[rx_antenna] * radar.lambdac / 2)**2 +
                       (y - radar.d_rx_ver[rx_antenna] * radar.lambdac / 2)**2 +
                       z**2)  # Distance to the RX antenna at each sample in m.

        tau = (d_tx +
               d_rx) / radar.c  # Return time-of-flight for each sample in s.
        f_sig = radar.mu * tau  # IF of each sample.
        phi_sig = radar.f0 * tau - radar.mu / 2 * tau**2  # IF phase of each sample.
        return AdcData.get_if_amplitude(radar, target) * np.exp(
            1j * 2 * np.pi * (f_sig * radar.t_axis_chirp + phi_sig))

    @staticmethod
    def get_if_amplitude(radar: Radar, target: Target) -> float:
        """Returns the IF amplitude considering the path loss and the target's RCS.

        Args:
            radar: Radar.
            target: Target.
        """
        # Calculate the IF amplitude using the radar equation.
        power_db = (
            radar.tx_eirp + constants.power2db(1e-3)  # Convert from dBm to dBW.
            + radar.rx_gain + target.rcs +
            constants.power2db(radar.lambdac**2 /
                               ((4 * np.pi)**3 * target.range**4)))
        return constants.power2mag(constants.db2power(power_db))
