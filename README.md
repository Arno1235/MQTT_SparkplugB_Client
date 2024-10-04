# MQTT Sparkplug B Client Framework

This framework provides a simple interface for handling MQTT communications using the Sparkplug B protocol. It allows for easy connection to an MQTT broker, publishing messages in Sparkplug B format, subscribing to topics, and handling incoming messages with custom callbacks.

## Features
- Connect to an MQTT broker using Sparkplug B protocol.
- Publish structured messages to the broker.
- Subscribe to topics and handle incoming messages using custom callbacks.
- Automatically publish birth and death messages as part of Sparkplug B functionality.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-repo/mqtt-sparkplugb-client.git
```

2. Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Setup MQTT Client

Define the message structure and create an instance of MQTTSparkplugBClient:

```python
from mqtt_sparkplugb_client import MQTTSparkplugBClient

message_structure = {
    'string_message': str,
    'int_message': int,
    'float_message': float,
}

client = MQTTSparkplugBClient(
    broker_ip='192.168.0.70',
    broker_port=1883,
    secrets_file='secrets.txt',
    topic_group='test_group',
    topic_node='test_node',
    message_structure=message_structure,
    name='test_client'
)

client.connect()
```

### 2. Publishing Messages

Publish messages in a loop:

```python
for i in range(10):
    message = {
        'string_message': f'message nr {i}',
        'int_message': i,
        'float_message': i / 100,
    }
    client.publish(message)
```

### 3. Subscribing to Topics

Subscribe to a topic and handle incoming messages with a custom callback:

```python
def custom_callback(client, userdata, message):
    print(f"Received message on {message.topic}: {message.payload.decode()}")

client.subscribe('test_group/test_node/data', custom_callback)
```

### 4. Disconnecting

After finishing communication, disconnect from the MQTT broker:

```python
client.disconnect()
```

Full Example can be found in `example.py`.

## Configuration
- `broker_ip`: IP address of the MQTT broker.
- `broker_port`: Port number for MQTT broker (default is 1883).
- `secrets_file`: Path to a file containing the username and password for the MQTT broker, each on a separate line.
- `topic_group`: Sparkplug B group topic.
- `topic_node`: Sparkplug B node topic.
- `message_structure`: A dictionary that defines the structure of the messages to be sent, mapping metric names to their data types (`str`, `int`, `float`, etc.).

## License

This project is licensed under the MIT License.
