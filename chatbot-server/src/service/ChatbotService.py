import os
import requests.exceptions
from dotenv import load_dotenv, find_dotenv
from groq import Groq
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from prompt.PromptMessage import PromptMessage
from util.util import Util
import logging

logger = logging.getLogger(__name__)


class ChatbotService:

    def __init__(self):
        self.template = None
        self.client = None
        self.llm_model = None
        self.retriever = None

        # Groq API

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

    def generate_answer(self, query):
        """Generate an answer using RAG and the Groq API."""
        if not self.is_query_relevant(query):
            return PromptMessage.Default_Message

        results = self.retriever.invoke(query)

        context = " ".join([doc.page_content for doc in results])
        prompt = self.template.invoke({"context": context, "query": query}).to_string()

        answer = self.query_groq_api(client=self.client, prompt=prompt, model=self.llm_model)

        return answer

    def is_query_relevant(self, query):
        """Check if the query is relevant to the prompt template using the model."""
        relevance_prompt = (
            f"This is prompt template : \"{self.template}\". Evaluate whether the following query is relevant to the prompt template: \"{query}\". Respond only one word 'relevant' or 'irrelevant'.")

        relevance_response = self.query_groq_api(client=self.client, prompt=relevance_prompt, model=self.llm_model)

        return relevance_response == "relevant"

    def load_vector_store(self, embedding_model):
        # create vector store if no vector store exists
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "../", "document", "product_information.txt")

        persistent_directory = os.path.join(current_dir, "../", "db", "chroma_db")

        # amazon
        persistent_directory_amazon = os.path.join(current_dir, "../", "db", "chroma_db_amazon")

        urls = ["https://www.amazon.co.uk/"]

        loader = WebBaseLoader(urls)
        documents = loader.load()  # Use  load if available

        # embedding
        logger.info("Creating Embedding")
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        logger.info("Finish creating Embedding")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)
        logger.info("Creating vector store from Amazon")
        Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory_amazon)
        logger.info("Finish creating vector store from Amazon")

        if not os.path.exists(persistent_directory):
            logger.info("The vector store does not exist. Initializing vector store...")

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The {file_path} does not exist")

            # load document from text
            loader = TextLoader(file_path)
            documents = loader.load()  # Use  load if available

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = text_splitter.split_documents(documents)

            logger.info(f"Number of chunks: {len(docs)}")
            logger.info(f"Sample chunk:\n{docs[0].page_content}\n")

            # create the vector store and save it to directory
            logger.info("Creating vector store")
            Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
            logger.info("Finish creating vector store")

        else:
            logger.info("The vector store already exists. No need to Initialize")

        # load the existing vector store
        logger.info("Loading the existing vector store from Amazon")
        vector_store = Chroma(persist_directory=persistent_directory_amazon, embedding_function=embeddings)

        vector_retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 3, "score_threshold": 0.1}
        )

        return vector_retriever

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
        self.retriever = self.load_vector_store(embedding_model)