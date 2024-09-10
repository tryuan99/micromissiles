"""This file defines the list of available missiles."""

from simulation.swarm.proto.agent_pb2 import MissileType

from simulation.swarm.missile.py.hydra_70 import Hydra70
from simulation.swarm.missile.py.micromissile import Micromissile

# Map from the missile type enumeration to the missile class.
MISSILE_TYPE_ENUM_TO_CLASS = {
    MissileType.MICROMISSILE: Micromissile,
    MissileType.HYDRA_70: Hydra70,
}
