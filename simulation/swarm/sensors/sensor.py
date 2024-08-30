"""This file defines the list of available sensors."""

from simulation.swarm.proto.sensor_pb2 import SensorType
from simulation.swarm.sensors.ideal_sensor import IdealSensor

# Map from the sensor type enumeration to the sensor class.
SENSOR_TYPE_ENUM_TO_CLASS = {
    SensorType.IDEAL: IdealSensor,
}
