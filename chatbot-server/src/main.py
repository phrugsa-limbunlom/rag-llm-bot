import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from http.client import responses

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service.ChatbotService import ChatbotService
from data.ChatMessage import ChatMessage
from processor.ChatbotProcessor import ChatbotProcessor

# configure logging
logger = logging.getLogger(__name__)

# kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = ['kafka:9092']
CHAT_TOPIC = 'chatbot_messages'
RESPONSE_TOPIC = 'chatbot_responses'


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = None
    consumer = None

    try:
        logger.info("Initializing Chatbot Service...")
        service = ChatbotService()
        service.initialize_service()

        logger.info("Initializing Kafka producer and consumer...")

        # Initialize producer
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await producer.start()

        # Initialize consumer
        consumer = AIOKafkaConsumer(
            RESPONSE_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id='chatbot_response_group',
            auto_offset_reset='latest',  # Changed from 'earliest' to 'latest'
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        await consumer.start()

        # Ensure consumer is properly subscribed
        #await consumer.seek_to_end()  # Move to the end of the topic
        #await consumer.subscribe([RESPONSE_TOPIC])

        # Store in app state
        app.state.producer = producer
        app.state.consumer = consumer
        app.state.service = service

        logger.info("Kafka producer and consumer initialized successfully.")

        yield  # App runs here

    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise
    finally:
        logger.info("Closing Kafka producer and consumer...")
        # Proper async cleanup with checks
        if producer:
            try:
                await producer.stop()
            except Exception as e:
                logger.error(f"Error stopping producer: {e}")

        if consumer:
            try:
                await consumer.unsubscribe()
                await consumer.stop()
            except Exception as e:
                logger.error(f"Error stopping consumer: {e}")

        logger.info("Kafka producer and consumer closed.")


app = FastAPI(lifespan=lifespan)

# enable cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow only frontend
    allow_credentials=True,
    allow_methods=["POST"],  # Define methods
    allow_headers=["*"],
)


@app.post("/api/chat")
async def process_chat_message(chat_message: ChatMessage, request: Request):
    logger.info(f"Message: {chat_message.message}")

    producer = request.app.state.producer
    consumer = request.app.state.consumer
    service = request.app.state.service

    if not producer or not consumer:
        raise HTTPException(status_code=500, detail="Kafka producer or consumer is not initialized.")

    processor = ChatbotProcessor(service=service,
                                 producer=producer,
                                 consumer=consumer,
                                 server=KAFKA_BOOTSTRAP_SERVERS,
                                 input_topic=CHAT_TOPIC,
                                 output_topic=RESPONSE_TOPIC)

    try:
        logger.info("Waiting for Kafka response...")
        response = await processor.process_messages(chat_message.message)
        logger.info(f"Kafka response received: {response}")
        return response
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))