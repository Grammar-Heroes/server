import logging

def setup_grammar_cache_logger():
    logger = logging.getLogger("grammar_cache")
    if logger.hasHandlers():
        return  # Prevent duplicate handlers

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent double logging with root/uvicorn