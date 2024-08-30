from absl.testing import absltest

from simulation.swarm.missiles.dummy_missile import DummyMissile
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.proto.target_config_pb2 import TargetConfig
from simulation.swarm.targets.dummy_target import DummyTarget
from simulation.swarm.targets.target_assignment import \
    DistanceBasedTargetAssignment


class DistanceBasedTargetAssignmentTestCase(absltest.TestCase):

    def setUp(self):
        # Configure the missiles.
        missiles = []
        missile_config = MissileConfig()
        missile_config.initial_state.position.x = 1
        missile_config.initial_state.position.y = 2
        missile_config.initial_state.position.z = 1
        missiles.append(DummyMissile(missile_config))

        missile_config = MissileConfig()
        missile_config.initial_state.position.x = 10
        missile_config.initial_state.position.y = 12
        missile_config.initial_state.position.z = 1
        missiles.append(DummyMissile(missile_config))

        missile_config = MissileConfig()
        missile_config.initial_state.position.x = 10
        missile_config.initial_state.position.y = 12
        missile_config.initial_state.position.z = 1
        missiles.append(DummyMissile(missile_config))

        missile_config = MissileConfig()
        missile_config.initial_state.position.x = 10
        missile_config.initial_state.position.y = 10
        missile_config.initial_state.position.z = 1
        missiles.append(DummyMissile(missile_config))

        # Configure the targets.
        targets = []
        target_config = TargetConfig()
        target_config.initial_state.position.x = 10
        target_config.initial_state.position.y = 15
        target_config.initial_state.position.z = 2
        targets.append(DummyTarget(target_config))

        target_config = TargetConfig()
        target_config.initial_state.position.x = 1
        target_config.initial_state.position.y = 2
        target_config.initial_state.position.z = 2
        targets.append(DummyTarget(target_config))

        # Assign targets to missiles.
        self.target_assignment = (DistanceBasedTargetAssignment(
            missiles, targets))

    def test_assign_targets(self):
        target_assignments = (
            self.target_assignment.missile_to_target_assignments)
        self.assertEqual(target_assignments[0], 1)
        self.assertEqual(target_assignments[1], 0)
        self.assertEqual(target_assignments[2], 0)
        self.assertEqual(target_assignments[3], 1)


if __name__ == "__main__":
    absltest.main()
