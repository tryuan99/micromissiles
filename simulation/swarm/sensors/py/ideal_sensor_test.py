import numpy as np
from absl.testing import absltest
from simulation.swarm.proto.state_pb2 import State

from simulation.swarm.py.model_agent import ModelAgent
from simulation.swarm.sensors.py.ideal_sensor import IdealSensor


class IdealSensorTargetAtBoresightTestCase(absltest.TestCase):

    def setUp(self):
        # Configure the agent.
        agent_state = State()
        self.agent_velocity = np.array([0, 4, 0])
        (
            agent_state.velocity.x,
            agent_state.velocity.y,
            agent_state.velocity.z,
        ) = self.agent_velocity
        self.agent = ModelAgent(agent_state)
        self.sensor = IdealSensor(self.agent)

        # Configure the target.
        target_state = State()
        self.target_position = np.array([0, 4, 0])

        (
            target_state.position.x,
            target_state.position.y,
            target_state.position.z,
        ) = self.target_position
        self.target_velocity = np.array([2, 2, -1])
        (
            target_state.velocity.x,
            target_state.velocity.y,
            target_state.velocity.z,
        ) = self.target_velocity
        self.target = ModelAgent(target_state)

    def test_sense_position_range(self):
        expected_range = np.linalg.norm(self.target_position)
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.range,
            expected_range,
        )

    def test_sense_position_azimuth(self):
        expected_azimuth = np.arctan(self.target_position[0] /
                                     self.target_position[1])
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.azimuth,
            expected_azimuth,
        )

    def test_sense_position_elevation(self):
        expected_elevation = np.arctan(
            self.target_position[2] /
            np.sqrt(self.target_position[0]**2 + self.target_position[1]**2))
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.elevation,
            expected_elevation,
        )

    def test_sense_velocity_range(self):
        expected_range_rate = -2
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.range,
            expected_range_rate,
        )

    def test_sense_velocity_azimuth(self):
        expected_azimuth_velocity = 2 / 4
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.azimuth,
            expected_azimuth_velocity,
        )

    def test_sense_velocity_elevation(self):
        expected_elevation_velocity = -1 / 4
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.elevation,
            expected_elevation_velocity,
        )


class IdealSensorTargetAtStarboardTestCase(absltest.TestCase):

    def setUp(self):
        # Configure the agent.
        agent_state = State()
        self.agent_velocity = np.array([0, 1, 0])
        (
            agent_state.velocity.x,
            agent_state.velocity.y,
            agent_state.velocity.z,
        ) = self.agent_velocity
        self.agent = ModelAgent(agent_state)
        self.sensor = IdealSensor(self.agent)

        # Configure the target.
        target_state = State()
        self.target_position = np.array([5, 0, 0])

        (
            target_state.position.x,
            target_state.position.y,
            target_state.position.z,
        ) = self.target_position
        self.target_velocity = np.array([2, 3, -1])
        (
            target_state.velocity.x,
            target_state.velocity.y,
            target_state.velocity.z,
        ) = self.target_velocity
        self.target = ModelAgent(target_state)

    def test_sense_position_range(self):
        expected_range = np.linalg.norm(self.target_position)
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.range,
            expected_range,
        )

    def test_sense_position_azimuth(self):
        expected_azimuth = np.arctan(self.target_position[0] /
                                     self.target_position[1])
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.azimuth,
            expected_azimuth,
        )

    def test_sense_position_elevation(self):
        expected_elevation = np.arctan(
            self.target_position[2] /
            np.sqrt(self.target_position[0]**2 + self.target_position[1]**2))
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.elevation,
            expected_elevation,
        )

    def test_sense_velocity_range(self):
        expected_range_rate = 2
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.range,
            expected_range_rate,
        )

    def test_sense_velocity_azimuth(self):
        expected_azimuth_velocity = -2 / 5
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.azimuth,
            expected_azimuth_velocity,
        )

    def test_sense_velocity_elevation(self):
        expected_elevation_velocity = -1 / 5
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.elevation,
            expected_elevation_velocity,
        )


