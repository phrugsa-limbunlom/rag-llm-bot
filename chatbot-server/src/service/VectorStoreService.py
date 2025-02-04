import logging

from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class VectorStoreService:

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def create_vector_store(self, url, persistent_directory):

        file_path = "C:/Users/asus/PycharmProjects/PickSmart/chatbot-server/src/document/product_information.txt"

        loader = TextLoader(file_path)
        documents = loader.load()

        # embedding
        logger.info("Creating Embedding")
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        logger.info("Finish creating Embedding")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)

        logger.info(f"Creating vector store : {persistent_directory}")
        Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
        logger.info(f"Finish creating vector store from Amazon : {persistent_directory}")


    def load_vector_store(self,persistent_directory):
        # load the existing vector store
        logger.info(f"Loading the existing vector store from {persistent_directory}")
        vector_store = Chroma(persist_directory=persistent_directory, embedding_function=self.embedding_model)

        vector_retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 3, "score_threshold": 0.4}
        )

        return vector_retriever