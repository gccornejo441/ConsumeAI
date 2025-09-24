import argparse
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(
    log_directory, f"llm_calls_{datetime.now().strftime('%Y-%m-%d')}.log")

logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False

file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(
logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)


def main():
    logger.info("Starting the LLM interaction script.")
    



if __name__ == "__main__":
    main()
