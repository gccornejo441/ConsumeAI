import importlib.util
import sys
from typing import Optional, Dict


ROUTING_MAPPING: Dict[str, str] = {
    'run': 'main.run',
}

def cli_main(routing_mapping: Optional[Dict[str, str]] = None) -> None:

    route_mapping = routing_mapping or ROUTING_MAPPING
    argv = sys.argv[1:]
    print(f"Arguments: {argv}")
    method_name = argv[0].replace('_', '-')
    argv = argv[1:]

    file_path = importlib.util.find_spec(route_mapping[method_name]).origin
    python_cmd = sys.executable
    args = [python_cmd, file_path, *argv]


def run():
    print("Running the main function...")

if __name__ == "__main__":
    cli_main()

