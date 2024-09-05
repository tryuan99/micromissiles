"""This file defines the list of available targets."""

from simulation.swarm.proto.target_config_pb2 import TargetType

from simulation.swarm.targets.py.drone import Drone
from simulation.swarm.targets.py.missile import Missile

# Map from the target type enumeration to the target class.
TARGET_TYPE_ENUM_TO_CLASS = {
    TargetType.DRONE: Drone,
    TargetType.MISSILE: Missile,
}
