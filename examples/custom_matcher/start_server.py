import jj
from jj.mock import Mock

from body_matcher import BodyKeyMatcher  # noqa

if __name__ == "__main__":
    jj.serve(Mock(), port=8080)
