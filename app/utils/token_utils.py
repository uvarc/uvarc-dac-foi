import tiktoken

def count_tokens(text: str) -> int:
    """
    Calculate the number of tokens in the text for embedding model.
    :param text: input text
    :return: token count
    """
    tokenizer = tiktoken.encoding_for_model(OPENAI_CONFIG["EMBEDDING_MODEL"])
    return len(tokenizer.encode(text))
