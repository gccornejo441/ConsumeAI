
import argparse


def initialize_cli() -> dict:
    parser = argparse.ArgumentParser(
        prog="ConsumeAI",
        description="A tool to consume AI services with caching and logging.",
        epilog="Developed by dev tools")

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--dir",
        help="Path to directory to crawl for files.",
        type=str,
        default=None
    )

    parser.add_argument(
        "--prompt",
        "-p",
        help="Prompt to send to the LLM.",
        type=str,
        default=None
    )

    args = parser.parse_args()

    user_inputs = {
        "local_dir": args.dir,
        "prompt": args.prompt
    }

    return user_inputs
