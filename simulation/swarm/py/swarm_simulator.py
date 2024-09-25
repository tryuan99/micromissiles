"""The swarm simulator class generates a swarm of interceptors placed at random
positions and a swarm of threats placed at random positions with random
velocities.
"""

import numpy as np
from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig
from simulation.swarm.proto.state_pb2 import State
from simulation.swarm.proto.swarm_config_pb2 import SwarmConfig

from simulation.swarm.py.simulator import Simulator


class SwarmSimulator(Simulator):
    """Swarm simulator."""

    def __init__(self, swarm_config: SwarmConfig) -> None:
        # Populate the simulator configuration.
        simulator_config = SimulatorConfig()
        simulator_config.step_time = swarm_config.step_time

        # Generate swarms of interceptors.
        for interceptor_swarm_config in swarm_config.interceptor_swarm_configs:
            for _ in range(interceptor_swarm_config.num_agents):
                interceptor_config = simulator_config.interceptor_configs.add()
                interceptor_config.interceptor_type = interceptor_swarm_config.agent_config.interceptor_type
                interceptor_config.initial_state.CopyFrom(
                    self._generate_random_state(
                        interceptor_swarm_config.agent_config.initial_state,
                        interceptor_swarm_config.agent_config.
                        standard_deviation,
                    ))
                interceptor_config.dynamic_config.CopyFrom(
                    interceptor_swarm_config.agent_config.dynamic_config)
                interceptor_config.plotting_config.CopyFrom(
                    interceptor_swarm_config.agent_config.plotting_config)
                interceptor_config.submunitions_config.CopyFrom(
                    interceptor_swarm_config.agent_config.submunitions_config)

        # Generate swarms of threats.
        for threat_swarm_config in swarm_config.threat_swarm_configs:
            for _ in range(threat_swarm_config.num_agents):
                threat_config = simulator_config.threat_configs.add()
                threat_config.threat_type = threat_swarm_config.agent_config.threat_type
                threat_config.initial_state.CopyFrom(
                    self._generate_random_state(
                        threat_swarm_config.agent_config.initial_state,
                        threat_swarm_config.agent_config.standard_deviation,
                    ))
                threat_config.dynamic_config.CopyFrom(
                    threat_swarm_config.agent_config.dynamic_config)
                threat_config.plotting_config.CopyFrom(
                    threat_swarm_config.agent_config.plotting_config)
                threat_config.submunitions_config.CopyFrom(
                    threat_swarm_config.agent_config.submunitions_config)
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
