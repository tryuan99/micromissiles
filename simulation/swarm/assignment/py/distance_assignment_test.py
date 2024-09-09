from absl.testing import absltest
from simulation.swarm.proto.agent_pb2 import AgentConfig

from simulation.swarm.assignment.py.distance_assignment import \
    DistanceAssignment
from simulation.swarm.missiles.py.dummy_missile import DummyMissile
from simulation.swarm.targets.py.dummy_target import DummyTarget


class DistanceAssignmentTestCase(absltest.TestCase):

    def setUp(self):
        # Configure the missiles.
        missiles = []
        missile_config = AgentConfig()
        missile_config.initial_state.position.x = 1
        missile_config.initial_state.position.y = 2
        missile_config.initial_state.position.z = 1
        missiles.append(DummyMissile(missile_config))

        missile_config = AgentConfig()
        missile_config.initial_state.position.x = 10
        missile_config.initial_state.position.y = 12
        missile_config.initial_state.position.z = 1
        missiles.append(DummyMissile(missile_config))

        missile_config = AgentConfig()
        missile_config.initial_state.position.x = 10
        missile_config.initial_state.position.y = 12
        missile_config.initial_state.position.z = 1
        missiles.append(DummyMissile(missile_config))

        missile_config = AgentConfig()
        missile_config.initial_state.position.x = 10
        missile_config.initial_state.position.y = 10
        missile_config.initial_state.position.z = 1
        missiles.append(DummyMissile(missile_config))

        # Configure the targets.
        targets = []
        target_config = AgentConfig()
        target_config.initial_state.position.x = 10
        target_config.initial_state.position.y = 15
        target_config.initial_state.position.z = 2
        targets.append(DummyTarget(target_config))

        target_config = AgentConfig()
        target_config.initial_state.position.x = 1
        target_config.initial_state.position.y = 2
        target_config.initial_state.position.z = 2
        targets.append(DummyTarget(target_config))

        # Assign targets to missiles.
        self.target_assignment = DistanceAssignment(missiles, targets)

    def test_assign_targets(self):
        target_assignments = (
            self.target_assignment.missile_to_target_assignments)
        self.assertEqual(target_assignments[0], 1)
        self.assertEqual(target_assignments[1], 0)
        self.assertEqual(target_assignments[2], 0)
        self.assertEqual(target_assignments[3], 1)


if __name__ == "__main__":
    absltest.main()
