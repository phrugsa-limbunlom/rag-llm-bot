import logging
import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class VectorStoreService:

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def load_vector_store(self, urls):
        # embedding
        logger.info("Creating Embedding")
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        logger.info("Finish creating Embedding")

        vector_retrievers = []
        for url in urls:
            domain = url.replace("https://www.", "").split('.')[0]

            loader = WebBaseLoader([url])
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = text_splitter.split_documents(documents)

            current_dir = os.path.dirname(os.path.abspath(__file__))

            persistent_directory = os.path.join(current_dir, "db", f"chroma_db_{domain}")

            if not os.path.exists(persistent_directory):
                logger.info(f"Creating vector store : {persistent_directory}")
                Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
                logger.info(f"Finish creating vector store : {persistent_directory}")
            else:
                logger.info(f"Vector store : {persistent_directory} already exists")

            logger.info(f"Loading the existing vector store from {persistent_directory}")

            vector_store = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

            vector_retriever = vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 3, "score_threshold": 0.5}
            )

            vector_retrievers.append(vector_retriever)

        return vector_retrievers
