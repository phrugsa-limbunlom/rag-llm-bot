import os
from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer
import json

from service.ChatbotService import ChatbotService

class ChatbotProcessor:
    def __init__(self):
        self.kafka_servers = ['localhost:9092']
        self.input_topic = 'chatbot_messages'
        self.output_topic = 'chatbot_responses'

    def create_kafka_consumer(self):
        return KafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.kafka_servers,
            group_id='chatbot_processor_group',
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def create_kafka_producer(self):
        return KafkaProducer(
            bootstrap_servers=self.kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def process_messages(self):
        consumer = self.create_kafka_consumer()
        producer = self.create_kafka_producer()

        for message in consumer:
            try:
                user_message = message.value['message']

                response = service.generate_answer(query=user_message)

                bot_response = response.choices[0].message.content

                # Produce response to Kafka
                producer.send(self.output_topic, {
                    'response': bot_response,
                    'timestamp': str(datetime.now())
                })
                producer.flush()

            except Exception as e:
                print(f"Processing error: {e}")


if __name__ == "__main__":
    processor = ChatbotProcessor()
    processor.process_messages()