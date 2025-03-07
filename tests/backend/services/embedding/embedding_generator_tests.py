import unittest
from unittest.mock import MagicMock, patch, call
from backend.services.embedding.embedding_generator import EmbeddingGenerator
from backend.core.populate_config import OPENAI_CONFIG
from backend.utils.token_utils import count_tokens, chunk_text

class TestEmbeddingGenerator(unittest.TestCase):
    MODULE_PATH = "backend.services.embedding.embedding_generator"

    def setUp(self):
        self.mock_openai_client = MagicMock()
        self.generator = EmbeddingGenerator(self.mock_openai_client)

    @patch(f"{MODULE_PATH}.count_tokens")
    @patch(f"{MODULE_PATH}.EmbeddingGenerator._call_embedding_api")
    def test_generate_embedding_within_token_limits(self, mock_call_api, mock_count_tokens):
        mock_count_tokens.return_value = OPENAI_CONFIG["MAX_TOKENS"] - 10
        mock_call_api.return_value = [0.1, 0.2, 0.3]

        result = self.generator.generate_embedding("test text")

        mock_call_api.assert_called_once_with("test text")
        self.assertEqual(result, [0.1, 0.2, 0.3])

    @patch(f"{MODULE_PATH}.chunk_text")
    @patch(f"{MODULE_PATH}.count_tokens")
    @patch(f"{MODULE_PATH}.EmbeddingGenerator._call_embedding_api")
    def test_generate_embedding_exceeds_token_limits(self, mock_call_api, mock_count_tokens, mock_chunk_text):
        mock_count_tokens.return_value = OPENAI_CONFIG["MAX_TOKENS"] + 10
        mock_chunk_text.return_value = ["chunk1", "chunk2"]
        mock_call_api.side_effect = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        result = self.generator.generate_embedding("long test text")

        mock_call_api.assert_has_calls([call("chunk1"), call("chunk2")])
        for i in range(len(result)):
            self.assertAlmostEqual(
                result[i],
                [0.25, 0.35, 0.45][i],
                places=2
            )

    def test_aggregate_embeddings(self):
        embeddings = [
            [1, 2, 3],
            [4, 5, 6],
        ]

        result = self.generator._aggregate_embeddings(embeddings)

        for i in range(len(result)):
            self.assertAlmostEqual(
                result[i],
                [2.5, 3.5, 4.5][i],
                places=2
            )

    @patch(f"{MODULE_PATH}.EmbeddingGenerator._call_embedding_api")
    def test_call_embedding_api_success(self, mock_call_api):
        mock_call_api.return_value = [0.1, 0.2, 0.3]
        self.mock_openai_client.embeddings.create.return_value = MagicMock(data=[{"embedding": [0.1, 0.2, 0.3]}])

        result = self.generator._call_embedding_api("test text")

        self.assertEqual(result, [0.1, 0.2, 0.3])

    def test_call_embedding_api_failure(self):
        self.mock_openai_client.embeddings.create.side_effect = Exception("API ERROR")

        with self.assertRaises(Exception) as context:
            self.generator._call_embedding_api("test text")

        self.assertEqual(str(context.exception), "API ERROR")

if __name__ == "__main__":
    unittest.main()



