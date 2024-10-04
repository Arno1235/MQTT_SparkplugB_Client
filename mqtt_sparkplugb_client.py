import logging
from typing import Type, Any

import paho.mqtt.client as mqtt
from tahutils import MetricDataType, SpbModel, SpbTopic


MESSAGE_TYPE_CONVERSIONS = {
    str: {
        'spb_type': MetricDataType.String,
        'birth_value': '',
    },
    int: {
        'spb_type': MetricDataType.Int32,
        'birth_value': -1,
    },
    float: {
        'spb_type': MetricDataType.Float,
        'birth_value': -1,
    },
}


class MQTTSparkplugBClient:
    """A client for handling MQTT communications using the Sparkplug B protocol."""

    def __init__(
            self,
            broker_ip: str,
            broker_port: int,
            secrets_file: str,
            topic_group: str,
            topic_node: str,
            message_structure: dict[str, Type],
            name: str = None,
        ) -> None:
        """
        Initializes the MQTTSparkplugBClient instance.

        Args:
            broker_ip (str): The IP address of the MQTT broker.
            broker_port (int): The port to connect to the MQTT broker.
            secrets_file (str): Path to the file containing MQTT credentials (username and password).
            topic_group (str): The group topic for Sparkplug B messages.
            topic_node (str): The node topic for Sparkplug B messages.
            message_structure (dict[str, Type]): A dictionary defining the message structure and corresponding data types.
            name (str, optional): The name of the MQTT client. Defaults to None.
        """
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.secrets_file = secrets_file
        self.topic_group = topic_group
        self.topic_node = topic_node
        self.message_structure = message_structure
        self.name = name

    def connect(self) -> None:
        """
        Connects to the MQTT broker and publishes the birth message.

        The function constructs the Sparkplug B model and topic based on the message structure, reads the
        credentials from the secrets file, and connects to the MQTT broker. The birth message is then published
        after the connection is established.
        """
        spb_message_structure = {message_name: MESSAGE_TYPE_CONVERSIONS[message_type]['spb_type'] for message_name, message_type in self.message_structure.items()}

        self.sparkplugb_model = SpbModel(spb_message_structure, serialize_cast=bytes)
        self.sparkplugb_topic = SpbTopic(self.topic_group, self.topic_node)

        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.name)

        with open(self.secrets_file, "r") as f:
            secrets = f.read().splitlines()
        self.mqtt_client.username_pw_set(secrets[0], secrets[1])

        self.mqtt_client.will_set(self.sparkplugb_topic.ndeath, self.sparkplugb_model.getDeathPayload())

        logging.info('Connecting to client')
        self.mqtt_client.connect(self.broker_ip, self.broker_port)

        spb_birth_data = {message_name: MESSAGE_TYPE_CONVERSIONS[message_type]['birth_value'] for message_name, message_type in self.message_structure.items()}

        logging.info(f'Publishing birth with data {spb_birth_data}')
        birth = self.sparkplugb_model.getBirthPayload(spb_birth_data)
        self.mqtt_client.publish(self.sparkplugb_topic.nbirth, birth)
    
    def disconnect(self) -> None:
        """
        Disconnects from the MQTT broker after publishing the death message.

        This function publishes the last known death message to the Sparkplug B death topic and then
        disconnects from the broker.
        """
        logging.info('Publishing death')
        self.mqtt_client.publish(self.sparkplugb_topic.ndeath, self.sparkplugb_model.last_death)

        logging.info('Disconnecting to client')
        self.mqtt_client.disconnect()
    
    def publish(self, data: dict[str, Any]) -> None:
        """
        Publishes data to the MQTT broker.

        Args:
            data (dict[str, Any]): A dictionary containing the data to be published. The keys must
            match the metrics defined in the message structure, but not all metrics need to be included.
        
        This function publishes the provided data to the NDATA topic using the Sparkplug B model.
        """
        logging.info(f'Publishing data: {data}')
        self.mqtt_client.publish(self.sparkplugb_topic.ndata, self.sparkplugb_model.getDataPayload(data))

        logging.info(f'Last published state: {self.sparkplugb_model.current_values}')
