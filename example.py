import time
import logging

from mqtt_sparkplugb_client import MQTTSparkplugBClient

if __name__ == '__main__':
    # Set up logging configuration to output logs to the console
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Define the structure of the messages to be sent, mapping message names to their data types
    message_structure = {
        'string_message': str,      # Message containing a string
        'int_message': int,         # Message containing an integer
        'float_message': float,     # Message containing a float
    }

    # Create an instance of the MQTTSparkplugBClient with the necessary parameters
    client = MQTTSparkplugBClient(
        broker_ip='192.168.0.70',               # IP address of the MQTT broker
        broker_port=1883,                       # Port for MQTT communication
        secrets_file='secrets.txt',             # File containing MQTT credentials
        topic_group='test_group',               # Group topic for Sparkplug B messages
        topic_node='test_node',                 # Node topic for Sparkplug B messages
        message_structure=message_structure,    # Structure of the messages to be sent
        name='test',                            # Name for the MQTT client
    )

    # Connect to the MQTT broker
    client.connect()

    # Publish a series of messages to the MQTT broker
    for i in range(10):
        # Create a message with a string, integer, and float
        message = {
            'string_message': f'message nr {i}',    # String message with the current iteration number
            'int_message': i,                       # Integer message with the current iteration number
            'float_message': i/100,                 # Float message as a fraction of the iteration number
        }
        # Publish the constructed message
        client.publish(message)

        # Sleep for 1 second before sending the next message
        time.sleep(1)

    # Disconnect from the MQTT broker after publishing all messages
    client.disconnect()
