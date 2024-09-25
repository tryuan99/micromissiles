from absl.testing import absltest
from simulation.swarm.proto.agent_pb2 import AgentConfig

from simulation.swarm.assignment.py.distance_assignment import \
    DistanceAssignment
from simulation.swarm.interceptor.py.dummy_interceptor import DummyInterceptor
from simulation.swarm.threat.py.dummy_threat import DummyThreat


class DistanceAssignmentTestCase(absltest.TestCase):

    def setUp(self):
        # Configure the interceptors.
        interceptors = []
        interceptor_config = AgentConfig()
        interceptor_config.initial_state.position.x = 1
        interceptor_config.initial_state.position.y = 2
        interceptor_config.initial_state.position.z = 1
        interceptors.append(DummyInterceptor(interceptor_config))

        interceptor_config = AgentConfig()
        interceptor_config.initial_state.position.x = 10
        interceptor_config.initial_state.position.y = 12
        interceptor_config.initial_state.position.z = 1
        interceptors.append(DummyInterceptor(interceptor_config))

        interceptor_config = AgentConfig()
        interceptor_config.initial_state.position.x = 10
        interceptor_config.initial_state.position.y = 12
        interceptor_config.initial_state.position.z = 1
        interceptors.append(DummyInterceptor(interceptor_config))

        interceptor_config = AgentConfig()
        interceptor_config.initial_state.position.x = 10
        interceptor_config.initial_state.position.y = 10
        interceptor_config.initial_state.position.z = 1
        interceptors.append(DummyInterceptor(interceptor_config))

        # Configure the threats.
        threats = []
        threat_config = AgentConfig()
        threat_config.initial_state.position.x = 10
        threat_config.initial_state.position.y = 15
        threat_config.initial_state.position.z = 2
        threats.append(DummyThreat(threat_config))

        threat_config = AgentConfig()
        threat_config.initial_state.position.x = 1
        threat_config.initial_state.position.y = 2
        threat_config.initial_state.position.z = 2
        threats.append(DummyThreat(threat_config))

        # Assign threats to interceptors.
        self.threat_assignment = DistanceAssignment(interceptors, threats)

    def test_assign_threats(self):
        threat_assignments = (
            self.threat_assignment.interceptor_to_threat_assignments)
        self.assertEqual(threat_assignments[0], 1)
        self.assertEqual(threat_assignments[1], 0)
        self.assertEqual(threat_assignments[2], 0)
        self.assertEqual(threat_assignments[3], 1)


if __name__ == "__main__":
    absltest.main()
