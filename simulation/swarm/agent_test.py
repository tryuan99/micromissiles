import numpy as np
from absl.testing import absltest

from simulation.swarm.agent import StaticAgent
from simulation.swarm.proto.state_pb2 import State


class StaticAgentTestCase(absltest.TestCase):

    def setUp(self):
        # Configure the agent.
        agent_state = State()
        self.agent_velocity = np.array([-2, 1, 0])
        (
            agent_state.velocity.x,
            agent_state.velocity.y,
            agent_state.velocity.z,
        ) = self.agent_velocity
        self.agent = StaticAgent(agent_state)

    def test_get_principal_axes_roll(self):
        roll, lateral, yaw = self.agent.get_principal_axes()

        # Check that the roll axis is aligned to the velocity vector.
        self.assertAlmostEqual(
            np.dot(roll, self.agent_velocity),
            np.linalg.norm(roll) * np.linalg.norm(self.agent_velocity))

        # Check that the roll axis is orthogonal to the other axes.
        self.assertAlmostEqual(np.dot(roll, lateral), 0)
        self.assertAlmostEqual(np.dot(roll, yaw), 0)

    def test_get_principal_axes_lateral(self):
        roll, lateral, yaw = self.agent.get_principal_axes()

        # Check the lateral axis direction.
        expected_lateral_axis = np.array([1, 2, 0])
        self.assertAlmostEqual(
            np.dot(lateral, expected_lateral_axis),
            np.linalg.norm(lateral) * np.linalg.norm(expected_lateral_axis))

        # Check that the lateral axis is orthogonal to the other axes.
        self.assertAlmostEqual(np.dot(lateral, roll), 0)
        self.assertAlmostEqual(np.dot(lateral, yaw), 0)

    def test_get_principal_axes_yaw(self):
        roll, lateral, yaw = self.agent.get_principal_axes()

        # Check the yaw axis direction.
        expected_yaw_axis = np.array([0, 0, 1])
        self.assertAlmostEqual(
            np.dot(yaw, expected_yaw_axis),
            np.linalg.norm(yaw) * np.linalg.norm(expected_yaw_axis))

        # Check that the yaw axis is orthogonal to the other axes.
        self.assertAlmostEqual(np.dot(yaw, roll), 0)
        self.assertAlmostEqual(np.dot(yaw, lateral), 0)


if __name__ == "__main__":
    absltest.main()
