import argparse
from os import environ as env
from pathlib import Path

import jj
from jj.mock import Mock

from ._load_module import load_module


def run() -> None:
    """
    Run the remote HTTP mock server.

    This function sets up an argument parser to configure the server's host, port,
    and optionally load custom matcher modules. It retrieves values from the
    environment or provided arguments and starts the `jj` mock server.
    """
    parser = argparse.ArgumentParser("jj", description="Remote HTTP Mock Server")
    parser.add_argument(
        "-H", "--host", type=str, default=None,
        help="Host address to serve on (default: None)"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=env.get("PORT", 8080),
        help="Port number to serve on (default: 8080)"
    )
    parser.add_argument(
        "--use-matchers", type=str, nargs="+",
        help="Path(s) to custom matcher module(s), separated by space."
    )
    args = parser.parse_args()

    if args.use_matchers:
        for module_path_str in args.use_matchers:
            module_path = Path(module_path_str)
            load_module(module_path)

    jj.serve(Mock(), host=args.host, port=args.port)
