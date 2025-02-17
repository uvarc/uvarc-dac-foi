import faiss
import logging
import typing
import numpy as np
from backend.core.script_config import OPENAI_CONFIG, INDEX_PATH

logger = logging.getLogger(__name__)

class EmbeddingStorage:
    def __init__(self, database_driver: "DatabaseDriver"):
        self.database_driver = database_driver
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
        :return: list of indexes
        """
        logging.info(f"Searching FAISS index for {top_k} most similar embeddings.")

        logging.debug(f"Total embeddings in the index: {self.index.ntotal}")
        logging.debug(f"Query embedding dimension: {len(query_embedding)}")
        logging.debug(f"FAISS index dimension: {self.index.d}")

        try:
            query_vector = np.array([query_embedding], dtype=np.float32)

            if self.are_search_parameters_empty(
                    school=school,
                    department=department,
                    activity_code=activity_code,
                    agency_ic_admin=agency_ic_admin,
                    has_funding=has_funding
            ):
                logging.info("No filters detected, search entire FAISS index.")
                indices = self.search_no_parameters(
                    query_vector=query_vector,
                    top_k=top_k
                )
            else:
                logging.info("Filters detected, reducing index search space.")
                indices = self.search_with_parameters(
                    query_vector=query_vector,
                    top_k=top_k,
                    school=school,
                    department=department,
                    activity_code=activity_code,
                    agency_ic_admin=agency_ic_admin,
                    has_funding=has_funding
                )

            logging.info(f"Search completed. Found {len(indices)} results.")
            return indices

        except Exception as e:
            logging.error(f"Error during search: {e}")
            raise

    def search_no_parameters(self,
                             query_vector: np.ndarray = None,
                             top_k: int = None) -> typing.List[int]:
        _, indices = self.index.search(query_vector, top_k)
        return indices.flatten().tolist()

    def search_with_parameters(self,
                               query_vector: np.ndarray = None,
                               top_k: int = None,
                               school: str = None,
                               department: str = None,
                               activity_code: str = None,
                               agency_ic_admin: str = None,
                               has_funding: bool = None) -> typing.List[int]:

        filtered_eids = self.get_filtered_eids(
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
        query_vector = query_vector.reshape(1, -1)

        distances = np.linalg.norm(subset_vectors - query_vector, axis=1) ** 2
        top_k_indices = np.argsort(distances)[:min(top_k, len(subset_vectors))]
        return [valid_eids[idx] for idx in top_k_indices]

        ### NOTE: DEPRECATED LOGIC ###
        # subset_index = faiss.IndexIDMap(faiss.IndexFlatL2(self.index.d))
        # subset_vectors = np.array(self.index.reconstruct_batch(filtered_eids), dtype=np.float32)
        # subset_index.add_with_ids(subset_vectors, np.array(filtered_eids, dtype=np.int64))
        # _, indices = subset_index.search(query_vector, top_k)
        # return indices.flatten().tolist()

    def get_filtered_eids(self,
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
        """
        logging.info(f"Applying filters to FAISS index.")
        return self.database_driver.get_embedding_ids_by_filters(
            school=school,
            department=department,
            activity_code=activity_code,
            agency_ic_admin=agency_ic_admin,
            has_funding=has_funding
        )

    @staticmethod
    def are_search_parameters_empty(**parameters) -> bool:
        """
        Check if search parameters are empty
        """
        return not any(parameters.values())
