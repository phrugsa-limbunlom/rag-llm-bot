import logging
import json
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from kafka import KafkaConsumer, KafkaProducer
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service.ChatbotService import ChatbotService
from data.ChatMessage import ChatMessage

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
CHAT_TOPIC = 'chatbot_messages'
RESPONSE_TOPIC = 'chatbot_responses'


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Initializing Chatbot Service...")
#     service = ChatbotService()
#     service.initialize_service()
#
#     print("Initializing Kafka producer and consumer...")
#     producer = AIOKafkaProducer(
#         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#         value_serializer=lambda v: json.dumps(v).encode('utf-8')
#     )
#     await producer.start()
#
#     consumer = AIOKafkaConsumer(
#         RESPONSE_TOPIC,
#         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#         group_id='chatbot_response_group',
#         auto_offset_reset='earliest',
#         value_deserializer=lambda x: json.loads(x.decode('utf-8'))
#     )
#
#     await consumer.start()
#
#     # make producer and consumer available in the app state
#     app.state.producer = producer
#     app.state.consumer = consumer
#
#     yield  # mark the point where the app runs
#
#     # shutdown
#     print("Closing Kafka producer and consumer...")
#     producer.close()
#     consumer.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = None
    consumer = None
    try:
        print("Initializing Chatbot Service...")
        service = ChatbotService()
        service.initialize_service()

        print("Initializing Kafka producer and consumer...")
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
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        await consumer.start()

        # Store in app state
        app.state.producer = producer
        app.state.consumer = consumer

        yield  # App runs here

    finally:
        print("Closing Kafka producer and consumer...")
        # Proper async cleanup
        if producer:
            await producer.stop()
        if consumer:
            await consumer.stop()

app = FastAPI(lifespan=lifespan)

# allow all origins (for development purposes)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat")
async def process_chat_message(chat_message: ChatMessage, request: Request):
    logger.info(f"Message: {chat_message.message}")

    producer = request.app.state.producer
    consumer = request.app.state.consumer

    # produce message to Kafka
    await producer.send_and_wait(CHAT_TOPIC, {
        'message': chat_message.message,
        'timestamp': str(datetime.now())
    })

    # producer.send(CHAT_TOPIC, {
    #     'message': chat_message.message,
    #     'timestamp': str(datetime.now())
    # })
    # producer.flush()

    for msg in consumer:
        return {"response": msg.value['response']}


@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket, request: Request):
    producer = request.app.state.producer
    consumer = request.app.state.consumer

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()

            # produce message to Kafka
            producer.send(CHAT_TOPIC, {
                'message': data,
                'timestamp': str(datetime.now())
            })
            producer.flush()

            # listen for responses
            for message in consumer:
                await websocket.send_text(message.value['response'])
                break
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()