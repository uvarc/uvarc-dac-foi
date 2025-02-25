import tiktoken
import typing
from backend.core.populate_config import OPENAI_CONFIG

def count_tokens(text: str) -> int:
    """
    Calculate the number of tokens in the text for embedding model.
    :param text: input text
    :return: token count
    """
    tokenizer = tiktoken.encoding_for_model(OPENAI_CONFIG["EMBEDDING_MODEL"])
    return len(tokenizer.encode(text))

def chunk_text(text: str) -> typing.List[str]:
    """
    Split text into chunks that fit within the model's token limit.
    :param text: input text
    :return: list of text chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        word_length = count_tokens(word)
        if current_length + word_length > OPENAI_CONFIG["MAX_TOKENS"]:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += word_length + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks