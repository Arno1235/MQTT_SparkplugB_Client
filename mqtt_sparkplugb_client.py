from enum import Enum
import logging

import paho.mqtt.client as mqtt
from tahutils import MetricDataType, SpbModel, SpbTopic


"""
Enums can be used to define the metric names. This is useful for ensuring that the metric names are consistent across the application.
"""
class Metric(Enum):
    message = "message"
    steps = "steps"
    percent = "percent"


class MQTTSparkplugBClient:
    def __init__(self, broker_ip, broker_port, topic, secrets_file, name=None) -> None:
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.topic = topic
        self.secrets_file = secrets_file
        self.name = name

    def connect(self) -> None:
        """
        When constructing the SpbModel, every metric must be defined with its corresponding MetricDataType.
        Additionally, we set the serialize_cast to the datatype expected by the MQTT client's publish method.
        """
        self.sparkplugb_model = SpbModel(
            {
                Metric.message: MetricDataType.String,
                Metric.steps: MetricDataType.Int32,
                Metric.percent: MetricDataType.Float,
            },
            serialize_cast=bytes
        )
        self.sparkplugb_topic = SpbTopic("testgroup", "testnode")

        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.name)

        with open(self.secrets_file, "r") as f:
            secrets = f.read().splitlines()
        self.mqtt_client.username_pw_set(secrets[0], secrets[1])

        """
        We must get the death payload before connecting to the broker. This is because the will payload is sent as part of the connection process.
        Additionally, the death payload must be generated before a birth payload is requested. 
        """
        self.mqtt_client.will_set(
            self.sparkplugb_topic.ndeath,
            self.sparkplugb_model.getDeathPayload(),
        )

        logging.info('Connecting to client')
        self.mqtt_client.connect(self.broker_ip, self.broker_port)

        data = {
            Metric.message: "Hello, world!",
            Metric.steps: 0,
            Metric.percent: 0,
        }

        logging.info(f'Publishing birth with data {data}')
        birth = self.sparkplugb_model.getBirthPayload(data)
        self.mqtt_client.publish(
            self.sparkplugb_topic.nbirth,
            birth
        )
    
    def disconnect(self) -> None:
        logging.info('Publishing death')
        self.mqtt_client.publish(
            self.sparkplugb_topic.ndeath,
            self.sparkplugb_model.last_death
        )

        logging.info('Disconnecting to client')
        self.mqtt_client.disconnect()
    
    def publish(self, message) -> None:
        """
        Data for NDATA/DDATA doesn't have to be a complete set of metrics.
        """

        data = {
            Metric.message: message,
            Metric.steps: 0,
            Metric.percent: 0,
        }

        logging.info(f'Publishing data: {data}')
        self.mqtt_client.publish(
            self.sparkplugb_topic.ndata,
            self.sparkplugb_model.getDataPayload(data)
        )
        logging.info(f'Last published state: {self.sparkplugb_model.current_values}')