class IdealSensorTargetAboveOnYawTestCase(absltest.TestCase):

    def setUp(self):
        # Configure the agent.
        agent_state = State()
        self.agent_velocity = np.array([0, 1, 0])
        (
            agent_state.velocity.x,
            agent_state.velocity.y,
            agent_state.velocity.z,
        ) = self.agent_velocity
        self.agent = ModelAgent(agent_state)
        self.sensor = IdealSensor(self.agent)

        # Configure the target.
        target_state = State()
        self.target_position = np.array([0, 0, 5])

        (
            target_state.position.x,
            target_state.position.y,
            target_state.position.z,
        ) = self.target_position
        self.target_velocity = np.array([0, 2, 0])
        (
            target_state.velocity.x,
            target_state.velocity.y,
            target_state.velocity.z,
        ) = self.target_velocity
        self.target = ModelAgent(target_state)

    def test_sense_position_range(self):
        expected_range = np.linalg.norm(self.target_position)
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.range,
            expected_range,
        )

    def test_sense_position_azimuth(self):
        expected_azimuth = 0
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.azimuth,
            expected_azimuth,
        )

    def test_sense_position_elevation(self):
        expected_elevation = np.arctan(
            self.target_position[2] /
            np.sqrt(self.target_position[0]**2 + self.target_position[1]**2))
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.elevation,
            expected_elevation,
        )

    def test_sense_velocity_range(self):
        expected_range_rate = 0
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.range,
            expected_range_rate,
        )

    def test_sense_velocity_azimuth(self):
        expected_azimuth_velocity = 0
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.azimuth,
            expected_azimuth_velocity,
        )

    def test_sense_velocity_elevation(self):
        expected_elevation_velocity = -1 / 5
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.elevation,
            expected_elevation_velocity,
        )


class IdealSensorTargetAtAzimuth45Elevation45TestCase(absltest.TestCase):

    def setUp(self):
        # Configure the agent.
        agent_state = State()
        self.agent_velocity = np.array([0, 1, 0])
        (
            agent_state.velocity.x,
            agent_state.velocity.y,
            agent_state.velocity.z,
        ) = self.agent_velocity
        self.agent = ModelAgent(agent_state)
        self.sensor = IdealSensor(self.agent)

        # Configure the target.
        target_state = State()
        self.target_position = np.array([1, 1, np.sqrt(2)])

        (
            target_state.position.x,
            target_state.position.y,
            target_state.position.z,
        ) = self.target_position
        self.target_velocity = (np.array([-1, 1, 0]) +
                                np.array([1, 1, -np.sqrt(2)]) +
                                self.agent_velocity)
        (
            target_state.velocity.x,
            target_state.velocity.y,
            target_state.velocity.z,
        ) = self.target_velocity
        self.target = ModelAgent(target_state)

    def test_sense_position_range(self):
        expected_range = np.linalg.norm(self.target_position)
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.range,
            expected_range,
        )

    def test_sense_position_azimuth(self):
        expected_azimuth = np.arctan(self.target_position[0] /
                                     self.target_position[1])
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.azimuth,
            expected_azimuth,
        )

    def test_sense_position_elevation(self):
        expected_elevation = np.arctan(
            self.target_position[2] /
            np.sqrt(self.target_position[0]**2 + self.target_position[1]**2))
        sensor_output = self.sensor.sense_position(self.target)
        self.assertAlmostEqual(
            sensor_output.position.elevation,
            expected_elevation,
        )

    def test_sense_velocity_range(self):
        expected_range_rate = 0
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.range,
            expected_range_rate,
        )

    def test_sense_velocity_azimuth(self):
        expected_azimuth_velocity = -np.sqrt(2) / 2
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.azimuth,
            expected_azimuth_velocity,
        )

    def test_sense_velocity_elevation(self):
        expected_elevation_velocity = -2 / 2
        sensor_output = self.sensor.sense_velocity(self.target)
        self.assertAlmostEqual(
            sensor_output.velocity.elevation,
            expected_elevation_velocity,
        )


if __name__ == "__main__":
    absltest.main()
