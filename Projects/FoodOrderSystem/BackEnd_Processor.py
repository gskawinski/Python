""" 
START KAFKA SERVER
- Start a single-node ZooKeeper instance using the following command:
sudo systemctl start zookeeper
- Verify the status of ZooKeeper:
sudo systemctl status zookeeper

Kafka requires ZooKeeper, so make sure ZooKeeper is running before starting Kafka.
- Now start the Kafka server:
sudo systemctl start kafka
- Check the status of the Kafka service:
sudo systemctl status kafka

"""

import json
import os
import random
import time
from kafka import KafkaProducer
from confluent_kafka import Producer

# import order generator
from FrontEnd_Processor import create_order_automatic as get_order

# Load restaurant data/offer from restaurant_menus.json
with open("restaurant_menus.json", "r") as f:
    restaurants_data = json.load(f)


# kafka producer call back function
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to topic:{msg.topic()} partition[{msg.partition()}]")


# Stream Topic details
ORDER_KAFKA_TOPIC = "food_order_details"
ORDER_LIMIT = 30

# Producer configuration
# See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
conf = {
    "bootstrap.servers": "localhost:9092",
    #'compression.type': 'gzip',
}

# Create Producer instance, as **kwargs
producer = Producer(**conf)

print("Start generating orders")
print(f"Kafka Producer config => Topic: {ORDER_KAFKA_TOPIC}")

for i in range(1, ORDER_LIMIT):

    # generate order -> message
    order_data = get_order(restaurants_data)
    # print(order_data)
    # serliazise data
    msg = json.dumps(order_data).encode("utf-8")
    # produce/send message
    print(f"Order: {order_data['_order_number']}")
    producer.produce(ORDER_KAFKA_TOPIC, msg, on_delivery=delivery_report)
    producer.flush()

    # Generate a random delay between 0.5 and 2 seconds
    delay = random.uniform(0.5, 5.0)
    # Sleep for the random delay
    time.sleep(delay)
