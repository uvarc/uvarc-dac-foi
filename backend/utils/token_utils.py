import tiktoken
from backend.core.script_config import OPENAI_CONFIG

def count_tokens(text: str) -> int:
    """
    Calculate the number of tokens in the text for embedding model.
    :param text: input text
    :return: token count
    """
    tokenizer = tiktoken.encoding_for_model(OPENAI_CONFIG["EMBEDDING_MODEL"])
    return len(tokenizer.encode(text))
