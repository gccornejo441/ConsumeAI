import argparse
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

from chat import chat_response
from src.cli import initialize_cli

load_dotenv()

cache_file = "llm_cache.json"

def create_log_file() -> str:
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(
        log_dir, f"llm_calls_{datetime.now().strftime('%Y-%m-%d')}.log")
    return file_path


def log_handler(file_path: str) -> logging.Logger:
    logger = logging.getLogger("llm_logger")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    )
    logger.addHandler(file_handler)
    return logger


def call_llm(
        prompt: str,
        use_cache: bool = True) -> str:
    logger = log_handler(create_log_file())

    logger.info(f"PROMPT: {prompt}")

    if use_cache:
        cache = {}
        if os.path.exists(cache_file):
            try: 
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.loads(f)
            except:
                logger.warning(f"Failed to load cache, starting with empty cache.")
        else:
            logger.info("No cache file found, starting with empty cache.")

        if prompt in cache:
            logger.info(f"Response: {cache[prompt]}")
            return cache[prompt]
    
    
    resp = chat_response(chat=[{"role": "user", "content": prompt}])
    logger.info(f"Response: {resp}")

    if use_cache:
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.loads(f)
            except:
                pass
        
        cache[prompt] = resp
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f)
        except Exception as e:
            logger.error(f"Failed to write cache: {e}")
        
    return resp


def main():
    print("Calling LLM...")
    user_inputs = initialize_cli()
    user_prompt = user_inputs.get("prompt")

    res = call_llm(user_prompt, use_cache=True)
    print(f"Response: {res}")

if __name__ == "__main__":
    main()
