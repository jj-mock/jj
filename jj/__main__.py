import argparse

import jj
from jj.mock import Mock

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default=None)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    jj.serve(Mock(), host=args.host, port=args.port)
