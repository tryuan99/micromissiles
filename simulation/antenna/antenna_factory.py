"""The antenna factory class instantiates various antennas."""

from simulation.antenna.antenna import Antenna
from simulation.antenna.antenna_radiation_pattern import \
    AntennaRadiationPattern
from simulation.antenna.dipole_antenna import DipoleAntenna
from simulation.antenna.horn_antenna import HornAntenna
from simulation.antenna.isotropic_antenna import IsotropicAntenna
from simulation.antenna.patch_antenna import PatchAntenna
from simulation.antenna.proto.antenna_config_pb2 import AntennaConfig


class AntennaFactory:
    """Antenna factory."""

    @staticmethod
    def create_antenna(antenna_config: AntennaConfig) -> Antenna:
        """Creates an antenna according to the configuration.

        Args:
            antenna_config: Antenna configuration.

        Returns:
            The antenna instance.
        """
        match antenna_config.WhichOneof("type_oneof"):
            case "isotropic":
                return IsotropicAntenna()
            case "dipole":
                return DipoleAntenna(length=antenna_config.dipole.length,)
            case "horn":
                return HornAntenna(
                    a=antenna_config.horn.a,
                    b=antenna_config.horn.b,
                    a1=antenna_config.horn.a1,
                    b1=antenna_config.horn.b1,
                    rho1=antenna_config.horn.rho1,
                    rho2=antenna_config.horn.rho2,
                )
            case "patch":
                return PatchAntenna(
                    width=antenna_config.patch.width,
                    length=antenna_config.patch.length,
                )
            case "radiation_pattern":
                return AntennaRadiationPattern(
                    data_csv=antenna_config.radiation_pattern.data,)
            case _:
                return IsotropicAntenna()
