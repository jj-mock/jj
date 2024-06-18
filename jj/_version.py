import aiohttp

version = "2.10.3"
server_version = "jj/{} via aiohttp/{}".format(version, aiohttp.__version__)


__all__ = ("version", "server_version")
