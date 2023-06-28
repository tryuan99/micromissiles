import numpy as np
from absl.testing import absltest

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.radar import Radar
from simulation.radar.components.target import Target
from utils import constants


class AdcDataTestCase(absltest.TestCase):

    radar = Radar()
    rnge = 15
    target = Target(rnge=rnge)

    def test_get_if_amplitude(self):
        self.assertAlmostEqual(
            AdcData.get_if_amplitude(self.radar, self.target),
            constants.power2mag(
                constants.db2power(self.radar.tx_eirp +
                                   constants.power2db(1e-3) +
                                   self.radar.rx_gain + self.target.rcs) *
                self.radar.lambdac**2 /
                ((4 * np.pi)**3 * self.target.range**4)))

    def test_get_if_amplitude_double_range(self):
        target_at_double_range = Target(rnge=2 * self.rnge)
        self.assertAlmostEqual(
            AdcData.get_if_amplitude(self.radar, target_at_double_range) *
            np.sqrt(2**4), AdcData.get_if_amplitude(self.radar, self.target))


if __name__ == "__main__":
    absltest.main()
