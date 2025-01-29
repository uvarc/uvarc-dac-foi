import faiss
import logging
import typing
import numpy as np
from app.core.script_config import OPENAI_CONFIG, INDEX_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingStorage:
    def __init__(self):
        logging.info(f"Loading FAISS index from {INDEX_PATH}.")
        try:
            self.index = faiss.read_index(INDEX_PATH)
            logging.info("FAISS index loaded successfully.")
        except Exception:
            logging.warning("No existing index found. Starting with an empty index.")
            self.index = faiss.IndexFlatL2(OPENAI_CONFIG["EMBEDDING_DIMENSIONS"])
        logging.info(f"Initialized EmbeddingStorage with index path: {INDEX_PATH}")

    def save_index(self):
        """
        Save the FAISS index to a file
        """
        logging.info(f"Saving FAISS index to {INDEX_PATH}.")
        try:
            faiss.write_index(self.index, INDEX_PATH)
            logging.info("FAISS index saved successfully.")
        except Exception as e:
            logging.error(f"Error saving FAISS index: {INDEX_PATH}")
            raise

    def add_embedding(self, faculty_name: str, embedding: typing.List[float]) -> int:
        """
        Add an embedding to the FAISS index
        :param faculty_name: name of the faculty
        :param embedding: faculty embedding
        :return: index of the added embedding
        """
        logging.info(f"Adding embedding for faculty: {faculty_name}.")
        try:
            vector = np.array([embedding], dtype=np.float32)
            self.index.add(vector)
            self.save_index()
            current_index = self.index.ntotal - 1
            return current_index
        except Exception as e:
            logging.error(f"Error adding embedding: {e}")
            raise

    def search(self, query_embedding: typing.List[float], top_k: int = 10) -> typing.List[int]:
        """
        Search the FAISS index for most similar embeddings
        :param query_embedding: embedding generated from user input
        :param top_k: number of similar embeddings to return
        :return: list of indexes
        """
        logging.info(f"Searching FAISS index for {top_k} most similar embeddings.")
        try:
            logging.info(f"Total embeddings in the index: {self.index.ntotal}")

            logging.info(f"Query embedding dimension: {len(query_embedding)}")
            logging.info(f"FAISS index dimension: {self.index.d}")

            query_vector = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_vector, top_k)
            logging.info(f"Search completed. Found {len(indices.flatten())} results.")
            return indices.flatten().tolist()
        except Exception as e:
            logging.error(f"Error during search: {e}")
        raise