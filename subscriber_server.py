"""
central_server.py

A module that provides a central server for consuming video frames from a Kafka topic, 
processing them using Google Cloud Vision API, and displaying the annotated frames.

Classes:
    CentralServer: A central server that consumes video frames from a Kafka topic, 
    processes them using Google Cloud Vision API, and displays the annotated frames.
"""

import pickle
import cv2
from confluent_kafka import Consumer, KafkaError

class CentralServer:
    """
    A central server that consumes video frames from a Kafka topic, processes them using Google Cloud Vision API,
    and displays the annotated frames.

    Parameters:
    bootstrap_servers (str): The bootstrap servers for the Kafka cluster.
    group_id (str): The group ID for the consumer.
    topic (str): The Kafka topic to subscribe to.

    Example:
    >>> central_server = CentralServer("localhost:9092", "my_group", "my_topic")
    """

    def __init__(self, bootstrap_servers, group_id, topic):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
        })
        self.topic = topic
        self.consumer.subscribe([self.topic])
        self.running = True

    def update(self, data):
        """
        Updates the central server with a new frame.

        Parameters:
        data (bytes): The serialized frame data.

        Returns:
        None
        """
        frame = pickle.loads(data)
        cv2.imshow('Central Server', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.running = False
            self.consumer.close()
            cv2.destroyAllWindows()

    def listen(self):
        """
        Listens to the Kafka topic and processes incoming frames.

        Returns:
        None
        """
        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaError(msg.error())
                else:
                    self.update(msg.value())
        except Exception as e:
            print(f"Error in listen loop: {e}")
        finally:
            self.consumer.close()
