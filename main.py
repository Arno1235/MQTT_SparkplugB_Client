import time
import logging

from mqtt_sparkplugb_client import MQTTSparkplugBClient

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    client = MQTTSparkplugBClient(broker_ip='192.168.0.70', broker_port=1883, topic=None, secrets_file='secrets.txt', name='test')

    client.connect()

    for i in range(10):
        client.publish(f'index {i}')
        time.sleep(1)

    client.disconnect()
