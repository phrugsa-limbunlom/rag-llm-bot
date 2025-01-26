import os
import sys
import uuid
import logging
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

        try:

            uid = str(uuid.uuid4())
            logger.info(f"Generated UID for message: {uid}")

            # Produce the input message to Kafka
            await producer.send_and_wait(self.input_topic, {
                'uid': uid,
                'message': message,
                'timestamp': str(datetime.now())
            })

            # Process the message using ChatbotService
            answer = await self.service.generate_answer(query=message)

            # Produce the generated answer to the output topic
            await producer.send_and_wait(self.output_topic, {
                'uid': uid,
                'response': answer,
                'timestamp': str(datetime.now())
            })

            # Consume the response from the output topic
            await consumer.subscribe([self.output_topic])
            msg = await consumer.getone()

            if msg.value['uid'] != uid:
                logger.error(f"UID mismatch: expected {uid}, got {msg.value['uid']}")
                raise ValueError("UID mismatch in Kafka message")

            return {"response": msg.value['response'],
                    "uid": msg.value['uid']}

        finally:
            # Clean up the consumer and producer
            await consumer.unsubscribe()
            await consumer.stop()
            await producer.stop()
