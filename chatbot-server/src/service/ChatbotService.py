import logging
import os

import requests.exceptions
from dotenv import load_dotenv, find_dotenv
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from text.PromptMessage import PromptMessage
from text.WebURLs import WebURLs
from util.util import Util
from service.VectorStoreService import VectorStoreService

logger = logging.getLogger(__name__)


class ChatbotService:

    def __init__(self):
        self.template = None
        self.client = None
        self.llm_model = None
        self.retriever = None

    def query_groq_api(self, client, prompt, model):
        """Query the Groq API directly and return the response."""
        try:
            if not isinstance(prompt, str):
                raise ValueError(f"Prompt must be a string, but got {type(prompt)}")

            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=0.5,
                max_tokens=1024,
                stop=None,
                stream=False,
            )

            return response.choices[0].message.content

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error occurred: {e.response.status_code} - {e.response.text}")
            return "Sorry, I encountered an error while processing your request."
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return "Sorry, I encountered an unexpected error."

    def is_query_relevant(self, query):
        """Check if the query is relevant to the prompt template using the model."""
        relevance_prompt = (
            f"This is prompt template : \"{self.template}\". Evaluate whether the following query is relevant to the prompt template: \"{query}\". Respond only one word 'relevant' or 'irrelevant'.")

        relevance_response = self.query_groq_api(client=self.client, prompt=relevance_prompt, model=self.llm_model)

        return relevance_response == "relevant"

    def generate_answer(self, query):
        """Generate an answer using RAG and the Groq API."""
        if not self.is_query_relevant(query):
            return PromptMessage.Default_Message

        results = self.retriever.invoke(query)

        context = " ".join([doc.page_content for doc in results])
        prompt = self.template.invoke({"context": context, "query": query}).to_string()

        answer = self.query_groq_api(client=self.client, prompt=prompt, model=self.llm_model)

        return answer

    def initialize_service(self):
        logger.info("Initialize the service")

        load_dotenv(find_dotenv())

        self.template = ChatPromptTemplate.from_messages(
            [PromptMessage.System_Message, PromptMessage.Human_Message, PromptMessage.AI_Message])

        # groq API client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # model
        file_path = '../model.yaml'
        model_list = Util.load_yaml(file_path)

        self.llm_model = model_list["LLM"]
        embedding_model = model_list["EMBEDDING"]

        # vector store
        urls = [WebURLs.Amazon, WebURLs.Ebay]
        self.retriever = VectorStoreService(embedding_model=embedding_model).load_vector_store(urls=urls)[0]
