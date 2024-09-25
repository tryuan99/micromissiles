"""This file defines the list of available threats."""

from simulation.swarm.proto.agent_pb2 import ThreatType

from simulation.swarm.threat.py.drone import Drone
from simulation.swarm.threat.py.missile import Missile

# Map from the threat type enumeration to the threat class.
THREAT_TYPE_ENUM_TO_CLASS = {
    ThreatType.DRONE: Drone,
    ThreatType.MISSILE: Missile,
}
