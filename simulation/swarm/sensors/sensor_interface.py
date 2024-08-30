"""The sensor class is an interface for a missile's sensing system."""

from abc import ABC, abstractmethod

from simulation.swarm.agent import Agent
from simulation.swarm.proto.sensor_pb2 import SensorOutput


class Sensor(ABC):
    """Sensing system.

    Attributes:
        agent: The agent on which the sensor is mounted.
    """

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    @abstractmethod
    def sense(self, targets: list[Agent]) -> list[SensorOutput]:
        """Senses the targets.

        TODO(titan): The sensor output should be relative to the agent's roll,
        pitch, and yaw.

        Args:
            targets: List of targets to sense.

        Returns:
            A list of sensor outputs for the targets.
        """
