"""The swarm simulator class generates a swarm of missiles placed at random
positions and a swarm of targets placed at random positions with random
velocities.
"""

import numpy as np

from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig
from simulation.swarm.proto.state_pb2 import State
from simulation.swarm.proto.swarm_config_pb2 import SwarmConfig
from simulation.swarm.simulator import Simulator


class SwarmSimulator(Simulator):
    """Swarm simulator."""

    def __init__(self, swarm_config: SwarmConfig) -> None:
        # Populate the simulator configuration.
        simulator_config = SimulatorConfig()
        simulator_config.step_time = swarm_config.step_time

        # Generate swarms of missiles.
        for missile_swarm_config in swarm_config.missile_swarm_configs:
            for _ in range(missile_swarm_config.num_missiles):
                missile_config = simulator_config.missile_configs.add()
                missile_config.initial_state.CopyFrom(
                    self._generate_random_state(
                        missile_swarm_config.mean,
                        missile_swarm_config.standard_deviation,
                    ))
                missile_config.physical_config.CopyFrom(
                    missile_swarm_config.physical_config)

        # Generate swarms of targets.
        for target_swarm_config in swarm_config.target_swarm_configs:
            for _ in range(target_swarm_config.num_targets):
                target_config = simulator_config.target_configs.add()
                target_config.initial_state.CopyFrom(
                    self._generate_random_state(
                        target_swarm_config.mean,
                        target_swarm_config.standard_deviation,
                    ))
                target_config.physical_config.CopyFrom(
                    target_swarm_config.physical_config)
        super().__init__(simulator_config)

    @staticmethod
    def _generate_random_state(mean: State, standard_deviation: State) -> State:
        """Generates a random state.

        Args:
            mean: Mean of the state variables.
            standard_deviation: Standard deviatino of the state variables.

        Returns:
            The randomly generated state.
        """
        generate_sample = lambda mean, standard_deviation: np.random.normal(
            mean, standard_deviation)
        state = State()
        # Randomly generate the position vector.
        state.position.x = generate_sample(
            mean.position.x,
            standard_deviation.position.x,
        )
        state.position.y = generate_sample(
            mean.position.y,
            standard_deviation.position.y,
        )
        state.position.z = generate_sample(
            mean.position.z,
            standard_deviation.position.z,
        )
        # Randomly generate the velocity vector.
        state.velocity.x = generate_sample(
            mean.velocity.x,
            standard_deviation.velocity.x,
        )
        state.velocity.y = generate_sample(
            mean.velocity.y,
            standard_deviation.velocity.y,
        )
        state.velocity.z = generate_sample(
            mean.velocity.z,
            standard_deviation.velocity.z,
        )
        return state
