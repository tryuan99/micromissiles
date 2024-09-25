"""This file defines the list of available interceptors."""

from simulation.swarm.proto.agent_pb2 import InterceptorType

from simulation.swarm.interceptor.py.hydra_70 import Hydra70
from simulation.swarm.interceptor.py.micromissile import Micromissile

# Map from the interceptor type enumeration to the interceptor class.
INTERCEPTOR_TYPE_ENUM_TO_CLASS = {
    InterceptorType.MICROMISSILE: Micromissile,
    InterceptorType.HYDRA_70: Hydra70,
}
