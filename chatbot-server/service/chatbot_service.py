import os

import requests.exceptions
from dotenv import load_dotenv
from groq import Groq
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from util.prompt_message import PromptMessage
from util.util import Util


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
            print(f"HTTP Error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    # rag-based QA chain
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

        # embedding
        print("Creating Embedding")
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        print("Finish creating Embedding")

        if not os.path.exists(persistent_directory):
            print("The vector store does not exist. Initializing vector store...")

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The {file_path} does not exist")

            # load document
            loader = TextLoader(file_path)
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = text_splitter.split_documents(documents)

            print(f"Number of chunks: {len(docs)}")
            print(f"Sample chunk:\n{docs[0].page_content}\n")

            # create the vector store and save it to directory
            print("Creating vector store")
            Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
            print("Finish creating vector store")

        else:
            print("The vector store already exists. No need to Initialize")

        # load the existing vector store
        print("Loading the existing vector store")
        vector_store = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

        vector_retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 3, "score_threshold": 0.1}
        )

        return vector_retriever

    def initialize_service(self):
        print("Initialize the service")

        load_dotenv('./.env')

        self.template = ChatPromptTemplate.from_messages(
            [PromptMessage.System_Message, PromptMessage.Human_Message, PromptMessage.AI_Message])

        # groq API client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # model
        model_list = Util.load_yaml('./model.yaml')

        self.llm_model = model_list["LLM"]
        embedding_model = model_list["EMBEDDING"]

        # vector store
        self.retriever = self.load_vector_store(embedding_model)


def chatbot():
    print("Welcome to AI Chatbot. Type 'exit' to quit.")

    service = ChatbotService()
    service.initialize_service()

    while True:
        query = input("\nUser: ")
        if query.lower() == 'exit':
            break

        result = service.generate_answer(query=query)
        print("\nBot:", result)
