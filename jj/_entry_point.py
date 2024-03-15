import argparse

import jj
from jj.mock import Mock


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str, default=None)
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    jj.serve(Mock(), host=args.host, port=args.port)
