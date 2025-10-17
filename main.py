import argparse
import logging
import os
import sys
from rich.console import Console
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import config

def initiate():
    if not os.path.exists("logs/"):
        print("Creating logs directory")
        os.makedirs("logs/")
    logging.basicConfig(
        filename=config.LOG_PATH,
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="Blackbird",
        description="A social media scraper",
    )
    parser.add_argument(
        "-u",
        "--username",
        nargs="*",
        type=str,
        help="One or more usernames to search"
    )

    args = parser.parse_args()

    config.username_list = args.username
    config.console = Console()

if __name__ == "__main__":
    initiate()

    config.console.print("Blackbird is running...")
