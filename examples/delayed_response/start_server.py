import jj
from jj.mock import Mock

from delayed_response import DelayedResponse  # noqa

if __name__ == "__main__":
    jj.serve(Mock(), port=8080)
