"""Top-level package for Cfg4Py."""
from cfg4py.core import (
    RedisConfigFetcher,
    RemoteConfigFetcher,
    _cfg_obj,
    config_remote_fetcher,
    config_server_role,
    enable_logging,
    envar,
    get_config_dir,
    init,
    update_config,
)

__author__ = """Aaron Yang"""
__email__ = "code@jieyu.ai"
__version__ = "0.9.3"


def get_instance():
    return _cfg_obj


__all__ = [
    "RemoteConfigFetcher",
    "enable_logging",
    "config_remote_fetcher",
    "init",
    "update_config",
    "RedisConfigFetcher",
    "config_server_role",
    "envar",
    "get_instance",
    "get_config_dir",
]
