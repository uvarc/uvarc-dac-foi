import faiss
import logging
import typing
import numpy as np
from backend.core.populate_config import OPENAI_CONFIG, INDEX_PATH

logger = logging.getLogger(__name__)

class EmbeddingStorage:
    def __init__(self, database_driver: "DatabaseDriver"):
        self.database_driver = database_driver
        self.index = None # lazy loading

    def _load_index(self):
        if self.index is None:
            try:
                self.index = faiss.read_index(INDEX_PATH)
                logger.info("FAISS index loaded successfully.")
            except Exception:
                logger.warning("No FAISS index found; creating a new one.")
                self.index = faiss.IndexFlatL2(OPENAI_CONFIG["EMBEDDING_DIMENSIONS"])

    def save_index(self):
        """
        Save the FAISS index to a file
        """
        self._load_index()
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
        self._load_index()
        logging.info(f"Adding embedding for faculty: {faculty_name}.")
        try:
            vector = np.array([embedding], dtype=np.float32)
            self.index.add(vector)
            self.save_index()
            return self.index.ntotal - 1
        except Exception as e:
            logging.error(f"Error adding embedding: {e}")
            raise

    def search_similar_embeddings(self,
                                  query_embedding: typing.List[float] = None,
                                  top_k: int = None,
                                  school: str = None,
                                  department: str = None,
                                  activity_code: str = None,
                                  agency_ic_admin: str = None,
                                  has_funding: bool = None) -> typing.List[int]:
        """
        Search the FAISS index for most similar embeddings
        :param query_embedding: embedding generated from user input
        :param top_k: number of similar embeddings to return
        :param school: school name
        :param department: department name
        :param activity_code: activity code
        :param agency_ic_admin: agency ic admin
        :param has_funding: has funding
        :return: list of indexes
        """
        self._load_index()
        logger.info(f"Performing FAISS search with top_k={top_k}.")

        try:
            query_vector = np.expand_dims(np.array(query_embedding, dtype=np.float32), axis=0)

            if self.are_search_parameters_empty(school, department, activity_code, agency_ic_admin, has_funding):
                return self._search_full_index(query_vector, top_k)

            return self.search_with_parameters(
                    query_vector=query_vector,
                    top_k=top_k,
                    school=school,
                    department=department,
                    activity_code=activity_code,
                    agency_ic_admin=agency_ic_admin,
                    has_funding=has_funding
            )

        except Exception as e:
            logging.error(f"Error during search: {e}")
            raise

    def _search_full_index(self,
                           query_vector: np.ndarray = None,
                           top_k: int = None) -> typing.List[int]:
        _, indices = self.index.search(query_vector, top_k)
        return indices.flatten().tolist()

    def search_with_parameters(self,
                               query_vector: np.ndarray,
                               top_k: int,
                               school: str = None,
                               department: str = None,
                               activity_code: str = None,
                               agency_ic_admin: str = None,
                               has_funding: bool = None) -> typing.List[int]:
        """
        Perform a filtered FAISS search based on metadata constraints
        """
        filtered_eids = self._get_filtered_eids(
            school=school,
            department=department,
            activity_code=activity_code,
            agency_ic_admin=agency_ic_admin,
            has_funding=has_funding
        )
        valid_eids = [eid for eid in filtered_eids if eid < self.index.ntotal]

        if not valid_eids:
            logging.warning("No matching embeddings found after filtering.")
            return []

        subset_vectors = np.array(self.index.reconstruct_batch(valid_eids), dtype=np.float32)

        distances = np.linalg.norm(subset_vectors - query_vector, axis=1) ** 2
        top_k_indices = np.argsort(distances)[:min(top_k, len(subset_vectors))]

        return [valid_eids[idx] for idx in top_k_indices]

    def _get_filtered_eids(self,
                           school: str = None,
                           department: str = None,
                           activity_code: str = None,
                           agency_ic_admin: str = None,
                           has_funding: bool = None) -> typing.List[int]:
        """
        Get embedding ids for faculty with matching metadata
        :param school: school name
        :param department: department name
        :param activity_code: activity code
        :param agency_ic_admin: agency ic admin
        :param has_funding: faculty has funding
        """
        """Retrieve filtered embedding IDs from the database"""
        return self.database_driver.get_embedding_ids_by_search_parameters(
            school=school,
            department=department,
            activity_code=activity_code,
            agency_ic_admin=agency_ic_admin,
            has_funding=has_funding
        )

    def search_exact_words(self, query: str, top_k: int, school: str = None,
                           department: str = None, activity_code: str = None,
                           agency_ic_admin: str = None, has_funding: bool = None) -> typing.List[int]:
        """
        Search for exact words in faculty profiles
        :param query: exact words to search
        :param top_k: number of results to return
        :param school: school name
        :param department: department name
        :param activity_code: activity code
        :param agency_ic_admin: agency ic admin name
        :param has_funding: faculty has funding
        :return: List of faculty EIDs
        """
        return self.database_driver.search_exact_words(
            query=query,
            top_k=top_k,
            school=school,
            department=department,
            activity_code=activity_code,
            agency_ic_admin=agency_ic_admin,
            has_funding=has_funding
        )

    @staticmethod
    def are_search_parameters_empty(*parameters) -> bool:
        """Check if all search parameters are empty"""
        return not any(parameters)
