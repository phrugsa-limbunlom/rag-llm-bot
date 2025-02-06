import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatbotProcessor:
    def __init__(self, service, producer, consumer, server, input_topic, output_topic):
        self.service = service
        self.producer = producer
        self.consumer = consumer
        self.kafka_servers = server
        self.input_topic = input_topic
        self.output_topic = output_topic

    async def process_messages(self, message):
        consumer = self.consumer
        producer = self.producer

        logger.info(f"Producer: {producer}, Consumer: {consumer}")

        uid = str(uuid.uuid4())
        logger.info(f"Generated UID for message: {uid}")

        # produce the input message to Kafka
        await producer.send_and_wait(self.input_topic, {
            'uid': uid,
            'message': message,
            'timestamp': str(datetime.now())
        })

        # process the message using ChatbotService
        # answer = self.service.generate_answer(query=message)

        # process the message using Agent
        answer = self.service.generate_answer_with_agent(query=message)

        # produce the generated answer to the output topic
        await producer.send_and_wait(self.output_topic, {
            'uid': uid,
            'response': answer,
            'timestamp': str(datetime.now())
        })

        # consume the response from the output topic
        msg = await consumer.getone()

        if msg.value['uid'] != uid:
            logger.error(f"UID mismatch: expected {uid}, got {msg.value['uid']}")
            raise ValueError("UID mismatch in Kafka message")

        return {"value": msg.value['response'],
                "uid": msg.value['uid']}
