import logging
import typing
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, client: OpenAI):
        self.client = client
        logging.info("Initialized EmbeddingGenerator with OpenAI client")

    def generate_embedding(self, text: str) -> typing.List[float]:
        """
        Generates an embedding for provided text using OpenAI's text-embedding-ada-002 model
        :param text: input text
        :return: embedding
        """
        logging.info(f"Generating embedding for text: {text}")
        try:
            response = self.client.embeddings.create(input=text,
            model="text-embedding-ada-002")
            logging.info("Successfully generated embedding.")
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error generating embedding: {e}")
            raise