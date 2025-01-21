import faiss
import logging
import typing
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingStorage:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.index = faiss.IndexFlatL2(1536)
        logging.info(f"Initialized EmbeddingStorage with index path: {self.index_path}")

    def load_index(self):
        """
        Load the FAISS index from a file
        """
        logging.info(f"Loading FAISS index from {self.index_path}.")
        try:
            self.index = faiss.read_index(self.index_path)
            logging.info("FAISS index loaded successfully.")
        except Exception:
            logging.warning("No existing index found. Starting with an empty index.")

    def save_index(self):
        """
        Save the FAISS index to a file
        """
        logging.info(f"Saving FAISS index to {self.index_path}.")
        try:
            faiss.write_index(self.index, self.index_path)
            logging.info("FAISS index saved successfully.")
        except Exception as e:
            logging.error(f"Error saving FAISS index: {e}")
            raise

    def add_embedding(self, embedding: typing.List[float]) -> int:
        """
        Add an embedding to the FAISS index
        :param embedding: faculty embedding
        :return: index of the added embedding
        """
        logging.info(f"Adding embedding...")
        try:
            vector = np.array([embedding], dtype=np.float32)
            self.index.add(vector)
            current_index = self.index.ntotal - 1
            logging.info(f"Embedding added at index: {current_index}.")
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
            query_vector = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_vector, top_k)
            logging.info(f"Search completed. Found {len(indices.flatten())} results.")
            return indices.flatten().tolist()
        except Exception as e:
            logging.error(f"Error during search: {e}")
        raise