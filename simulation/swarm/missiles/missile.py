"""This file defines the list of available missiles."""

from simulation.swarm.missiles.micromissile import Micromissile
from simulation.swarm.proto.missile_config_pb2 import MissileType

# Map from the missile type enumeration to the missile class.
MISSILE_TYPE_ENUM_TO_CLASS = {
    MissileType.MICROMISSILE: Micromissile,
}
