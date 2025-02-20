import logging
import typing
from openai import OpenAI
from backend.core.populate_config import OPENAI_CONFIG
from backend.utils.token_utils import count_tokens, chunk_text

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        logger.info("Initialized EmbeddingGenerator with OpenAI client")

    def generate_embedding(self, text: str) -> typing.List[float]:
        """
        Generates an embedding for provided text using OpenAI's text-embedding-ada-002 model.
        Handles chunking if the text exceeds the token limit.
        :param text: input text
        :return: embedding
        """
        token_count = count_tokens(text)
        return (
            self._call_embedding_api(text)
            if token_count <= OPENAI_CONFIG["MAX_TOKENS"]
            else self._generate_chunked_embedding(text)
        )

    def _generate_chunked_embedding(self, text: str) -> typing.List[float]:
        """
        Generates and aggregates embeddings for chunked text.
        :param text: input text
        :return: aggregated embedding
        """
        chunks = chunk_text(text)
        logger.info(f"Text chunked into {len(chunks)} parts.")
        embeddings = [self._call_embedding_api(chunk) for chunk in chunks]
        return self._aggregate_embeddings(embeddings)

    @staticmethod
    def _aggregate_embeddings(embeddings: typing.List[typing.List[float]]) -> typing.List[float]:
        """
        Aggregates multiple embeddings into a single vector by averaging
        :param embeddings: list of embeddings
        :return: aggregated embedding
        """
        logging.info("Aggregating embeddings using mean pooling.")
        try:
            return [sum(x) / len(embeddings) for x in zip(*embeddings)]
        except Exception as e:
            logging.error(f"Failed to aggregate embeddings: {e}")
            raise

    def _call_embedding_api(self, text: str) -> typing.List[float]:
        try:
            response = self.client.embeddings.create(
                input=text,
                model=OPENAI_CONFIG["EMBEDDING_MODEL"],
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error generating single embedding: {e}")
            raise