import numpy as np
from absl.testing import absltest

from simulation.antenna.antenna_factory import AntennaFactory
from simulation.antenna.dipole_antenna import DipoleAntenna
from simulation.antenna.horn_antenna import HornAntenna
from simulation.antenna.isotropic_antenna import IsotropicAntenna
from simulation.antenna.patch_antenna import PatchAntenna
from simulation.antenna.proto.antenna_config_pb2 import AntennaConfig
from simulation.antenna.radiation_pattern import RadiationPattern


class AntennaFactoryTestCase(absltest.TestCase):

    def test_create_default(self):
        antenna_config = AntennaConfig()
        antenna = AntennaFactory.create_antenna(antenna_config)
        self.assertIsInstance(antenna, IsotropicAntenna)

    def test_create_isotropic(self):
        antenna_config = AntennaConfig()
        antenna_config.isotropic.SetInParent()
        antenna = AntennaFactory.create_antenna(antenna_config)
        self.assertIsInstance(antenna, IsotropicAntenna)

    def test_create_dipole(self):
        antenna_config = AntennaConfig()
        antenna_config.dipole.SetInParent()
        antenna = AntennaFactory.create_antenna(antenna_config)
        self.assertIsInstance(antenna, DipoleAntenna)

    def test_create_horn(self):
        antenna_config = AntennaConfig()
        antenna_config.horn.SetInParent()
        antenna = AntennaFactory.create_antenna(antenna_config)
        self.assertIsInstance(antenna, HornAntenna)

    def test_create_patch(self):
        antenna_config = AntennaConfig()
        antenna_config.patch.SetInParent()
        antenna = AntennaFactory.create_antenna(antenna_config)
        self.assertIsInstance(antenna, PatchAntenna)

    def test_create_radiation_pattern(self):
        antenna_config = AntennaConfig()
        antenna_config.radiation_pattern.data = (
            "simulation/antenna/data/radiation_pattern_patch_antenna_24ghz_20mil_0mm.csv"
        )
        antenna = AntennaFactory.create_antenna(antenna_config)
        self.assertIsInstance(antenna, RadiationPattern)


if __name__ == "__main__":
    absltest.main()
