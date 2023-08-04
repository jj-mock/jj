from os import environ as env

import jj
from jj.mock import Mock

jj.serve(Mock(), port=int(env.get("PORT", 8080)))
